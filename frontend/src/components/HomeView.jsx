import React from 'react';
import { 
  ArrowRight, 
  Image as ImageIcon, 
  Video, 
  Camera, 
  Database, 
  BarChart3, 
  Play
} from 'lucide-react';

export default function HomeView({ setCurrentView }) {
  return (
    <div>
      {/* Page Header */}
      <div className="view-header" style={{ marginBottom: '32px' }}>
        <div>
          <h1>Face Forge: Emotion Detection System</h1>
          <p>
            Real-time detected expression analysis from Image, Video, and Live Webcam.
          </p>
        </div>

        <div>
          <button 
            className="btn btn-primary"
            onClick={() => setCurrentView('image')}
            style={{ padding: '10px 20px', fontSize: '0.95rem' }}
          >
            <Play size={16} />
            <span>Start Detection</span>
          </button>
        </div>
      </div>

      {/* Three Primary Detection Cards */}
      <div className="grid-3" style={{ marginBottom: '30px' }}>
        {/* Card 1: Image Detection */}
        <div 
          className="card" 
          style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
          onClick={() => setCurrentView('image')}
        >
          <div>
            <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px', color: 'var(--primary)' }}>
              <ImageIcon size={26} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '8px' }}>Image Detection</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: '1.5', marginBottom: '20px' }}>
              Upload JPG or PNG photos to detect faces, render bounding boxes, and display detected expressions with confidence scores.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--primary)', fontWeight: 600, fontSize: '0.88rem' }}>
            <span>Open Image Detection</span>
            <ArrowRight size={16} />
          </div>
        </div>

        {/* Card 2: Video Detection */}
        <div 
          className="card" 
          style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
          onClick={() => setCurrentView('video')}
        >
          <div>
            <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px', color: 'var(--cyan)' }}>
              <Video size={26} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '8px' }}>Video Detection</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: '1.5', marginBottom: '20px' }}>
              Upload MP4 or AVI video clips. Configure frame sampling step to analyze detected expressions across frames.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--cyan)', fontWeight: 600, fontSize: '0.88rem' }}>
            <span>Open Video Detection</span>
            <ArrowRight size={16} />
          </div>
        </div>

        {/* Card 3: Webcam Detection */}
        <div 
          className="card" 
          style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
          onClick={() => setCurrentView('webcam')}
        >
          <div>
            <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px', color: 'var(--emerald)' }}>
              <Camera size={26} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '8px' }}>Webcam Detection</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: '1.5', marginBottom: '20px' }}>
              Connect your browser camera for live facial detection and continuous detected expression classification.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontWeight: 600, fontSize: '0.88rem' }}>
            <span>Open Webcam Detection</span>
            <ArrowRight size={16} />
          </div>
        </div>
      </div>

      {/* Secondary Management Links (Results & Analytics) */}
      <div className="grid-2">
        <div 
          className="stat-box" 
          style={{ cursor: 'pointer', background: 'rgba(15, 23, 42, 0.6)' }}
          onClick={() => setCurrentView('results')}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Database size={20} color="var(--primary)" />
            <strong style={{ color: '#fff', fontSize: '0.95rem' }}>Results History</strong>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
            View logged predictions in results.csv, filter by source or emotion, and download CSV.
          </p>
        </div>

        <div 
          className="stat-box" 
          style={{ cursor: 'pointer', background: 'rgba(15, 23, 42, 0.6)' }}
          onClick={() => setCurrentView('analytics')}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <BarChart3 size={20} color="var(--cyan)" />
            <strong style={{ color: '#fff', fontSize: '0.95rem' }}>Analytics & Charts</strong>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
            Explore expression distribution, average confidence, and detection timelines.
          </p>
        </div>
      </div>
    </div>
  );
}
