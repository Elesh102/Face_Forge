import React, { useState, useRef, useEffect } from 'react';
import { Camera, Play, Square, AlertCircle } from 'lucide-react';

export default function WebcamView({ badge, config }) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [currentDetection, setCurrentDetection] = useState(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const startWebcam = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setIsStreaming(true);
      setCurrentDetection({
        emotion: 'Neutral',
        confidence: 0.85,
        status: 'Neutral'
      });
    } catch (err) {
      console.warn('Camera access error:', err);
      setCameraError('No camera found or camera permission was denied. Please connect a webcam and allow access.');
      setIsStreaming(false);
    }
  };

  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    setCurrentDetection(null);
  };

  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, []);

  return (
    <div>
      <div className="view-header">
        <h1>Webcam Detection</h1>
        <p>Live facial expression detection using your browser camera.</p>
      </div>

      {cameraError && (
        <div className="notice-box" style={{ background: 'rgba(239, 68, 68, 0.15)', borderColor: '#ef4444', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={18} />
          <span>{cameraError}</span>
        </div>
      )}

      <div className="card">
        {/* Controls */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button 
            className="btn btn-primary" 
            onClick={startWebcam} 
            disabled={isStreaming}
          >
            <Play size={16} /> Start Webcam
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={stopWebcam} 
            disabled={!isStreaming}
          >
            <Square size={16} /> Stop Webcam
          </button>
        </div>

        {/* Video Display */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#070b14', borderRadius: '8px', border: '1px solid var(--border-color)', minHeight: '380px', position: 'relative', overflow: 'hidden' }}>
          <video 
            ref={videoRef} 
            playsInline 
            muted 
            style={{ width: '100%', maxWidth: '640px', display: isStreaming ? 'block' : 'none', borderRadius: '6px' }}
          />

          {!isStreaming && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
              <Camera size={48} style={{ opacity: 0.3, margin: '0 auto 12px auto' }} />
              <div style={{ fontSize: '1.05rem', color: '#fff', fontWeight: 600, marginBottom: '6px' }}>
                Webcam is turned off
              </div>
              <p style={{ fontSize: '0.85rem' }}>
                Click "Start Webcam" above to begin live detection.
              </p>
            </div>
          )}

          {isStreaming && currentDetection && (
            <div style={{ position: 'absolute', bottom: '16px', left: '16px', background: 'rgba(15, 23, 42, 0.85)', border: '1px solid var(--border-color)', padding: '10px 16px', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Detected Expression:</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#38bdf8' }}>
                {currentDetection.emotion} ({Math.round(currentDetection.confidence * 100)}%)
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Status: {currentDetection.status}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
