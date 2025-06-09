"""
3D Biomechanics Analysis Module for Baseball Swing
Enhanced analysis using 3D pose data for comprehensive swing evaluation
"""

import numpy as np
import json
import math
from typing import List, Dict, Tuple, Optional
from scipy.spatial.transform import Rotation as R
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

class Biomechanics3DAnalyzer:
    def __init__(self, ideal_metrics_path: str = "biomechanics_ideal.json"):
        """Initialize 3D biomechanics analyzer with ideal swing metrics."""
        try:
            with open(ideal_metrics_path, 'r') as f:
                self.ideal_metrics = json.load(f)
        except FileNotFoundError:
            # Enhanced default metrics for 3D analysis
            self.ideal_metrics = {
                "hip_shoulder_separation_3d": [0.15, 0.35],  # meters
                "pelvis_rotation_deg": [40, 60],
                "shoulder_rotation_deg": [90, 120],
                "bat_speed_mph": [75, 95],
                "stride_timing_ms": [150, 200],
                "knee_angle_deg": [140, 170],
                "elbow_angle_deg": [90, 140],
                "wrist_snap_timing_ms": [50, 100],
                "weight_transfer_ratio": [0.6, 0.8],
                "hip_lead_time_ms": [30, 80],
                "launch_angle_deg": [10, 30],
                "spine_tilt_deg": [10, 25]
            }
        
        # Joint indices for MediaPipe pose
        self.joints = {
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28,
            'nose': 0
        }

    def analyze_swing_3d(self, pose_data: Dict) -> Dict:
 
        """
        Comprehensive 3D swing analysis.
        
        Args:
            pose_data: 3D pose sequence data
            
        Returns:
            Detailed swing analysis results
        """
        analysis_results = {
            'swing_phases': self._identify_swing_phases(pose_data),
            'kinematic_sequence': self._analyze_kinematic_sequence(pose_data),
            'spatial_analysis': self._analyze_spatial_mechanics(pose_data),
            'temporal_analysis': self._analyze_temporal_mechanics(pose_data),
            'issues_detected': [],
            'recommendations': [],
            'performance_scores': {},
            'visualization_data': {}
        }  
        
        # Detect biomechanical issues
        issues = self._detect_3d_issues(pose_data, analysis_results)
        analysis_results['issues_detected'] = issues
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues)
        analysis_results['recommendations'] = recommendations
        
        # Calculate performance scores
        scores = self._calculate_performance_scores(analysis_results)
        analysis_results['performance_scores'] = scores
        
        return analysis_results

    def _identify_swing_phases(self, pose_data: Dict) -> Dict:
        """Identify key phases of the swing using 3D kinematics."""
        sequence = pose_data['pose_sequence']
        if not sequence:
            return {}
        
        # Extract wrist positions over time
        wrist_positions = self._extract_joint_trajectory(sequence, 'right_wrist')
        if len(wrist_positions) == 0:
            wrist_positions = self._extract_joint_trajectory(sequence, 'left_wrist')
        
        if len(wrist_positions) == 0:
            return {}
        
        # Calculate wrist velocity and acceleration
        velocities = self._calculate_velocity(wrist_positions)
        accelerations = self._calculate_acceleration(velocities)
        
        # Identify swing phases based on velocity patterns
        phases = {
            'stance': {'start': 0, 'end': 0},
            'load': {'start': 0, 'end': 0},
            'stride': {'start': 0, 'end': 0},
            'swing': {'start': 0, 'end': 0},
            'contact': {'start': 0, 'end': 0},
            'follow_through': {'start': 0, 'end': 0}
        }
        
        # Find velocity peaks to identify phase transitions
        if len(velocities) > 10:
            vel_magnitude = [np.linalg.norm(v) for v in velocities]
            peaks, _ = find_peaks(vel_magnitude, height=np.mean(vel_magnitude))
            
            if len(peaks) > 0:
                # Estimate phases based on velocity profile
                total_frames = len(sequence)
                
                # Stance phase (beginning, low movement)
                phases['stance']['end'] = min(total_frames // 4, 15)
                
                # Load phase (gathering energy)
                phases['load']['start'] = phases['stance']['end']
                phases['load']['end'] = min(total_frames // 3, 20)
                
                # Stride phase (forward movement)
                phases['stride']['start'] = phases['load']['end']
                phases['stride']['end'] = min(total_frames // 2, 30)
                
                # Swing phase (bat acceleration)
                phases['swing']['start'] = phases['stride']['end']
                contact_frame = peaks[0] if peaks is not None and len(peaks) > 0 else total_frames * 2 // 3

                phases['swing']['end'] = contact_frame
                
                # Contact phase (ball contact)
                phases['contact']['start'] = contact_frame
                phases['contact']['end'] = min(contact_frame + 3, total_frames - 5)
                
                # Follow through
                phases['follow_through']['start'] = phases['contact']['end']
                phases['follow_through']['end'] = total_frames - 1
        
        return phases

    def _analyze_kinematic_sequence(self, pose_data: Dict) -> Dict:
        """Analyze the kinematic sequence (ground up power generation)."""
        sequence = pose_data['pose_sequence']
        
        # Extract angular velocities for key body segments
        hip_rotation = self._calculate_segment_rotation(sequence, 'hips')
        shoulder_rotation = self._calculate_segment_rotation(sequence, 'shoulders')
        
        kinematic_sequence = {
            'hip_initiation_time': 0,
            'shoulder_initiation_time': 0,
            'hip_peak_velocity': 0,
            'shoulder_peak_velocity': 0,
            'sequence_efficiency': 0,
            'energy_transfer': 'optimal'
        }
        
        if hip_rotation and shoulder_rotation:
            # Find when each segment starts accelerating
            hip_accel = np.diff(hip_rotation)
            shoulder_accel = np.diff(shoulder_rotation)
            
            # Find initiation points (when acceleration becomes significant)
            hip_threshold = np.std(hip_accel) * 2
            shoulder_threshold = np.std(shoulder_accel) * 2
            
            hip_start = np.where(np.abs(hip_accel) > hip_threshold)[0]
            shoulder_start = np.where(np.abs(shoulder_accel) > shoulder_threshold)[0]
            
            if len(hip_start) > 0 and len(shoulder_start) > 0:
                kinematic_sequence['hip_initiation_time'] = hip_start[0]
                kinematic_sequence['shoulder_initiation_time'] = shoulder_start[0]
                
                # Check if hips lead shoulders (proper kinematic sequence)
                if hip_start[0] < shoulder_start[0]:
                    lead_time = shoulder_start[0] - hip_start[0]
                    kinematic_sequence['sequence_efficiency'] = min(100, lead_time * 10)
                    
                    if lead_time >= 2:
                        kinematic_sequence['energy_transfer'] = 'optimal'
                    elif lead_time >= 1:
                        kinematic_sequence['energy_transfer'] = 'good'
                    else:
                        kinematic_sequence['energy_transfer'] = 'poor'
                else:
                    kinematic_sequence['energy_transfer'] = 'reverse'
        
        return kinematic_sequence

    def _analyze_spatial_mechanics(self, pose_data: Dict) -> Dict:
        """Analyze spatial aspects of the swing."""
        sequence = pose_data['pose_sequence']
        
        spatial_analysis = {
            'hip_shoulder_separation': [],
            'spine_tilt': [],
            'stance_width': [],
            'weight_distribution': [],
            'bat_path_efficiency': 0
        }
        
        for frame_data in sequence:
            landmarks = {lm['joint_name']: lm for lm in frame_data['landmarks_3d']}
            
            # Hip-shoulder separation in 3D
            if all(joint in landmarks for joint in ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder']):
                hip_center = self._calculate_midpoint_3d(
                    landmarks['left_hip'], landmarks['right_hip']
                )
                shoulder_center = self._calculate_midpoint_3d(
                    landmarks['left_shoulder'], landmarks['right_shoulder']
                )
                separation = self._distance_3d(hip_center, shoulder_center)
                spatial_analysis['hip_shoulder_separation'].append(separation)
            
            # Spine tilt angle
            if all(joint in landmarks for joint in ['nose', 'left_hip', 'right_hip']):
                spine_tilt = self._calculate_spine_tilt(
                    landmarks['nose'], landmarks['left_hip'], landmarks['right_hip']
                )
                spatial_analysis['spine_tilt'].append(spine_tilt)
            
            # Stance width
            if 'left_ankle' in landmarks and 'right_ankle' in landmarks:
                stance_width = abs(landmarks['left_ankle']['x'] - landmarks['right_ankle']['x'])
                spatial_analysis['stance_width'].append(stance_width)
        
        return spatial_analysis

    def _analyze_temporal_mechanics(self, pose_data: Dict) -> Dict:
        """Analyze timing aspects of the swing."""
        sequence = pose_data['pose_sequence']
        
        temporal_analysis = {
            'total_swing_time': 0,
            'acceleration_phase_duration': 0,
            'deceleration_phase_duration': 0,
            'timing_efficiency': 0
        }
        
        if sequence:
            total_frames = len(sequence)
            fps = 30  # Assumed frame rate
            temporal_analysis['total_swing_time'] = total_frames / fps
            
            # Analyze wrist velocity to determine acceleration/deceleration phases
            wrist_positions = self._extract_joint_trajectory(sequence, 'right_wrist')
            if len(wrist_positions) > 0:
                velocities = self._calculate_velocity(wrist_positions)
                vel_magnitudes = [np.linalg.norm(v) for v in velocities]
                
                if len(vel_magnitudes) > 0:
                    peak_idx = np.argmax(vel_magnitudes)
                    temporal_analysis['acceleration_phase_duration'] = peak_idx / fps
                    temporal_analysis['deceleration_phase_duration'] = (len(vel_magnitudes) - peak_idx) / fps
        
        return temporal_analysis

    def _detect_3d_issues(self, pose_data: Dict, analysis: Dict) -> List[str]:
        """Detect biomechanical issues using 3D analysis."""
        issues = []
        
        # Check hip-shoulder separation
        hip_sep_data = analysis['spatial_analysis']['hip_shoulder_separation']
        if len(hip_sep_data) > 0:
            avg_separation = np.mean(hip_sep_data)
            ideal_range = self.ideal_metrics['hip_shoulder_separation_3d']
            
            if avg_separation < ideal_range[0]:
                issues.append("Insufficient 3D hip-shoulder separation")
            elif avg_separation > ideal_range[1]:
                issues.append("Excessive hip-shoulder separation")
        
        # Check kinematic sequence
        kinematic = analysis['kinematic_sequence']
        if kinematic['energy_transfer'] == 'reverse':
            issues.append("Reverse kinematic sequence - shoulders leading hips")
        elif kinematic['energy_transfer'] == 'poor':
            issues.append("Poor kinematic sequence timing")
        
        # Check spine tilt
        spine_tilt_data = analysis['spatial_analysis']['spine_tilt']
        if len(spine_tilt_data) > 0:
            avg_tilt = np.mean(spine_tilt_data)
            ideal_range = self.ideal_metrics['spine_tilt_deg']
            
            if avg_tilt < ideal_range[0]:
                issues.append("Insufficient spine tilt")
            elif avg_tilt > ideal_range[1]:
                issues.append("Excessive spine tilt")
        
        # Check stance width
        stance_width_data = analysis['spatial_analysis']['stance_width']
        if len(stance_width_data) > 0:
            avg_width = np.mean(stance_width_data)
            if avg_width < 0.3:  # meters
                issues.append("Narrow stance detected")
            elif avg_width > 0.8:
                issues.append("Overly wide stance")
        
        return issues

    def _generate_recommendations(self, issues: List[str]) -> List[Dict]:
        """Generate specific recommendations based on detected issues."""
        recommendations_map = {
            "Insufficient 3D hip-shoulder separation": {
                "category": "Kinematic Sequence",
                "drills": [
                    "3D separation drill with resistance bands",
                    "Hip turn with shoulder restraint drill",
                    "Mirror work focusing on torso coil",
                    "Medicine ball rotational throws"
                ],
                "exercises": [
                    "Seated Russian twists",
                    "Cable wood chops",
                    "Thoracic spine mobility work",
                    "Hip flexor stretches"
                ],
                "technical_focus": "Work on creating proper torso coil by leading with hips while keeping shoulders closed"
            },
            "Reverse kinematic sequence - shoulders leading hips": {
                "category": "Power Generation",
                "drills": [
                    "Hip-first initiation drill",
                    "Pause swing with hip emphasis",
                    "Towel drill for sequence timing",
                    "Step and swing coordination"
                ],
                "exercises": [
                    "Hip abductor strengthening",
                    "Glute activation exercises",
                    "Core rotational power training",
                    "Balance and proprioception work"
                ],
                "technical_focus": "Practice initiating movement from the ground up - hips lead, shoulders follow"
            },
            "Insufficient spine tilt": {
                "category": "Posture & Setup",
                "drills": [
                    "Spine angle awareness drill",
                    "Posture mirror work",
                    "Athletic position holds",
                    "Tilt and turn combination drill"
                ],
                "exercises": [
                    "Thoracic extension exercises",
                    "Hip hinge movement patterns",
                    "Posterior chain strengthening",
                    "Core stability training"
                ],
                "technical_focus": "Maintain proper spine tilt throughout the swing for optimal launch angle"
            },
            "Narrow stance detected": {
                "category": "Setup & Balance",
                "drills": [
                    "Stance width marker drill",
                    "Wide stance batting practice",
                    "Balance challenge drills",
                    "Stability progression training"
                ],
                "exercises": [
                    "Single-leg balance exercises",
                    "Lateral strength training",
                    "Hip abductor strengthening",
                    "Ankle stability work"
                ],
                "technical_focus": "Establish a stable, athletic base with proper foot placement for balance and power"
            }
        }
        
        recommendations = []
        for issue in issues:
            if issue in recommendations_map:
                recommendations.append(recommendations_map[issue])
            else:
                # Generic recommendation for unspecified issues
                recommendations.append({
                    "category": "General Improvement",
                    "drills": ["Video analysis and feedback", "Slow motion practice"],
                    "exercises": ["General strength and conditioning"],
                    "technical_focus": f"Address: {issue}"
                })
        
        return recommendations

    def _calculate_performance_scores(self, analysis: Dict) -> Dict:
        """Calculate overall performance scores."""
        scores = {
            'kinematic_sequence_score': 0,
            'spatial_mechanics_score': 0,
            'temporal_efficiency_score': 0,
            'overall_score': 0
        }
        
        # Kinematic sequence score
        kinematic = analysis['kinematic_sequence']
        if kinematic['energy_transfer'] == 'optimal':
            scores['kinematic_sequence_score'] = 95
        elif kinematic['energy_transfer'] == 'good':
            scores['kinematic_sequence_score'] = 80
        elif kinematic['energy_transfer'] == 'poor':
            scores['kinematic_sequence_score'] = 60
        else:  # reverse
            scores['kinematic_sequence_score'] = 30
        
        # Spatial mechanics score (based on number of issues)
        total_possible_issues = 4  # Number of spatial checks
        issues_found = len([issue for issue in analysis['issues_detected'] 
                           if any(keyword in issue.lower() for keyword in 
                                ['separation', 'stance', 'tilt', 'posture'])])
        scores['spatial_mechanics_score'] = max(0, 100 - (issues_found / total_possible_issues) * 100)
        
        # Temporal efficiency score
        temporal = analysis['temporal_analysis']
        if 1.0 <= temporal['total_swing_time'] <= 1.5:  # Optimal swing time
            scores['temporal_efficiency_score'] = 90
        else:
            scores['temporal_efficiency_score'] = max(0, 90 - abs(temporal['total_swing_time'] - 1.25) * 40)
        
        # Overall score
        scores['overall_score'] = (
            scores['kinematic_sequence_score'] * 0.4 +
            scores['spatial_mechanics_score'] * 0.4 +
            scores['temporal_efficiency_score'] * 0.2
        )
        
        return scores

    # Helper methods
    def _extract_joint_trajectory(self, sequence: List, joint_name: str) -> List[Tuple[float, float, float]]:
        """Extract 3D trajectory for a specific joint."""
        trajectory = []
        for frame_data in sequence:
            for landmark in frame_data['landmarks_3d']:
                if landmark['joint_name'] == joint_name:
                    trajectory.append((landmark['x'], landmark['y'], landmark['z']))
                    break
        return trajectory

    def _calculate_velocity(self, positions: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """Calculate 3D velocity from position data."""
        velocities = []
        for i in range(1, len(positions)):
            dt = 1/30.0  # Assuming 30 FPS
            vel = tuple((positions[i][j] - positions[i-1][j]) / dt for j in range(3))
            velocities.append(vel)
        return velocities

    def _calculate_acceleration(self, velocities: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """Calculate 3D acceleration from velocity data."""
        accelerations = []
        for i in range(1, len(velocities)):
            dt = 1/30.0
            acc = tuple((velocities[i][j] - velocities[i-1][j]) / dt for j in range(3))
            accelerations.append(acc)
        return accelerations

    def _calculate_segment_rotation(self, sequence: List, segment: str) -> List[float]:
        """Calculate rotation of body segment over time."""
        rotations = []
        
        for frame_data in sequence:
            landmarks = {lm['joint_name']: lm for lm in frame_data['landmarks_3d']}
            
            if segment == 'hips':
                if 'left_hip' in landmarks and 'right_hip' in landmarks:
                    # Calculate hip rotation based on hip line orientation
                    left_hip = landmarks['left_hip']
                    right_hip = landmarks['right_hip']
                    angle = math.atan2(left_hip['y'] - right_hip['y'], 
                                     left_hip['x'] - right_hip['x'])
                    rotations.append(math.degrees(angle))
            
            elif segment == 'shoulders':
                if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
                    left_shoulder = landmarks['left_shoulder']
                    right_shoulder = landmarks['right_shoulder']
                    angle = math.atan2(left_shoulder['y'] - right_shoulder['y'], 
                                     left_shoulder['x'] - right_shoulder['x'])
                    rotations.append(math.degrees(angle))
        
        return rotations

    def _calculate_midpoint_3d(self, point1: Dict, point2: Dict) -> Tuple[float, float, float]:
        """Calculate 3D midpoint between two landmarks."""
        return (
            (point1['x'] + point2['x']) / 2,
            (point1['y'] + point2['y']) / 2,
            (point1['z'] + point2['z']) / 2
        )

    def _distance_3d(self, point1: Tuple[float, float, float], 
                    point2: Tuple[float, float, float]) -> float:
        """Calculate 3D distance between two points."""
        return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))

    def _calculate_spine_tilt(self, head: Dict, left_hip: Dict, right_hip: Dict) -> float:
        """Calculate spine tilt angle."""
        hip_center = self._calculate_midpoint_3d(left_hip, right_hip)
        
        # Vector from hip center to head
        spine_vector = (head['x'] - hip_center[0], 
                       head['y'] - hip_center[1], 
                       head['z'] - hip_center[2])
        
        # Calculate angle with vertical (z-axis)
        vertical = (0, 0, 1)
        dot_product = spine_vector[2]  # z component
        spine_magnitude = math.sqrt(sum(comp**2 for comp in spine_vector))
        
        if spine_magnitude == 0:
            return 0
        
        cos_angle = dot_product / spine_magnitude
        cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
        angle = math.acos(cos_angle)
        
        return math.degrees(angle)