"""
3D Pose Estimation Module for Swing Analysis
Uses MediaPipe for real-time 3D pose detection with triangulation
Replaces OpenPose 2D approach with full 3D biomechanical analysis
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import os
from scipy.spatial.transform import Rotation as R
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.offline as offline
from typing import List, Dict, Tuple, Optional

class Pose3DEstimator:
    def __init__(self):
        """Initialize MediaPipe 3D pose estimation."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Higher accuracy
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 3D pose landmarks mapping (33 landmarks in MediaPipe)
        self.landmark_names = [
            'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
            'right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
            'left_index', 'right_index', 'left_thumb', 'right_thumb',
            'left_hip', 'right_hip', 'left_knee', 'right_knee',
            'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
            'left_foot_index', 'right_foot_index'
        ]
        
        # Key joints for swing analysis
        self.swing_joints = {
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28
        }

    def process_video(self,
                     video_path: str,
                     output_dir: str,
                     frame_skip: int = 1,
                     max_frames: Optional[int] = None,
                     apply_smoothing: bool = True,
                     progress_callback: Optional[callable] = None) -> str:
        """
        Process video to extract 3D pose sequences with enhanced error handling and performance.
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save 3D pose data
            frame_skip: Process every nth frame (1 = every frame, 2 = every other frame)
            max_frames: Maximum number of frames to process (None = all frames)
            apply_smoothing: Whether to apply temporal smoothing to pose data
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Path to saved 3D pose data file
            
        Raises:
            ValueError: If video file cannot be opened or is invalid
            FileNotFoundError: If video file doesn't exist
            PermissionError: If output directory cannot be created/written to
            RuntimeError: If pose processing fails critically
        """
        # Validate inputs
        self._validate_video_inputs(video_path, output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize video capture with proper resource management
        cap = None
        try:
            cap = self._initialize_video_capture(video_path)
            video_info = self._get_video_info(cap)
            
            # Process video frames
            pose_sequence = self._process_video_frames(
                cap,
                video_info,
                frame_skip,
                max_frames,
                progress_callback
            )
            
            # Validate we have sufficient pose data
            if not pose_sequence:
                raise RuntimeError("No valid pose data extracted from video")
            
            # Apply temporal smoothing if requested
            if apply_smoothing and len(pose_sequence) > 1:
                pose_sequence = self._apply_temporal_smoothing(pose_sequence)
            
            # Save results
            output_file = self._save_pose_data(
                pose_sequence,
                output_dir,
                video_info
            )
            
            return output_file
            
        except Exception as e:
            # Log error and re-raise with context
            error_msg = f"Failed to process video '{video_path}': {str(e)}"
            raise RuntimeError(error_msg) from e
        finally:
            # Ensure video capture is properly released
            if cap is not None:
                cap.release()

    def _validate_video_inputs(self, video_path: str, output_dir: str) -> None:
        """Validate input parameters for video processing."""
        if not video_path or not isinstance(video_path, str):
            raise ValueError("video_path must be a non-empty string")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not output_dir or not isinstance(output_dir, str):
            raise ValueError("output_dir must be a non-empty string")
        
        # Check if we can create/write to output directory
        try:
            os.makedirs(output_dir, exist_ok=True)
            test_file = os.path.join(output_dir, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except (PermissionError, OSError) as e:
            raise PermissionError(f"Cannot write to output directory '{output_dir}': {e}")

    def _initialize_video_capture(self, video_path: str) -> cv2.VideoCapture:
        """Initialize video capture with validation."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # Verify video has frames
        ret, _ = cap.read()
        if not ret:
            cap.release()
            raise ValueError(f"Video file appears to be empty or corrupted: {video_path}")
        
        # Reset to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return cap

    def _get_video_info(self, cap: cv2.VideoCapture) -> Dict:
        """Extract video metadata."""
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0  # Default to 30 if not available
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        return {
            'total_frames': total_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'duration_seconds': total_frames / fps if fps > 0 else 0
        }

    def _process_video_frames(self,
                            cap: cv2.VideoCapture,
                            video_info: Dict,
                            frame_skip: int,
                            max_frames: Optional[int],
                            progress_callback: Optional[callable]) -> List[Dict]:
        """Process video frames and extract pose data."""
        pose_sequence = []
        frame_count = 0
        processed_count = 0
        
        # Calculate progress reporting interval
        total_frames = min(max_frames or video_info['total_frames'], video_info['total_frames'])
        progress_interval = max(1, total_frames // 100)  # Report every 1%
        
        while cap.isOpened() and (max_frames is None or processed_count < max_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames if requested
            if frame_count % frame_skip != 0:
                frame_count += 1
                continue
            
            try:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process pose estimation
                results = self.pose.process(rgb_frame)
                
                if results.pose_world_landmarks:
                    # Calculate actual timestamp based on video FPS
                    timestamp = frame_count / video_info['fps']
                    
                    frame_data = self._extract_3d_landmarks(
                        results.pose_world_landmarks,
                        frame_count,
                        timestamp
                    )
                    pose_sequence.append(frame_data)
                
            except Exception as e:
                # Log frame processing error but continue
                print(f"Warning: Failed to process frame {frame_count}: {e}")
                continue
            
            frame_count += 1
            processed_count += 1
            
            # Report progress
            if progress_callback and processed_count % progress_interval == 0:
                progress = (processed_count / total_frames) * 100
                progress_callback(progress, processed_count, total_frames)
        
        return pose_sequence

    def _save_pose_data(self,
                       pose_sequence: List[Dict],
                       output_dir: str,
                       video_info: Dict) -> str:
        """Save pose data with enhanced metadata."""
        output_file = os.path.join(output_dir, "pose_3d_sequence.json")
        
        # Prepare output data with enhanced metadata
        output_data = {
            'metadata': {
                'total_frames_processed': len(pose_sequence),
                'video_info': video_info,
                'coordinate_system': 'world_coordinates_meters',
                'landmark_names': self.landmark_names,
                'processing_timestamp': __import__('datetime').datetime.now().isoformat()
            },
            'pose_sequence': pose_sequence
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to save pose data to '{output_file}': {e}")
        
        return output_file

    def _extract_3d_landmarks(self, landmarks, frame_idx: int, timestamp: Optional[float] = None) -> Dict:
        """Extract 3D landmarks from MediaPipe results."""
        frame_data = {
            'frame': frame_idx,
            'timestamp': timestamp if timestamp is not None else frame_idx / 30.0,
            'landmarks_3d': []
        }
        
        for idx, landmark in enumerate(landmarks.landmark):
            frame_data['landmarks_3d'].append({
                'joint_name': self.landmark_names[idx],
                'joint_id': idx,
                'x': landmark.x,  # Meters from origin
                'y': landmark.y,  # Meters from origin  
                'z': landmark.z,  # Meters from origin (depth)
                'visibility': landmark.visibility
            })
        
        return frame_data

    def _apply_temporal_smoothing(self, pose_sequence: List[Dict], 
                                window_length: int = 5) -> List[Dict]:
        """
        Apply Savitzky-Golay filter for temporal smoothing of 3D trajectories.
        
        Args:
            pose_sequence: Raw pose sequence data
            window_length: Window size for smoothing filter
            
        Returns:
            Smoothed pose sequence
        """
        if len(pose_sequence) < window_length:
            return pose_sequence
        
        # Organize data by joint for smoothing
        joint_trajectories = {}
        for joint_name in self.landmark_names:
            joint_trajectories[joint_name] = {
                'x': [], 'y': [], 'z': [], 'visibility': []
            }
        
        # Extract trajectories
        for frame_data in pose_sequence:
            for landmark in frame_data['landmarks_3d']:
                joint_name = landmark['joint_name']
                joint_trajectories[joint_name]['x'].append(landmark['x'])
                joint_trajectories[joint_name]['y'].append(landmark['y'])
                joint_trajectories[joint_name]['z'].append(landmark['z'])
                joint_trajectories[joint_name]['visibility'].append(landmark['visibility'])
        
        # Apply smoothing
        for joint_name in joint_trajectories:
            for coord in ['x', 'y', 'z']:
                trajectory = np.array(joint_trajectories[joint_name][coord])
                if len(trajectory) >= window_length:
                    smoothed = savgol_filter(trajectory, window_length, 3)
                    joint_trajectories[joint_name][coord] = smoothed.tolist()
        
        # Reconstruct pose sequence with smoothed data
        smoothed_sequence = []
        for i, frame_data in enumerate(pose_sequence):
            smoothed_frame = {
                'frame': frame_data['frame'],
                'timestamp': frame_data['timestamp'],
                'landmarks_3d': []
            }
            
            for j, landmark in enumerate(frame_data['landmarks_3d']):
                joint_name = landmark['joint_name']
                smoothed_frame['landmarks_3d'].append({
                    'joint_name': joint_name,
                    'joint_id': landmark['joint_id'],
                    'x': joint_trajectories[joint_name]['x'][i],
                    'y': joint_trajectories[joint_name]['y'][i],
                    'z': joint_trajectories[joint_name]['z'][i],
                    'visibility': joint_trajectories[joint_name]['visibility'][i]
                })
            
            smoothed_sequence.append(smoothed_frame)
        
        return smoothed_sequence

    def create_3d_visualization(self, pose_data: Dict, output_dir: str) -> Tuple[str, str]:
        """
        Create 3D visualizations using matplotlib and plotly.
        
        Args:
            pose_data: 3D pose sequence data
            output_dir: Directory to save visualizations
            
        Returns:
            Tuple of (matplotlib_path, plotly_path)
        """
        matplotlib_path = self._create_matplotlib_3d(pose_data, output_dir)
        plotly_path = self._create_plotly_interactive(pose_data, output_dir)
        
        return matplotlib_path, plotly_path

    def _create_matplotlib_3d(self, pose_data: Dict, output_dir: str) -> str:
        """Create 3D trajectory plots using matplotlib."""
        fig = plt.figure(figsize=(15, 10))
        
        # Key joints for swing analysis
        key_joints = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                     'left_wrist', 'right_wrist', 'left_hip', 'right_hip']
        
        # Extract trajectories for key joints
        trajectories = {joint: {'x': [], 'y': [], 'z': []} for joint in key_joints}
        
        for frame_data in pose_data['pose_sequence']:
            for landmark in frame_data['landmarks_3d']:
                if landmark['joint_name'] in key_joints:
                    joint_name = landmark['joint_name']
                    trajectories[joint_name]['x'].append(landmark['x'])
                    trajectories[joint_name]['y'].append(landmark['y'])
                    trajectories[joint_name]['z'].append(landmark['z'])
        
        # Create subplots
        ax1 = fig.add_subplot(221, projection='3d')
        ax2 = fig.add_subplot(222, projection='3d')
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)
        
        # 3D trajectory plot
        colors = plt.cm.tab10(np.linspace(0, 1, len(key_joints)))
        for i, joint in enumerate(key_joints):
            if len(trajectories[joint]['x']) > 0:  # Check if data exists
                ax1.plot(trajectories[joint]['x'],
                        trajectories[joint]['y'],
                        trajectories[joint]['z'],
                        label=joint, color=colors[i], alpha=0.7)
        
        ax1.set_xlabel('X (meters)')
        ax1.set_ylabel('Y (meters)')
        ax1.set_zlabel('Z (meters)')
        ax1.set_title('3D Joint Trajectories')
        ax1.legend()
        
        # Wrist path analysis
        if len(trajectories['left_wrist']['x']) > 0 and len(trajectories['right_wrist']['x']) > 0:
            ax2.plot(trajectories['left_wrist']['x'], 
                    trajectories['left_wrist']['y'], 
                    trajectories['left_wrist']['z'], 
                    'b-', label='Left Wrist', linewidth=2)
            ax2.plot(trajectories['right_wrist']['x'], 
                    trajectories['right_wrist']['y'], 
                    trajectories['right_wrist']['z'], 
                    'r-', label='Right Wrist', linewidth=2)
            ax2.set_title('Wrist Path Analysis')
            ax2.legend()
        
        # X-Y plane view
        for i, joint in enumerate(['left_wrist', 'right_wrist']):
            if len(trajectories[joint]['x']) > 0:
                ax3.plot(trajectories[joint]['x'], trajectories[joint]['y'], 
                        label=joint, color=colors[i+6])
        ax3.set_xlabel('X (meters)')
        ax3.set_ylabel('Y (meters)')
        ax3.set_title('Top View (X-Y Plane)')
        ax3.legend()
        ax3.grid(True)
        
        # Z trajectory over time
        for i, joint in enumerate(['left_wrist', 'right_wrist']):
            if len(trajectories[joint]['z']) > 0:
                ax4.plot(trajectories[joint]['z'], label=joint, color=colors[i+6])
        ax4.set_xlabel('Frame')
        ax4.set_ylabel('Z (meters)')
        ax4.set_title('Depth Over Time')
        ax4.legend()
        ax4.grid(True)
        
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, 'swing_3d_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path

    def _create_plotly_interactive(self, pose_data: Dict, output_dir: str) -> str:
        """Create interactive 3D visualization using plotly."""
        fig = go.Figure()
        
        # Key joints for visualization
        key_joints = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                     'left_wrist', 'right_wrist', 'left_hip', 'right_hip']
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        # Extract and plot trajectories
        for i, joint in enumerate(key_joints):
            x_coords, y_coords, z_coords = [], [], []
            
            for frame_data in pose_data['pose_sequence']:
                for landmark in frame_data['landmarks_3d']:
                    if landmark['joint_name'] == joint:
                        x_coords.append(landmark['x'])
                        y_coords.append(landmark['y'])
                        z_coords.append(landmark['z'])
                        break
            
            if len(x_coords) > 0:  # Only plot if data exists
                fig.add_trace(go.Scatter3d(
                    x=x_coords,
                    y=y_coords,
                    z=z_coords,
                    mode='lines+markers',
                    name=joint,
                    line=dict(color=colors[i % len(colors)], width=4),
                    marker=dict(size=3)
                ))
        
        fig.update_layout(
            title='Interactive 3D Swing Analysis',
            scene=dict(
                xaxis_title='X (meters)',
                yaxis_title='Y (meters)',
                zaxis_title='Z (meters)',
                camera=dict(
                    eye=dict(x=1.2, y=1.2, z=0.8)
                )
            ),
            width=800,
            height=600
        )
        
        output_path = os.path.join(output_dir, 'interactive_3d_swing.html')
        offline.plot(fig, filename=output_path, auto_open=False)
        
        return output_path

    def create_mock_3d_data(self, output_dir: str) -> str:
        """Create mock 3D pose data for testing."""
        mock_sequence = []
        
        # Generate realistic swing motion over 60 frames (2 seconds at 30fps)
        for frame in range(60):
            t = frame / 30.0  # Time in seconds
            swing_phase = np.sin(t * np.pi)  # Swing motion from 0 to 1 and back
            
            frame_data = {
                'frame': frame,
                'timestamp': t,
                'landmarks_3d': []
            }
            
            # Generate realistic 3D coordinates for key joints
            base_positions = {
                'left_shoulder': [0.2, 0.0, 1.4],
                'right_shoulder': [-0.2, 0.0, 1.4],
                'left_elbow': [0.3, -0.1, 1.2],
                'right_elbow': [-0.3, -0.1, 1.2],
                'left_wrist': [0.4, -0.2, 1.0],
                'right_wrist': [-0.4, -0.2, 1.0],
                'left_hip': [0.1, 0.0, 0.9],
                'right_hip': [-0.1, 0.0, 0.9],
                'left_knee': [0.1, 0.0, 0.5],
                'right_knee': [-0.1, 0.0, 0.5],
                'left_ankle': [0.1, 0.0, 0.1],
                'right_ankle': [-0.1, 0.0, 0.1]
            }
            
            for idx, joint_name in enumerate(self.landmark_names):
                if joint_name in base_positions:
                    base_pos = base_positions[joint_name]
                    # Add swing motion
                    x = base_pos[0] + swing_phase * 0.3
                    y = base_pos[1] + swing_phase * 0.2
                    z = base_pos[2]
                else:
                    # Default position for other joints
                    x, y, z = 0.0, 0.0, 1.0
                
                frame_data['landmarks_3d'].append({
                    'joint_name': joint_name,
                    'joint_id': idx,
                    'x': x,
                    'y': y,
                    'z': z,
                    'visibility': 0.9
                })
            
            mock_sequence.append(frame_data)
        
        # Save mock data
        mock_data = {
            'total_frames': 60,
            'pose_sequence': mock_sequence,
            'landmark_names': self.landmark_names,
            'coordinate_system': 'world_coordinates_meters'
        }
        
        output_file = os.path.join(output_dir, "pose_3d_sequence.json")
        with open(output_file, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        return output_file

if __name__ == "__main__":
    # Test the 3D pose estimator
    estimator = Pose3DEstimator()
    test_dir = "./test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create mock data for testing
    pose_file = estimator.create_mock_3d_data(test_dir)
    print(f"Mock 3D pose data created: {pose_file}")
    
    # Create visualizations
    with open(pose_file, 'r') as f:
        pose_data = json.load(f)
    
    matplotlib_path, plotly_path = estimator.create_3d_visualization(pose_data, test_dir)
    print(f"Visualizations created: {matplotlib_path}, {plotly_path}")