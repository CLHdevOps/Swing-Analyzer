import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { AlertCircle, Upload, Activity, Target, Dumbbell } from 'lucide-react';

const SwingAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setError(null);
      setResults(null);
    } else {
      setError('Please select a valid video file');
    }
  };

  const analyzeSwing = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('video', file);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch('http://localhost:5001/analyze', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Swing Analyzer
        </h1>
        <p className="text-gray-600">
          Upload your swing video for biomechanical analysis and personalized feedback
        </p>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Video Upload
          </CardTitle>
          <CardDescription>
            Select a video file of your baseball or softball swing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-center w-full">
            <label
              htmlFor="video-upload"
              className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-8 h-8 mb-4 text-gray-500" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">MP4, MOV, AVI (MAX. 100MB)</p>
              </div>
              <input
                id="video-upload"
                type="file"
                className="hidden"
                accept="video/*"
                onChange={handleFileSelect}
              />
            </label>
          </div>

          {file && (
            <div className="text-sm text-gray-600">
              Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </div>
          )}

          {uploadProgress > 0 && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Upload Progress</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          )}

          <Button
            onClick={analyzeSwing}
            disabled={!file || analyzing}
            className="w-full"
          >
            {analyzing ? 'Analyzing...' : 'Analyze Swing'}
          </Button>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
          
          {results.feedback && results.feedback.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {results.feedback.map((item, index) => (
                <Card key={index} className="border-orange-200 bg-orange-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-orange-800">
                      <AlertCircle className="h-5 w-5" />
                      Issue Detected
                    </CardTitle>
                    <CardDescription className="text-orange-700">
                      {item.issue}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {item.drills && item.drills.length > 0 && (
                      <div>
                        <h4 className="flex items-center gap-2 font-semibold text-orange-800 mb-2">
                          <Activity className="h-4 w-4" />
                          Recommended Drills
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-orange-700">
                          {item.drills.map((drill, drillIndex) => (
                            <li key={drillIndex}>{drill}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {item.exercises && item.exercises.length > 0 && (
                      <div>
                        <h4 className="flex items-center gap-2 font-semibold text-orange-800 mb-2">
                          <Dumbbell className="h-4 w-4" />
                          Strengthening Exercises
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-orange-700">
                          {item.exercises.map((exercise, exerciseIndex) => (
                            <li key={exerciseIndex}>{exercise}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="border-green-200 bg-green-50">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-green-800">
                  <Target className="h-5 w-5" />
                  <span className="font-semibold">Great swing! No major issues detected.</span>
                </div>
                <p className="text-green-700 mt-2">
                  Your swing biomechanics are within ideal ranges. Keep up the good work!
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default SwingAnalyzer;