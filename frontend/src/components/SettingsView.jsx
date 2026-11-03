/**
 * =============================================================================
 * FaceForge - Module 4: Settings & Feature Flags Panel (SettingsView.jsx)
 * Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
 * Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur
 *
 * Responsibilities of Member 4:
 * - Feature flag controls for plugging/unplugging Module 1, 2, and 3
 * - Tuning confidence threshold and video sampling frequency
 * =============================================================================
 */

import React, { useState } from 'react';
import { Sliders, Save, CheckCircle2 } from 'lucide-react';

export default function SettingsView({ config, onConfigUpdated }) {
  const [formData, setFormData] = useState({
    demo_mode: config?.demo_mode ?? true,
    use_module1: config?.use_module1 ?? false,
    use_module2: config?.use_module2 ?? false,
    use_module3: config?.use_module3 ?? false,
    confidence_threshold: config?.confidence_threshold ?? 0.50,
    video_sampling_step: config?.video_sampling_step ?? 10
  });

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleToggle = (key) => {
    setFormData(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);

    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        const data = await res.json();
        setSaveSuccess(true);
        if (onConfigUpdated) onConfigUpdated(data.config, data.badge);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Failed to save settings:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="view-header">
        <h1>Settings</h1>
        <p>Edit system parameters and feature flags stored in config.yaml.</p>
      </div>

      {saveSuccess && (
        <div className="notice-box notice-success" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={16} />
          <span>Settings saved successfully.</span>
        </div>
      )}

      <form onSubmit={handleSave}>
        <div className="card" style={{ maxWidth: '640px' }}>
          <h3 className="card-title">
            <Sliders size={18} color="var(--primary)" />
            <span>Configuration Parameters</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Demo Mode */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
              <div>
                <strong style={{ color: 'var(--text-primary)' }}>Demo Mode</strong>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Use mock adapter data</div>
              </div>
              <input 
                type="checkbox" 
                checked={formData.demo_mode}
                onChange={() => handleToggle('demo_mode')}
                style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
              />
            </div>

            {/* Module 1 Switch */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
              <div>
                <strong style={{ color: 'var(--text-primary)' }}>Module 1 (Preprocessing)</strong>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Enable Module 1 adapter</div>
              </div>
              <input 
                type="checkbox" 
                checked={formData.use_module1}
                onChange={() => handleToggle('use_module1')}
                style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
              />
            </div>

            {/* Module 2 Switch */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
              <div>
                <strong style={{ color: 'var(--text-primary)' }}>Module 2 (Face Detection)</strong>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Enable Module 2 adapter</div>
              </div>
              <input 
                type="checkbox" 
                checked={formData.use_module2}
                onChange={() => handleToggle('use_module2')}
                style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
              />
            </div>

            {/* Module 3 Switch */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
              <div>
                <strong style={{ color: 'var(--text-primary)' }}>Module 3 (Emotion Model)</strong>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Enable Module 3 adapter</div>
              </div>
              <input 
                type="checkbox" 
                checked={formData.use_module3}
                onChange={() => handleToggle('use_module3')}
                style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
              />
            </div>

            {/* Confidence Threshold */}
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label">Confidence Threshold</label>
                <strong style={{ color: 'var(--primary)' }}>{formData.confidence_threshold}</strong>
              </div>
              <input 
                type="range" 
                min="0.1" 
                max="0.95" 
                step="0.05"
                value={formData.confidence_threshold}
                onChange={(e) => setFormData(prev => ({ ...prev, confidence_threshold: parseFloat(e.target.value) }))}
                style={{ width: '100%' }}
              />
            </div>

            {/* Video Sampling Step */}
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label">Video Sampling Step</label>
                <strong style={{ color: 'var(--primary)' }}>Every {formData.video_sampling_step} frames</strong>
              </div>
              <input 
                type="range" 
                min="1" 
                max="30" 
                step="1"
                value={formData.video_sampling_step}
                onChange={(e) => setFormData(prev => ({ ...prev, video_sampling_step: parseInt(e.target.value, 10) }))}
                style={{ width: '100%' }}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '8px' }} disabled={saving}>
              <Save size={16} /> {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
