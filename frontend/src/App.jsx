import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import HomeView from './components/HomeView';
import ImageView from './components/ImageView';
import VideoView from './components/VideoView';
import WebcamView from './components/WebcamView';
import ResultsView from './components/ResultsView';
import AnalyticsView from './components/AnalyticsView';
import SettingsView from './components/SettingsView';
import EvaluationView from './components/EvaluationView';
import { Sparkles, Info, X } from 'lucide-react';

/**
 * =============================================================================
 * FaceForge - Module 4: React Application Root Controller (App.jsx)
 * Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
 * Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur
 *
 * Responsibilities of Member 4:
 * - Manages active navigation views (Home, Image, Video, Webcam, Results, Analytics, Evaluation, Settings)
 * - Coordinates configuration state with backend (/api/config)
 * - Global system status monitoring and user notifications
 * =============================================================================
 */

export default function App() {
  const [currentView, setCurrentView] = useState('home');
  const [config, setConfig] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [badge, setBadge] = useState({ text: 'Ready', type: 'live', desc: 'Module 4 pipeline ready' });
  const [resultsRefreshTick, setResultsRefreshTick] = useState(0);

  // Notification toast state
  const [toast, setToast] = useState(null);

  const triggerToast = (title, message) => {
    setToast({ title, message, id: Date.now() });
  };

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        setToast(null);
      }, 4200);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const fetchSystemStatus = async () => {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        setStatusData(data);
      }

      const cfgRes = await fetch('/api/config');
      if (cfgRes.ok) {
        const cfg = await cfgRes.json();
        setConfig(cfg);
      }
    } catch (e) {
      console.warn('Backend connection pending or offline:', e);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const handleConfigUpdated = (newConfig, newBadge) => {
    setConfig(newConfig);
    if (newBadge) setBadge(newBadge);
    fetchSystemStatus();
  };

  const handleResultSaved = () => {
    setResultsRefreshTick(prev => prev + 1);
  };

  return (
    <div className="app-container">
      <Sidebar 
        currentView={currentView} 
        setCurrentView={setCurrentView} 
        triggerToast={triggerToast}
      />

      <main className="main-content">
        {currentView === 'home' && (
          <HomeView 
            setCurrentView={setCurrentView} 
            badge={badge} 
            statusData={statusData}
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'image' && (
          <ImageView 
            badge={badge} 
            onResultSaved={handleResultSaved} 
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'video' && (
          <VideoView 
            badge={badge} 
            config={config} 
            onResultSaved={handleResultSaved} 
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'webcam' && (
          <WebcamView 
            badge={badge} 
            config={config} 
            statusData={statusData} 
            onResultSaved={handleResultSaved} 
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'results' && (
          <ResultsView 
            badge={badge} 
            key={resultsRefreshTick} 
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'analytics' && (
          <AnalyticsView 
            badge={badge} 
            key={resultsRefreshTick} 
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'settings' && (
          <SettingsView 
            badge={badge} 
            config={config} 
            onConfigUpdated={handleConfigUpdated} 
            triggerToast={triggerToast}
          />
        )}

        {currentView === 'evaluation' && (
          <EvaluationView 
            badge={badge} 
            triggerToast={triggerToast}
          />
        )}
      </main>

      {/* Feedback Toast Notification */}
      {toast && (
        <div className="toast-container">
          <div className="toast">
            <Sparkles size={20} color="#06b6d4" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-primary)', marginBottom: '2px' }}>
                {toast.title}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                {toast.message}
              </div>
            </div>
            <button 
              onClick={() => setToast(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}
            >
              <X size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
