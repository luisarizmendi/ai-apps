'use client'; 

import React, { useState, useRef, useEffect } from 'react';
import { Upload, Camera, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Image from 'next/image';

const DetectionApp = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [results, setResults] = useState<{ filename: string, image_base64: string, object_counts: Record<string, number> }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const videoRef = useRef(null);
  //const [streamResults, setStreamResults] = useState(null);
  const [processingTime, setProcessingTime] = useState(null);
  
  // Get available cameras
  useEffect(() => {
    const getDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        setDevices(videoDevices);
        if (videoDevices.length > 0) {
          setSelectedDevice(videoDevices[0].deviceId);  
        }
      } catch {
        setError('Failed to get camera devices');
      }
    };
    getDevices();
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const processImages = async () => {
    setIsProcessing(true);
    setError(null);
    const startTime = performance.now();

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('images', file);
      });

      const response = await fetch('http://localhost:5000/detect_batch', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Detection failed');

      const data = await response.json();
      setResults(data.results);
      setProcessingTime((performance.now() - startTime) / 1000);
    } catch {
      setError('An error occurred while processing the images');
    } finally {
      setIsProcessing(false);
    }
  };

  const startStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: selectedDevice }
      });
      videoRef.current.srcObject = stream;
      setIsStreaming(true);
    } catch  {
      setError('Failed to start camera stream');
    }
  };

  const stopStream = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Object Detection App</h1>
        
        {/* Tab Selection */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'upload' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'
            }`}
          >
            <Upload className="inline-block mr-2 h-5 w-5" />
            Upload Images
          </button>
          <button
            onClick={() => setActiveTab('stream')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'stream' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'
            }`}
          >
            <Camera className="inline-block mr-2 h-5 w-5" />
            Camera Stream
          </button>
        </div>

        {/* Upload Section */}
        {activeTab === 'upload' && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center"
            >
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-600">
                  Drag and drop images here or click to select
                </p>
              </label>
            </div>

            {selectedFiles.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">Selected Files:</h3>
                <ul className="space-y-2">
                  {selectedFiles.map((file, index) => (
                    <li key={index} className="text-sm text-gray-600">
                      {file.name}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={processImages}
                  disabled={isProcessing}
                  className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                >
                  {isProcessing ? (
                    <Loader2 className="inline-block animate-spin mr-2" />
                  ) : 'Process Images'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Stream Section */}
        {activeTab === 'stream' && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <select
              value={selectedDevice}
              onChange={(e) => setSelectedDevice(e.target.value)}
              className="mb-4 p-2 border rounded"
            >
              {devices.map(device => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label || `Camera ${devices.indexOf(device) + 1}`}
                </option>
              ))}
            </select>

            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full rounded-lg"
              />
              <button
                onClick={isStreaming ? stopStream : startStream}
                className={`mt-4 px-4 py-2 rounded-lg ${
                  isStreaming ? 'bg-red-500' : 'bg-blue-500'
                } text-white`}
              >
                {isStreaming ? 'Stop Stream' : 'Start Stream'}
              </button>
            </div>
          </div>
        )}

        {/* Results Section */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {processingTime && (
          <div className="mb-4 text-sm text-gray-600">
            Processing time: {processingTime.toFixed(2)} seconds
          </div>
        )}

        {results.length > 0 && (
          <div className="space-y-8">
            {results.map((result, index) => (
              <div key={index} className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="font-medium mb-4">{result.filename}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Image
                    src={`data:image/jpeg;base64,${result.image_base64}`}
                    alt="Processed"
                    className="rounded-lg"
                  />
                  <div>
                    <h4 className="font-medium mb-2">Detected Objects:</h4>
                    <ul className="space-y-2">
                      {Object.entries(result.object_counts).map(([obj, count]) => (
                        <li key={obj} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                          <span className="capitalize">{obj}</span>
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {count}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DetectionApp;
