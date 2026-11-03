/**
 * =============================================================================
 * FaceForge - Module 4: Sidebar Navigation Component (Sidebar.jsx)
 * Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
 * Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur
 * =============================================================================
 */

import React from 'react';
import { 
  Home as HomeIcon, 
  Image as ImageIcon, 
  Video, 
  Camera, 
  Database, 
  BarChart3, 
  Activity,
  Sliders,
  Smile
} from 'lucide-react';

export default function Sidebar({ currentView, setCurrentView }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: HomeIcon },
    { id: 'image', label: 'Image Detection', icon: ImageIcon },
    { id: 'video', label: 'Video Detection', icon: Video },
    { id: 'webcam', label: 'Webcam Detection', icon: Camera },
    { id: 'results', label: 'Results', icon: Database },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'evaluation', label: 'Model Evaluation', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Sliders },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="brand-section">
        <div className="brand-title">
          <Smile size={24} color="#4f46e5" />
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
              <Icon size={18} color={isActive ? '#4f46e5' : '#64748b'} />
              <span style={{ flex: 1 }}>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
