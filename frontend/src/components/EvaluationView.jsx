import React, { useState } from 'react';
import { 
  FileCheck2, 
  Grid, 
  FileText, 
  RefreshCw, 
  Activity,
  Sliders,
  Download,
  Sparkles,
  Layers,
  Inbox
} from 'lucide-react';

export default function EvaluationView({ badge, triggerToast }) {
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [benchmarkDataset, setBenchmarkDataset] = useState('fer2013');

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      triggerToast?.('Evaluation Scan', 'Diagnostic files refreshed. No active evaluation artifacts found.');
    }, 600);
  };

  const handleRunEvaluation = () => {
    triggerToast?.('Evaluation Benchmark', 'Validation benchmark triggered on test dataset.');
  };

  return (
    <div>
      {/* Header */}
      <div className="view-header">
        <div>
          <h1>
            <Activity size={28} color="#a855f7" style={{ filter: 'drop-shadow(0 0 10px #a855f7)' }} />
            <span>Neural Diagnostics & Model Benchmark Evaluation</span>
          </h1>
          <p>
            Validation confusion matrix, precision-recall curve metrics, and benchmark test reports.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            className="btn btn-secondary" 
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Refresh Files</span>
          </button>

          <button 
            className="btn btn-primary"
            onClick={handleRunEvaluation}
          >
            <Activity size={14} />
            <span>Re-evaluate Matrix</span>
          </button>
        </div>
      </div>

      {/* Benchmark Selector Dropout */}
      <div className="card" style={{ padding: '16px 20px', border: '1px solid rgba(168, 85, 247, 0.25)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={16} color="#a855f7" />
            <strong style={{ color: '#fff', fontSize: '0.9rem' }}>Evaluation Benchmark & Validation Split</strong>
          </div>
          <span className="card-badge" style={{ borderColor: 'rgba(168, 85, 247, 0.3)', color: '#c084fc' }}>
            Model Validation
          </span>
        </div>

        <div className="grid-3">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Benchmark Test Split</label>
            <div className="select-wrapper">
              <select 
                className="form-control"
                value={benchmarkDataset}
                onChange={(e) => {
                  setBenchmarkDataset(e.target.value);
                  triggerToast?.('Dataset Swapped', `Evaluation targeted to ${e.target.options[e.target.selectedIndex].text}`);
                }}
              >
                <option value="fer2013">FER-2013 Public Test Set (3,589 images)</option>
                <option value="affectnet">AffectNet Real-World Wild Split</option>
                <option value="ckplus">CK+ Laboratory Controlled Benchmark</option>
              </select>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Target Metric</label>
            <div className="select-wrapper">
              <select className="form-control">
                <option>Macro F1-Score & Accuracy</option>
                <option>Top-1 / Top-2 Categorical Accuracy</option>
                <option>Receiver Operating Characteristic (ROC)</option>
              </select>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Batch Normalization</label>
            <div className="select-wrapper">
              <select className="form-control">
                <option>Standard Scaler (0-1 min-max)</option>
                <option>Z-Score Zero-Mean Normalization</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Confusion Matrix & Metrics Report */}
      <div className="grid-2">
        {/* Confusion Matrix Card (Empty State) */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 className="card-title" style={{ marginBottom: 0 }}>
              <Grid size={18} color="var(--cyan)" />
              <span>Confusion Matrix Heatmap</span>
            </h3>
            <span className="card-badge">7x7 Grid</span>
          </div>

          <div style={{ padding: '60px 20px', textAlign: 'center', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-subtle)' }}>
            <Grid size={44} style={{ opacity: 0.3, color: 'var(--cyan)', margin: '0 auto 12px auto' }} />
            <div style={{ fontSize: '1rem', color: '#fff', fontWeight: 600, marginBottom: '6px' }}>
              No Confusion Matrix Data
            </div>
            <p style={{ fontSize: '0.82rem', maxWidth: '320px', margin: '0 auto', lineHeight: '1.5' }}>
              Confusion matrix heatmap will render here when a model evaluation cycle is completed.
            </p>
          </div>
        </div>

        {/* Classification Report Card (Empty State) */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 className="card-title" style={{ marginBottom: 0 }}>
              <FileText size={18} color="var(--primary)" />
              <span>Metrics Classification Report</span>
            </h3>
            <span className="card-badge">F1 / Recall</span>
          </div>

          <div style={{ padding: '60px 20px', textAlign: 'center', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-subtle)' }}>
            <FileCheck2 size={44} style={{ opacity: 0.3, color: 'var(--primary)', margin: '0 auto 12px auto' }} />
            <div style={{ fontSize: '1rem', color: '#fff', fontWeight: 600, marginBottom: '6px' }}>
              No Classification Report
            </div>
            <p style={{ fontSize: '0.82rem', maxWidth: '320px', margin: '0 auto', lineHeight: '1.5' }}>
              Precision, recall, and support metrics will be parsed and formatted here upon evaluation.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
            <button 
              className="btn btn-outline" 
              style={{ flex: 1 }}
              onClick={() => triggerToast?.('Report Exported', 'Evaluation metrics summary saved to PDF.')}
            >
              <Download size={14} /> Export Metrics Summary
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
