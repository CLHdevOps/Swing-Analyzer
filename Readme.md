# Swing Analysis App

A prototype application that analyzes baseball or softball swings using OpenPose and biomechanics data. The app processes an uploaded video, extracts pose data, compares the swing against ideal biomechanics, and returns feedback including recommended drills and exercises.

## 🔧 Features

- 📹 **Video Upload**: Users can upload swing videos via the frontend.
- 🧍 **Pose Extraction**: Backend uses OpenPose to extract 2D keypoints.
- 📊 **Biomechanics Comparison**: JSON-based rules compare user swing to ideal form.
- 🧠 **Feedback Engine**: Detects flaws and maps them to swing drills and muscle exercises.
- ⚛️ **Frontend**: Built in React with shadcn/ui components for clean display.

## 📁 Project Structure

```
Swing Analyzer/
├── swing_analysis_prototype.py         # Flask backend with OpenPose integration
├── biomechanics_ideal.json            # Biomechanical standards and thresholds
├── requirements.txt                   # Python dependencies
├── frontend/                          # Complete React frontend
│   ├── package.json                  # Frontend dependencies
│   ├── vite.config.js               # Vite configuration
│   ├── tailwind.config.js           # Tailwind CSS config
│   ├── postcss.config.js            # PostCSS config
│   ├── index.html                   # HTML entry point
│   └── src/
│       ├── main.jsx                 # React entry point
│       ├── App.jsx                  # Main app component
│       ├── index.css                # Global styles with Tailwind
│       ├── lib/
│       │   └── utils.js             # Utility functions
│       └── components/
│           ├── SwingAnalyzer.jsx    # Main analysis component
│           └── ui/                  # Reusable UI components
│               ├── card.jsx
│               ├── button.jsx
│               └── progress.jsx
├── .gitignore                        # Git ignore patterns
└── README.md
```

## 🚀 How to Run

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenPose (optional - app will use mock analysis if not available)

### Backend Setup
1. Install Python dependencies:
```bash
cd "Swing Analyzer"
pip install -r requirements.txt
```

2. Run the Flask backend:
```bash
python swing_analysis_prototype.py
```

The backend will start on `http://localhost:5001` with these endpoints:
- `GET /health` - Health check and OpenPose availability
- `POST /analyze` - Video analysis endpoint

### Frontend Setup
1. Navigate to frontend directory and install dependencies:
```bash
cd "Swing Analyzer/frontend"
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Usage
1. Start both backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Upload a swing video (MP4, MOV, AVI up to 100MB)
4. Click "Analyze Swing" to get biomechanical feedback
5. Review detected issues and recommended drills/exercises

---

## ✅ Completed Work
- OpenPose API created with Flask
- Biomechanics-based swing fault detection (hip-shoulder separation sample)
- Drill/exercise feedback mapping in backend
- React frontend with file upload and result cards
- Error handling and graceful UI messaging

---

## 💡 Future Improvements

- 🔍 **More Biomechanical Metrics**
  - Add ideal ranges for shoulder angle, elbow flexion, stride timing, bat speed, etc.

- 🧠 **Machine Learning Model**
  - Use LSTM or ST-GCN to classify swing errors from sequences

- 🎥 **Video Annotation**
  - Draw keypoints or error labels directly onto swing frames

- 📱 **Mobile Support**
  - Build companion mobile app with camera capture & upload

- 💬 **Natural Language Feedback**
  - Use Codex/GPT-4 to explain what’s wrong and how to fix it conversationally

- 📈 **Progress Tracker**
  - Save historical swing reports to track improvements over time

- 👥 **Multi-Athlete Support**
  - Tag and filter reports by player (e.g., Landyn Hughes #15)

---

## 🙌 Credits
- OpenPose by CMU Perceptual Computing Lab
- UI built with [shadcn/ui](https://ui.shadcn.com)

---

## 🧪 Sample JSON Structure (Ideal Metrics)
```json
{
  "hip_shoulder_separation": [30, 60],
  "pelvis_rotation_deg": [40, 60],
  "bat_speed_mph": [75, 95]
}
```

Feel free to contribute or extend it into a production-grade swing diagnostic tool!
