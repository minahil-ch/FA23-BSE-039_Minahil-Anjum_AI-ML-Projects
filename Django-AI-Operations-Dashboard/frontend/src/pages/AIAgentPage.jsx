/**
 * AI Agent Page
 *
 * Autonomous agent that:
 * 1. Receives natural-language requests
 * 2. Selects the appropriate tool (RAG search, classify, summarize, report, assign, email)
 * 3. Executes or requests human approval for sensitive actions
 */
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Bot, Send, CheckCircle, XCircle, Loader2, Shield, Cpu,
  AlertCircle, Clock, Zap
} from 'lucide-react';

const TOOL_LABELS = {
  search_documents: '🔍 Document Search (RAG)',
  classify_ticket: '🏷️ Ticket Classification',
  summarize_document: '📝 Document Summary',
  generate_report: '📊 Weekly Report',
  assign_ticket: '👤 Assign Ticket',
  send_email: '📧 Send Email',
};

const AIAgentPage = () => {
  const { user } = useAuth();
  const [runs, setRuns] = useState([]);
  const [request, setRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedRun, setSelectedRun] = useState(null);
  const [error, setError] = useState('');

  const loadRuns = async () => {
    try {
      const res = await api.get('ai/agent/runs/');
      setRuns(res.data.results || res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadRuns(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!request.trim() || loading) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.post('ai/agent/runs/run/', { request: request.trim() });
      setRuns([res.data, ...runs]);
      setSelectedRun(res.data);
      setRequest('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Agent request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (runId, approved) => {
    try {
      const res = await api.post(`ai/agent/runs/${runId}/approve/`, { approved });
      setRuns(runs.map(r => r.id === runId ? res.data : r));
      setSelectedRun(res.data);
    } catch (e) {
      setError('Approval action failed.');
    }
  };

  const examplePrompts = [
    'What documents do we have about deployment?',
    'Generate a weekly operations report',
    'Classify: VPN connection keeps dropping for remote team',
    'Assign ticket #1 to manager',
  ];

  return (
    <div className="animate-slide-in">
      <div className="mb-4">
        <h2 className="text-white m-0 font-title d-flex align-items-center gap-2">
          <Bot className="text-primary" size={28} />
          AI Operations Agent
        </h2>
        <p className="text-muted mb-0">
          Intelligent agent with tool selection and human approval for sensitive actions.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 text-danger mb-3 py-2 px-3 rounded-3">
          <AlertCircle size={16} className="me-2" />{error}
        </div>
      )}

      <div className="row g-4">
        {/* Agent input */}
        <div className="col-12 col-lg-5">
          <div className="glass-card p-4 mb-4">
            <h6 className="text-white mb-3 font-title d-flex align-items-center gap-2">
              <Zap size={16} className="text-warning" /> Send Request
            </h6>
            <form onSubmit={handleSubmit}>
              <textarea
                className="form-control mb-3"
                rows={4}
                placeholder="Describe what you need the agent to do..."
                value={request}
                onChange={(e) => setRequest(e.target.value)}
                disabled={loading}
              />
              <button type="submit" className="btn glow-btn w-100 py-2 rounded-3 d-flex align-items-center justify-content-center gap-2" disabled={loading}>
                {loading ? <Loader2 size={16} className="spin-slow" /> : <Send size={16} />}
                Run Agent
              </button>
            </form>

            <div className="mt-3">
              <small className="text-muted">Try these examples:</small>
              {examplePrompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => setRequest(p)}
                  className="btn btn-sm w-100 text-start text-secondary mt-1 py-1 px-2 rounded-2"
                  style={{ background: 'rgba(255,255,255,0.03)', fontSize: '0.75rem' }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Available tools */}
          <div className="glass-card p-4">
            <h6 className="text-white mb-3 font-title d-flex align-items-center gap-2">
              <Cpu size={16} /> Agent Tools
            </h6>
            {Object.entries(TOOL_LABELS).map(([key, label]) => (
              <div key={key} className="small text-secondary mb-2 p-2 rounded-2" style={{ background: 'rgba(255,255,255,0.03)' }}>
                {label}
                {['assign_ticket', 'send_email'].includes(key) && (
                  <span className="badge text-warning bg-warning bg-opacity-10 ms-2" style={{ fontSize: '0.6rem' }}>
                    <Shield size={8} /> Approval Required
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Run history & results */}
        <div className="col-12 col-lg-7">
          <div className="glass-card p-4">
            <h6 className="text-white mb-3 font-title">Agent Runs</h6>
            {runs.length === 0 ? (
              <p className="text-muted text-center py-4">No agent runs yet.</p>
            ) : (
              runs.map(run => (
                <div
                  key={run.id}
                  onClick={() => setSelectedRun(run)}
                  className="p-3 rounded-3 mb-3 cursor-pointer"
                  style={{
                    background: selectedRun?.id === run.id ? 'rgba(99,102,241,0.12)' : 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    cursor: 'pointer',
                  }}
                >
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <div className="text-white small fw-semibold">{run.user_request}</div>
                      <div className="text-muted mt-1" style={{ fontSize: '0.75rem' }}>
                        Tool: {TOOL_LABELS[run.selected_tool] || run.selected_tool}
                      </div>
                    </div>
                    <span className={`badge ${
                      run.status === 'COMPLETED' ? 'text-success bg-success' :
                      run.status === 'AWAITING_APPROVAL' ? 'text-warning bg-warning' :
                      run.status === 'REJECTED' ? 'text-danger bg-danger' : 'text-info bg-info'
                    } bg-opacity-10`} style={{ fontSize: '0.65rem' }}>
                      {run.status}
                    </span>
                  </div>

                  {/* Approval gate */}
                  {run.status === 'AWAITING_APPROVAL' && run.approval && (
                    <div className="mt-3 p-3 rounded-3" style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
                      <div className="d-flex align-items-center gap-2 mb-2">
                        <Shield size={14} className="text-warning" />
                        <small className="text-warning fw-semibold">Human Approval Required</small>
                      </div>
                      <p className="text-secondary small mb-2">{run.approval.action_description}</p>
                      <div className="d-flex gap-2">
                        <button
                          onClick={(e) => { e.stopPropagation(); handleApproval(run.id, true); }}
                          className="btn btn-success btn-sm rounded-3 flex-grow-1"
                        >
                          <CheckCircle size={14} className="me-1" /> Approve
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleApproval(run.id, false); }}
                          className="btn btn-danger btn-sm rounded-3 flex-grow-1"
                        >
                          <XCircle size={14} className="me-1" /> Reject
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Final answer */}
                  {selectedRun?.id === run.id && run.final_answer && (
                    <div className="mt-3 p-3 rounded-3" style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)' }}>
                      <small className="text-success fw-semibold">Agent Response:</small>
                      <pre className="text-secondary small mt-1 mb-0" style={{ whiteSpace: 'pre-wrap' }}>
                        {run.final_answer.substring(0, 1500)}
                      </pre>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAgentPage;
