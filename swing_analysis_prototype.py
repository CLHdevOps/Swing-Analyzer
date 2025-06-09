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
try:
    from pose_3d_estimator import Pose3DEstimator
    from biomechanics_3d_analyzer import Biomechanics3DAnalyzer
except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    print("Some features may not work properly.")
    Pose3DEstimator = None
    Biomechanics3DAnalyzer = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Custom JSON encoder to handle numpy types and arrays
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Initialize 3D pose estimation and biomechanics analysis
pose_estimator = Pose3DEstimator() if Pose3DEstimator else None
biomechanics_analyzer = Biomechanics3DAnalyzer() if Biomechanics3DAnalyzer else None

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

def sanitize_for_json(data):
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(data, dict):
        return {key: sanitize_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(item) for item in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, np.bool_):
        return bool(data)
    elif hasattr(data, 'item'):
        return data.item()
    else:
        return data

def run_3d_pose_analysis(video_path: str, output_dir: str, use_mock_fallback: bool = True) -> dict:
    """
    Run comprehensive 3D pose analysis on a video file.
    
    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory for output files and visualizations
        use_mock_fallback (bool): Whether to fall back to mock analysis on failure
        
    Returns:
        dict: Analysis results containing scores, recommendations, and visualizations
        
    Raises:
        ValueError: If input parameters are invalid
        FileNotFoundError: If video file doesn't exist
        RuntimeError: If analysis fails and fallback is disabled
    """
    # Input validation
    _validate_analysis_inputs(video_path, output_dir)
    
    # Check module availability
    if not _are_analysis_modules_available():
        if use_mock_fallback:
            print("Analysis modules not available. Using mock analysis.")
            return create_mock_3d_analysis(output_dir)
        else:
            raise RuntimeError("Analysis modules are not available and fallback is disabled")
    
    try:
        # Step 1: Process video with 3D pose estimation
        pose_file = _process_video_for_pose_data(video_path, output_dir)
        
        # Step 2: Load and validate pose data
        pose_data = _load_and_validate_pose_data(pose_file)
        
        # Step 3: Perform biomechanical analysis
        analysis_results = _perform_biomechanical_analysis(pose_data)
        
        # Step 4: Generate visualizations
        visualization_paths = _create_analysis_visualizations(pose_data, output_dir)
        analysis_results['visualizations'] = visualization_paths
        
        # Step 5: Validate and sanitize results
        return _finalize_analysis_results(analysis_results)
        
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"3D pose analysis failed with specific error: {e}")
        if use_mock_fallback:
            print("Using mock 3D analysis for testing...")
            return create_mock_3d_analysis(output_dir)
        else:
            raise RuntimeError(f"Analysis failed: {e}") from e
            
    except Exception as e:
        print(f"Unexpected error during 3D pose analysis: {e}")
        print(f"Error type: {type(e).__name__}")
        if use_mock_fallback:
            print("Using mock 3D analysis for testing...")
            return create_mock_3d_analysis(output_dir)
        else:
            raise RuntimeError(f"Unexpected analysis failure: {e}") from e


def _validate_analysis_inputs(video_path: str, output_dir: str) -> None:
    """Validate input parameters for analysis."""
    if not video_path or not isinstance(video_path, str):
        raise ValueError("video_path must be a non-empty string")
    
    if not output_dir or not isinstance(output_dir, str):
        raise ValueError("output_dir must be a non-empty string")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.isfile(video_path):
        raise ValueError(f"video_path must be a file, not a directory: {video_path}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)


def _are_analysis_modules_available() -> bool:
    """Check if required analysis modules are available."""
    return pose_estimator is not None and biomechanics_analyzer is not None


def _process_video_for_pose_data(video_path: str, output_dir: str) -> str:
    """Process video file to extract pose data."""
    try:
        pose_file = pose_estimator.process_video(video_path, output_dir)
        
        if not pose_file or not os.path.exists(pose_file):
            raise FileNotFoundError(f"Pose estimation failed to generate output file: {pose_file}")
            
        return pose_file
        
    except Exception as e:
        raise RuntimeError(f"Video processing failed: {e}") from e


def _load_and_validate_pose_data(pose_file: str) -> dict:
    """Load pose data from file and validate its structure."""
    try:
        with open(pose_file, 'r', encoding='utf-8') as f:
            pose_data = json.load(f)
        
        # Basic validation of pose data structure
        if not isinstance(pose_data, dict):
            raise ValueError("Pose data must be a dictionary")
            
        # Add more specific validation as needed based on your data structure
        required_keys = ['poses', 'metadata']  # Adjust based on your actual structure
        missing_keys = [key for key in required_keys if key not in pose_data]
        if missing_keys:
            print(f"Warning: Missing keys in pose data: {missing_keys}")
            print("Loaded pose data:", pose_data)
        if 'poses' not in pose_data:
            raise RuntimeError("Pose data missing 'poses' key")

        
        return pose_data
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in pose file {pose_file}: {e.msg}", e.doc, e.pos) from e
    except FileNotFoundError:
        raise FileNotFoundError(f"Pose data file not found: {pose_file}")


def _perform_biomechanical_analysis(pose_data: dict) -> dict:
    """Perform biomechanical analysis on pose data."""
    try:
        analysis_results = biomechanics_analyzer.analyze_swing_3d(pose_data)
        
        if not isinstance(analysis_results, dict):
            raise ValueError("Biomechanical analysis must return a dictionary")
            
        return analysis_results
        
    except Exception as e:
        raise RuntimeError(f"Biomechanical analysis failed: {e}") from e


def _create_analysis_visualizations(pose_data: dict, output_dir: str) -> dict:
    """Create visualization files for the analysis."""
    try:
        matplotlib_path, plotly_path = pose_estimator.create_3d_visualization(pose_data, output_dir)
        
        visualizations = {}
        
        if matplotlib_path and os.path.exists(matplotlib_path):
            visualizations['matplotlib_plot'] = matplotlib_path
        else:
            print("Warning: Matplotlib visualization was not created successfully")
            
        if plotly_path and os.path.exists(plotly_path):
            visualizations['interactive_plot'] = plotly_path
        else:
            print("Warning: Plotly visualization was not created successfully")
            
        return visualizations
        
    except Exception as e:
        print(f"Warning: Visualization creation failed: {e}")
        return {}


def _finalize_analysis_results(analysis_results: dict) -> dict:
    """Validate and sanitize final analysis results."""
    # Ensure required keys exist with defaults
    default_structure = {
        'issues_detected': [],
        'recommendations': [],
        'performance_scores': {'overall_score': 0},
        'swing_phases': {},
        'kinematic_sequence': {},
        'spatial_analysis': {},
        'temporal_analysis': {},
        'visualizations': {}
    }
    
    # Merge with defaults
    for key, default_value in default_structure.items():
        if key not in analysis_results:
            analysis_results[key] = default_value
    
    # Sanitize for JSON serialization
    return sanitize_for_json(analysis_results)
    
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
@app.route('/')
def index():
    return 'Swing Analyzer Backend Running', 200

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
            
            # Sanitize all analysis results for JSON serialization
            analysis_results = sanitize_for_json(analysis_results)
            
            # Build visualization URLs if visualizations exist
            visualizations = {}
            if 'visualizations' in analysis_results and analysis_results['visualizations']:
                vis = analysis_results['visualizations']
                if 'matplotlib_plot' in vis and vis['matplotlib_plot']:
                    visualizations['matplotlib_plot'] = f"/visualization/{os.path.basename(vis['matplotlib_plot'])}"
                if 'interactive_plot' in vis and vis['interactive_plot']:
                    visualizations['interactive_plot'] = f"/visualization/{os.path.basename(vis['interactive_plot'])}"
            
            # Build response with sanitized data
            response_data = {
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
            }
            
            # Final sanitization to ensure no numpy types remain
            response_data = sanitize_for_json(response_data)
            
            return jsonify(response_data)
            
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
    }), 200

if __name__ == '__main__':
    print("Starting Swing Analyzer backend...")
    print("Health check: http://localhost:5001/health")
    print("Analysis endpoint: POST http://localhost:5001/analyze")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)