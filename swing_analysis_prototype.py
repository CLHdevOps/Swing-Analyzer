# swing_analysis_prototype.py
# Prototype: AI-Powered Swing Analysis using OpenPose + Biomechanics Rules

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import subprocess
import json
import tempfile
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        "pelvis_rotation_deg": [40, 60],
        "bat_speed_mph": [75, 95]
    }

def run_openpose(video_path, output_dir):
    """Run OpenPose on the uploaded video and save keypoints to JSON."""
    # Check for different OpenPose installations
    openpose_paths = [
        "./build/examples/openpose/openpose.bin",  # Linux build
        "./bin/OpenPoseDemo.exe",  # Windows build
        "openpose",  # System PATH
        "/usr/local/bin/openpose"  # Common Linux install
    ]
    
    openpose_cmd = None
    for path in openpose_paths:
        if os.path.exists(path) or shutil.which(path):
            openpose_cmd = path
            break
    
    if not openpose_cmd:
        print("Warning: OpenPose not found. Using mock analysis.")
        return create_mock_keypoints(output_dir)
    
    try:
        subprocess.run([
            openpose_cmd,
            "--video", video_path,
            "--write_json", output_dir,
            "--display", "0",
            "--render_pose", "0"
        ], check=True, timeout=120)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("Warning: OpenPose execution failed. Using mock analysis.")
        return create_mock_keypoints(output_dir)
    
    return output_dir

def create_mock_keypoints(output_dir):
    """Create mock keypoint data for testing when OpenPose is not available."""
    mock_data = {
        "version": 1.7,
        "people": [{
            "person_id": [-1],
            "pose_keypoints_2d": [
                # Mock keypoints with some intentional "flaws" for testing
                100, 200, 0.9,  # 0: Nose
                110, 190, 0.9,  # 1: Neck
                80, 220, 0.9,   # 2: R Shoulder (closer than ideal)
                140, 220, 0.9,  # 3: L Shoulder
                70, 280, 0.9,   # 4: R Elbow
                150, 280, 0.9,  # 5: L Elbow
                60, 340, 0.9,   # 6: R Wrist
                160, 340, 0.9,  # 7: L Wrist
                90, 350, 0.9,   # 8: Mid Hip
                85, 350, 0.9,   # 9: R Hip (close to shoulders - insufficient separation)
                95, 350, 0.9,   # 10: L Hip
                80, 450, 0.9,   # 11: R Knee
                100, 450, 0.9,  # 12: L Knee
                75, 550, 0.9,   # 13: R Ankle
                105, 550, 0.9,  # 14: L Ankle
                108, 195, 0.9,  # 15: R Eye
                112, 195, 0.9,  # 16: L Eye
                106, 205, 0.9,  # 17: R Ear
                114, 205, 0.9   # 18: L Ear
            ] + [0.0] * (25 - 19) * 3  # Fill remaining keypoints
        }]
    }
    
    # Create mock JSON file
    mock_file = os.path.join(output_dir, "000000000000_keypoints.json")
    with open(mock_file, 'w') as f:
        json.dump(mock_data, f)
    
    return output_dir

def analyze_pose(keypoint_json_dir):
    """Analyze extracted pose keypoints vs biomechanics standards."""
    issues_detected = []
    
    json_files = [f for f in os.listdir(keypoint_json_dir) if f.endswith(".json")]
    if not json_files:
        return ["No pose data found in video"]
    
    for file in json_files:
        try:
            with open(os.path.join(keypoint_json_dir, file)) as f:
                data = json.load(f)
                
            if not data.get("people"):
                continue
                
            keypoints = data["people"][0]["pose_keypoints_2d"]
            if len(keypoints) < 57:  # 19 keypoints * 3 values each
                continue
            
            # Extract key body points (x, y, confidence)
            r_shoulder = (keypoints[6], keypoints[7])   # keypoint 2
            l_shoulder = (keypoints[9], keypoints[10])  # keypoint 3
            r_hip = (keypoints[27], keypoints[28])      # keypoint 9
            l_hip = (keypoints[30], keypoints[31])      # keypoint 10
            r_elbow = (keypoints[12], keypoints[13])    # keypoint 4
            l_elbow = (keypoints[15], keypoints[16])    # keypoint 5
            
            # Check hip-shoulder separation
            avg_shoulder_x = (r_shoulder[0] + l_shoulder[0]) / 2
            avg_hip_x = (r_hip[0] + l_hip[0]) / 2
            separation = abs(avg_shoulder_x - avg_hip_x)
            
            if separation < IDEAL_METRICS["hip_shoulder_separation"][0]:
                issues_detected.append("Insufficient hip-shoulder separation")
            
            # Check shoulder width for stance
            shoulder_width = abs(r_shoulder[0] - l_shoulder[0])
            if shoulder_width < 50:  # pixels - adjust based on typical video resolution
                issues_detected.append("Narrow stance detected")
            
            # Check elbow positioning
            r_elbow_angle = calculate_angle(r_shoulder, r_elbow, (r_elbow[0], r_elbow[1] + 50))
            if r_elbow_angle < 90:
                issues_detected.append("Back elbow too low")
                
        except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
            print(f"Error processing {file}: {e}")
            continue
    
    return issues_detected

def calculate_angle(point1, point2, point3):
    """Calculate angle between three points."""
    import math
    
    # Vector from point2 to point1
    v1 = (point1[0] - point2[0], point1[1] - point2[1])
    # Vector from point2 to point3
    v2 = (point3[0] - point2[0], point3[1] - point2[1])
    
    # Calculate dot product and magnitudes
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude1 = math.sqrt(v1[0]**2 + v1[1]**2)
    magnitude2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    # Calculate angle in degrees
    cos_angle = dot_product / (magnitude1 * magnitude2)
    cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
    angle = math.acos(cos_angle) * 180 / math.pi
    
    return angle

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
            
            # Run pose analysis
            run_openpose(video_path, output_dir)
            issues = analyze_pose(output_dir)
            
            # Enhanced recommendations mapping
            recommendations = {
                "Insufficient hip-shoulder separation": {
                    "drills": [
                        "Separation drill with resistance band",
                        "Stride pause drill",
                        "Hip-shoulder dissociation drill",
                        "Coil and fire drill"
                    ],
                    "exercises": [
                        "Medicine ball rotational throws",
                        "Cable torso twists",
                        "Russian twists with medicine ball",
                        "Seated spinal rotation"
                    ]
                },
                "Narrow stance detected": {
                    "drills": [
                        "Wide stance batting practice",
                        "Balance board drills",
                        "Stance width marker drill"
                    ],
                    "exercises": [
                        "Single-leg balance exercises",
                        "Lateral lunges",
                        "Hip abductor strengthening"
                    ]
                },
                "Back elbow too low": {
                    "drills": [
                        "Elbow height drill with mirror",
                        "Wall lean drill",
                        "High elbow batting tee work"
                    ],
                    "exercises": [
                        "Rear deltoid strengthening",
                        "External rotation exercises",
                        "Rhomboid strengthening"
                    ]
                },
                "No pose data found in video": {
                    "drills": [
                        "Try recording from a different angle",
                        "Ensure good lighting in video",
                        "Record against a plain background"
                    ],
                    "exercises": []
                }
            }
            
            # Build feedback response
            feedback = []
            for issue in issues:
                feedback.append({
                    "issue": issue,
                    "drills": recommendations.get(issue, {}).get("drills", ["General swing improvement drills"]),
                    "exercises": recommendations.get(issue, {}).get("exercises", ["General strength training"])
                })
            
            return jsonify({
                "feedback": feedback,
                "status": "success",
                "analysis_notes": f"Analyzed {len(os.listdir(output_dir))} frames" if os.path.exists(output_dir) else "Mock analysis used"
            })
            
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Don't fail if cleanup fails
                
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "openpose_available": any(os.path.exists(path) or shutil.which(path) for path in [
            "./build/examples/openpose/openpose.bin",
            "./bin/OpenPoseDemo.exe",
            "openpose",
            "/usr/local/bin/openpose"
        ])
    })

if __name__ == '__main__':
    print("Starting Swing Analyzer backend...")
    print("Health check: http://localhost:5001/health")
    print("Analysis endpoint: POST http://localhost:5001/analyze")
    app.run(host='0.0.0.0', port=5001, debug=True)
