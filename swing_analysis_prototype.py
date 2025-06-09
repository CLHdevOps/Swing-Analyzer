from flask import Flask, request, jsonify
import os
import json
import traceback
from pose_3d_estimator import Pose3DEstimator
from biomechanics_3d_analyzer import analyze_swing_3d
import numpy as np

app = Flask(__name__)
pose_estimator = Pose3DEstimator()

# Utility to convert numpy types to native Python types
def convert_np(obj):
    if isinstance(obj, dict):
        return {k: convert_np(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np(i) for i in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    return obj

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Handle uploaded video
        if 'video' not in request.files:
            return jsonify({"error": "No video file uploaded"}), 400

        video_file = request.files['video']
        video_path = os.path.join("uploads", video_file.filename)
        os.makedirs("uploads", exist_ok=True)
        video_file.save(video_path)

        # Process video for 3D pose
        output_dir = os.path.join("outputs", os.path.splitext(video_file.filename)[0])
        os.makedirs(output_dir, exist_ok=True)

        pose_data_path = pose_estimator.process_video(
            video_path=video_path,
            output_dir=output_dir,
            frame_skip=2,
            max_frames=90
        )

        with open(pose_data_path, 'r') as f:
            pose_data = json.load(f)

        # Run biomechanical analysis
        result = analyze_swing_3d(pose_data)

        # Clean up large files if desired
        os.remove(video_path)

        # Ensure JSON-safe types before returning
        return jsonify(convert_np(result))

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
