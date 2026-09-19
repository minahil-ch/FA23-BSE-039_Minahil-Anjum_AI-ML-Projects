/**
 * AI Weekly Reports Page
 *
 * Generates operational reports aggregating tasks, tickets, documents, and AI activity.
 * Reports are created asynchronously via Celery.
 */
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  FileBarChart, Plus, Loader2, CheckCircle, XCircle, Clock, Download, AlertCircle
} from 'lucide-react';

const STATUS_BADGE = {
  PENDING: { color: 'warning', icon: Clock, label: 'Pending' },
  GENERATING: { color: 'info', icon: Loader2, label: 'Generating' },
  COMPLETED: { color: 'success', icon: CheckCircle, label: 'Completed' },
  FAILED: { color: 'danger', icon: XCircle, label: 'Failed' },
};

const AIReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const loadReports = async () => {
    try {
      const res = await api.get('ai/reports/');
      const data = res.data.results || res.data;
      setReports(data);
      // Auto-refresh if any report is still generating
      if (data.some(r => ['PENDING', 'GENERATING'].includes(r.status))) {
        setTimeout(loadReports, 3000);
      }
    } catch (e) {
      setError('Failed to load reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadReports(); }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError('');
    try {
      const res = await api.post('ai/reports/', {});
      setReports([res.data, ...reports]);
      // Poll until complete
      setTimeout(loadReports, 2000);
    } catch (e) {
      setError('Failed to queue report generation.');
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = (report) => {
    const blob = new Blob([report.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.title.replace(/\s+/g, '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title d-flex align-items-center gap-2">
            <FileBarChart className="text-primary" size={28} />
            AI Report Generator
          </h2>
          <p className="text-muted mb-0">Weekly operational reports powered by AI — tasks, tickets, documents, AI usage.</p>
        </div>
        <button onClick={handleGenerate} className="btn glow-btn py-2 px-4 rounded-3 d-flex align-items-center gap-2" disabled={generating}>
          {generating ? <Loader2 size={16} className="spin-slow" /> : <Plus size={16} />}
          Generate Report
        </button>
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 text-danger mb-3 py-2 px-3 rounded-3">
          <AlertCircle size={16} className="me-2" />{error}
        </div>
      )}

      <div className="row g-4">
        {/* Report list */}
        <div className="col-12 col-lg-4">
          <div className="glass-card p-3">
            <h6 className="text-white mb-3 font-title">Generated Reports</h6>
            {loading ? (
              <div className="text-center py-4"><Loader2 className="spin-slow text-primary" /></div>
            ) : reports.length === 0 ? (
              <p className="text-muted small">No reports yet. Click "Generate Report" to create one.</p>
            ) : (
              reports.map(r => {
                const badge = STATUS_BADGE[r.status] || STATUS_BADGE.PENDING;
                const Icon = badge.icon;
                return (
                  <button
                    key={r.id}
                    onClick={() => setSelectedReport(r)}
                    className="btn w-100 text-start mb-2 p-3 rounded-3"
                    style={{
                      background: selectedReport?.id === r.id ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.08)',
                    }}
                  >
                    <div className="text-white small fw-semibold">{r.title}</div>
                    <div className="d-flex align-items-center gap-2 mt-1">
                      <span className={`badge text-${badge.color} bg-${badge.color} bg-opacity-10`}>
                        <Icon size={10} className="me-1" />{badge.label}
                      </span>
                      <small className="text-muted">{new Date(r.created_at).toLocaleDateString()}</small>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Report preview */}
        <div className="col-12 col-lg-8">
          <div className="glass-card p-4" style={{ minHeight: '400px' }}>
            {!selectedReport ? (
              <div className="text-center text-muted py-5">
                <FileBarChart size={48} className="mb-3 text-primary opacity-50" />
                <p>Select a report to preview its content.</p>
              </div>
            ) : selectedReport.status !== 'COMPLETED' ? (
              <div className="text-center py-5">
                <Loader2 size={32} className="spin-slow text-primary mb-3" />
                <p className="text-muted">Report is being generated in the background...</p>
              </div>
            ) : (
              <>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h5 className="text-white m-0 font-title">{selectedReport.title}</h5>
                  <button onClick={() => downloadReport(selectedReport)} className="btn btn-outline-info btn-sm rounded-3">
                    <Download size={14} className="me-1" /> Download .md
                  </button>
                </div>
                <pre
                  className="text-secondary small p-3 rounded-3 overflow-auto"
                  style={{ background: 'rgba(0,0,0,0.3)', maxHeight: '500px', whiteSpace: 'pre-wrap' }}
                >
                  {selectedReport.content}
                </pre>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIReportsPage;
