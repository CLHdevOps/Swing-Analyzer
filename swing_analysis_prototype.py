# swing_analysis_prototype.py
# Advanced: AI-Powered 3D Swing Analysis using MediaPipe + Enhanced Biomechanics

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
import tempfile
import shutil
import traceback
import numpy as np
from pose_3d_estimator import Pose3DEstimator
from biomechanics_3d_analyzer import Biomechanics3DAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Custom JSON encoder to handle numpy types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Initialize 3D pose estimation and biomechanics analysis
pose_estimator = Pose3DEstimator()
biomechanics_analyzer = Biomechanics3DAnalyzer()

# Load biomechanical swing standards from a JSON file
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "biomechanics_ideal.json")
    with open(json_path) as f:
        IDEAL_METRICS = json.load(f)
except FileNotFoundError:
    print("Warning: biomechanics_ideal.json not found. Using default values.")
    IDEAL_METRICS = {
        "hip_shoulder_separation": [30, 60],
        "hip_shoulder_separation_3d": [0.15, 0.35],
        "pelvis_rotation_deg": [40, 60],
        "bat_speed_mph": [75, 95]
    }

def run_3d_pose_analysis(video_path, output_dir):
    """Run 3D pose analysis on the uploaded video using MediaPipe."""
    try:
        # Process video with 3D pose estimation
        pose_file = pose_estimator.process_video(video_path, output_dir)
        
        # Load pose data for analysis
        with open(pose_file, 'r') as f:
            pose_data = json.load(f)
        
        # Perform biomechanical analysis
        analysis_results = biomechanics_analyzer.analyze_swing_3d(pose_data)
        
        # Create visualizations
        matplotlib_path, plotly_path = pose_estimator.create_3d_visualization(pose_data, output_dir)
        analysis_results['visualizations'] = {
            'matplotlib_plot': matplotlib_path,
            'interactive_plot': plotly_path
        }
        
        return analysis_results
        
    except Exception as e:
        print(f"3D pose analysis failed: {e}")
        print("Using mock 3D analysis for testing...")
        return create_mock_3d_analysis(output_dir)

def create_mock_3d_analysis(output_dir):
    """Create mock 3D analysis for testing when pose estimation fails."""
    try:
        # Create mock 3D pose data
        pose_file = pose_estimator.create_mock_3d_data(output_dir)
        
        # Load mock data
        with open(pose_file, 'r') as f:
            pose_data = json.load(f)
        
        # Analyze mock data
        analysis_results = biomechanics_analyzer.analyze_swing_3d(pose_data)
        
        # Create mock visualizations
        matplotlib_path, plotly_path = pose_estimator.create_3d_visualization(pose_data, output_dir)
        analysis_results['visualizations'] = {
            'matplotlib_plot': matplotlib_path,
            'interactive_plot': plotly_path
        }
        
        # Add some intentional issues for demonstration
        analysis_results['issues_detected'].extend([
            "Mock analysis - Insufficient 3D hip-shoulder separation",
            "Mock analysis - Poor kinematic sequence timing"
        ])
        
        return analysis_results
        
    except Exception as e:
        print(f"Mock analysis creation failed: {e}")
        return {
            'issues_detected': ["Analysis system unavailable"],
            'recommendations': [],
            'performance_scores': {'overall_score': 0},
            'swing_phases': {},
            'kinematic_sequence': {},
            'spatial_analysis': {},
            'temporal_analysis': {}
        }

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Validate request
        if 'video' not in request.files:
            return jsonify({
                "error": "No video file provided",
                "status": "error"
            }), 400
        
        video = request.files['video']
        if video.filename == '':
            return jsonify({
                "error": "No video file selected",
                "status": "error"
            }), 400
        
        # Check file size (limit to 100MB)
        video.seek(0, 2)  # Seek to end
        file_size = video.tell()
        video.seek(0)  # Reset to beginning
        
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return jsonify({
                "error": "File size too large. Maximum size is 100MB.",
                "status": "error"
            }), 400
        
        # Create temporary directories
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Save uploaded video
            video.save(video_path)
            
            # Run 3D pose analysis
            analysis_results = run_3d_pose_analysis(video_path, output_dir)
            
            # Build visualization URLs if visualizations exist
            visualizations = {}
            if 'visualizations' in analysis_results and analysis_results['visualizations']:
                vis = analysis_results['visualizations']
                if 'matplotlib_plot' in vis and vis['matplotlib_plot']:
                    visualizations['matplotlib_plot'] = f"/visualization/{os.path.basename(vis['matplotlib_plot'])}"
                if 'interactive_plot' in vis and vis['interactive_plot']:
                    visualizations['interactive_plot'] = f"/visualization/{os.path.basename(vis['interactive_plot'])}"
            
            # Build response
            return jsonify({
                "score": analysis_results.get('score', 0),
                "feedback": analysis_results.get('recommendations', []),
                "status": "success",
                "analysis_type": "3D Pose Analysis",
                "performance_scores": analysis_results.get('performance_scores', {}),
                "swing_phases": analysis_results.get('swing_phases', {}),
                "kinematic_sequence": analysis_results.get('kinematic_sequence', {}),
                "spatial_analysis": analysis_results.get('spatial_analysis', {}),
                "temporal_analysis": analysis_results.get('temporal_analysis', {}),
                "visualizations": visualizations,
                "analysis_notes": "3D analysis response"
            })
            
        finally:
            # Store temp_dir path for visualization serving
            app.config['TEMP_DIRS'] = getattr(app.config, 'TEMP_DIRS', [])
            app.config['TEMP_DIRS'].append(temp_dir)
            
            # Clean up old temp directories
            if len(app.config['TEMP_DIRS']) > 5:
                old_dir = app.config['TEMP_DIRS'].pop(0)
                try:
                    shutil.rmtree(old_dir)
                except Exception as e:
                    print(f"Error cleaning up temp directory: {str(e)}")
                
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": f"3D Analysis failed: {str(e)}",
            "status": "error",
            "analysis_type": "Error"
        }), 500

@app.route('/visualization/<filename>')
def serve_visualization(filename):
    """Serve visualization files."""
    try:
        # Look for the file in temp directories
        for temp_dir in app.config.get('TEMP_DIRS', []):
            file_path = os.path.join(temp_dir, 'output', filename)
            if os.path.exists(file_path):
                return send_file(file_path)
        
        return jsonify({"error": "Visualization not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to serve visualization: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test MediaPipe availability
        import mediapipe as mp
        mediapipe_available = True
    except ImportError:
        mediapipe_available = False
    
    try:
        # Test other dependencies
        import cv2, numpy, matplotlib, plotly, scipy
        dependencies_available = True
    except ImportError:
        dependencies_available = False
    
    return jsonify({
        "status": "healthy",
        "analysis_type": "3D Pose Analysis with MediaPipe",
        "mediapipe_available": mediapipe_available,
        "dependencies_available": dependencies_available,
        "features": [
            "3D pose estimation",
            "Kinematic sequence analysis",
            "Spatial biomechanics",
            "Temporal analysis",
            "Interactive visualizations"
        ]
    })

if __name__ == '__main__':
    print("Starting Swing Analyzer backend...")
    print("Health check: http://localhost:5001/health")
    print("Analysis endpoint: POST http://localhost:5001/analyze")
    app.run(host='0.0.0.0', port=5001, debug=True)
