import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { AlertCircle, Upload, Activity, Target, Dumbbell, BarChart3, Clock, Zap, Eye } from 'lucide-react';

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
          3D AI Swing Analyzer
        </h1>
        <p className="text-gray-600">
          Upload your swing video for advanced 3D biomechanical analysis, kinematic sequence evaluation, and personalized feedback
        </p>
        <div className="flex justify-center gap-4 mt-3 text-sm text-blue-600">
          <span className="flex items-center gap-1">
            <Zap className="h-4 w-4" />
            3D Pose Estimation
          </span>
          <span className="flex items-center gap-1">
            <BarChart3 className="h-4 w-4" />
            Kinematic Analysis
          </span>
          <span className="flex items-center gap-1">
            <Eye className="h-4 w-4" />
            Interactive Visualizations
          </span>
        </div>
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
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">3D Analysis Results</h2>
            {results.analysis_type && (
              <span className="text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                {results.analysis_type}
              </span>
            )}
          </div>

          {/* Performance Scores */}
          {results.performance_scores && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-800">
                  <BarChart3 className="h-5 w-5" />
                  Performance Scores
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(results.performance_scores).map(([key, value]) => (
                    <div key={key} className="text-center">
                      <div className="text-2xl font-bold text-blue-800">
                        {typeof value === 'number' ? Math.round(value) : value}
                        {typeof value === 'number' && '%'}
                      </div>
                      <div className="text-sm text-blue-600 capitalize">
                        {key.replace(/_/g, ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Kinematic Sequence */}
          {results.kinematic_sequence && Object.keys(results.kinematic_sequence).length > 0 && (
            <Card className="border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-800">
                  <Zap className="h-5 w-5" />
                  Kinematic Sequence Analysis
                </CardTitle>
                <CardDescription className="text-purple-700">
                  Ground-up power generation sequence
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {results.kinematic_sequence.energy_transfer && (
                    <div className="text-center">
                      <div className="text-lg font-semibold text-purple-800 capitalize">
                        {results.kinematic_sequence.energy_transfer}
                      </div>
                      <div className="text-sm text-purple-600">Energy Transfer</div>
                    </div>
                  )}
                  {results.kinematic_sequence.sequence_efficiency && (
                    <div className="text-center">
                      <div className="text-lg font-semibold text-purple-800">
                        {Math.round(results.kinematic_sequence.sequence_efficiency)}%
                      </div>
                      <div className="text-sm text-purple-600">Sequence Efficiency</div>
                    </div>
                  )}
                  {results.kinematic_sequence.hip_initiation_time !== undefined && (
                    <div className="text-center">
                      <div className="text-lg font-semibold text-purple-800">
                        Frame {results.kinematic_sequence.hip_initiation_time}
                      </div>
                      <div className="text-sm text-purple-600">Hip Initiation</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Temporal Analysis */}
          {results.temporal_analysis && Object.keys(results.temporal_analysis).length > 0 && (
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-800">
                  <Clock className="h-5 w-5" />
                  Timing Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {results.temporal_analysis.total_swing_time && (
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-800">
                        {results.temporal_analysis.total_swing_time.toFixed(2)}s
                      </div>
                      <div className="text-sm text-green-600">Total Swing Time</div>
                    </div>
                  )}
                  {results.temporal_analysis.acceleration_phase_duration && (
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-800">
                        {results.temporal_analysis.acceleration_phase_duration.toFixed(2)}s
                      </div>
                      <div className="text-sm text-green-600">Acceleration Phase</div>
                    </div>
                  )}
                  {results.temporal_analysis.deceleration_phase_duration && (
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-800">
                        {results.temporal_analysis.deceleration_phase_duration.toFixed(2)}s
                      </div>
                      <div className="text-sm text-green-600">Deceleration Phase</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Visualizations */}
          {results.visualizations && Object.keys(results.visualizations).length > 0 && (
            <Card className="border-indigo-200 bg-indigo-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-indigo-800">
                  <Eye className="h-5 w-5" />
                  3D Visualizations
                </CardTitle>
                <CardDescription className="text-indigo-700">
                  Interactive 3D analysis plots and trajectory visualizations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {results.visualizations.swing_analysis_plot && (
                    <div className="text-center">
                      <Button
                        variant="outline"
                        onClick={() => window.open(`http://localhost:5001${results.visualizations.swing_analysis_plot}`, '_blank')}
                        className="w-full"
                      >
                        <BarChart3 className="h-4 w-4 mr-2" />
                        View 3D Analysis Plot
                      </Button>
                    </div>
                  )}
                  {results.visualizations.interactive_3d && (
                    <div className="text-center">
                      <Button
                        variant="outline"
                        onClick={() => window.open(`http://localhost:5001${results.visualizations.interactive_3d}`, '_blank')}
                        className="w-full"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View Interactive 3D
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
          
          {/* Feedback Section */}
          {results.feedback && results.feedback.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Detailed Feedback & Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {results.feedback.map((item, index) => (
                    <Card key={index} className="border-orange-200 bg-orange-50">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-orange-800">
                          <AlertCircle className="h-5 w-5" />
                          {item.category || 'Issue Detected'}
                        </CardTitle>
                        <CardDescription className="text-orange-700">
                          {item.issue}
                        </CardDescription>
                        {item.technical_focus && (
                          <div className="text-sm text-orange-600 font-medium mt-2">
                            Focus: {item.technical_focus}
                          </div>
                        )}
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
              </CardContent>
            </Card>
          ) : (
            <Card className="border-green-200 bg-green-50">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-green-800">
                  <Target className="h-5 w-5" />
                  <span className="font-semibold">Excellent swing mechanics!</span>
                </div>
                <p className="text-green-700 mt-2">
                  Your 3D biomechanical analysis shows optimal swing characteristics. Keep up the outstanding work!
                </p>
              </CardContent>
            </Card>
          )}

          {/* Analysis Notes */}
          {results.analysis_notes && (
            <div className="text-sm text-gray-600 text-center italic">
              {results.analysis_notes}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SwingAnalyzer;