import React from 'react';
import { 
  Home as HomeIcon, 
  Image as ImageIcon, 
  Video, 
  Camera, 
  Database, 
  BarChart3, 
  Smile
} from 'lucide-react';

export default function Sidebar({ currentView, setCurrentView }) {
  // Settings and Model Evaluation hidden for now as requested
  const navItems = [
    { id: 'home', label: 'Home', icon: HomeIcon },
    { id: 'image', label: 'Image Detection', icon: ImageIcon },
    { id: 'video', label: 'Video Detection', icon: Video },
    { id: 'webcam', label: 'Webcam Detection', icon: Camera },
    { id: 'results', label: 'Results', icon: Database },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="brand-section">
        <div className="brand-title">
          <Smile size={24} color="#38bdf8" />
          <span>Face Forge</span>
        </div>
        <div className="brand-tag">
          <span>Emotion Detection System</span>
        </div>
        
        <div className="status-indicator-pill">
          <span className="pulse-dot"></span>
          <span>Ready</span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="nav-list">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              className={`nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentView(item.id)}
            >
              <Icon size={18} color={isActive ? '#38bdf8' : '#94a3b8'} />
              <span style={{ flex: 1 }}>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Clean Status Footer */}
      <div className="sidebar-telemetry">
        <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', textAlign: 'center', padding: '8px 0' }}>
          Face Forge &copy; 2026
        </div>
      </div>
    </aside>
  );
}
