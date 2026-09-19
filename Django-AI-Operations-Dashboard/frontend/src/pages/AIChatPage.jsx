/**
 * RAG Chatbot Page
 *
 * Lets users ask questions grounded ONLY in uploaded documents.
 * Shows source references (document title, chunk, excerpt) with each answer.
 */
import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import {
  MessageSquare, Send, Bot, User, BookOpen, Loader2, Sparkles, AlertCircle
} from 'lucide-react';

const AIChatPage = () => {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const chatEndRef = useRef(null);

  // Load past chat sessions on mount
  useEffect(() => {
    api.get('ai/chat/sessions/')
      .then(res => setSessions(res.data.results || res.data))
      .catch(() => {});
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSession = async (sessionId) => {
    try {
      const res = await api.get(`ai/chat/sessions/${sessionId}/`);
      setActiveSession(res.data);
      setMessages(res.data.messages || []);
    } catch (e) {
      setError('Failed to load chat session.');
    }
  };

  const startNewChat = () => {
    setActiveSession(null);
    setMessages([]);
    setQuestion('');
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();
    setQuestion('');
    setLoading(true);
    setError('');

    // Optimistically show user message
    setMessages(prev => [...prev, { role: 'user', content: userQuestion, sources: [] }]);

    try {
      const res = await api.post('ai/chat/', {
        question: userQuestion,
        session_id: activeSession?.id || null,
      });

      setActiveSession(prev => prev || { id: res.data.session_id });
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: res.data.answer,
          sources: res.data.sources || [],
          model_used: res.data.model_used,
        },
      ]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get AI response.');
      setMessages(prev => prev.slice(0, -1)); // remove optimistic user msg on failure
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title d-flex align-items-center gap-2">
            <MessageSquare className="text-primary" size={28} />
            RAG Knowledge Chat
          </h2>
          <p className="text-muted mb-0">
            Ask questions — answers come only from your uploaded PDF, DOCX, and TXT documents.
          </p>
        </div>
        <button onClick={startNewChat} className="btn glow-btn py-2 px-3 rounded-3">
          New Chat
        </button>
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 border-danger border-opacity-25 text-danger d-flex align-items-center gap-2 mb-3 py-2 px-3 rounded-3">
          <AlertCircle size={16} /><span className="small">{error}</span>
        </div>
      )}

      <div className="row g-4">
        {/* Session sidebar */}
        <div className="col-12 col-lg-3">
          <div className="glass-card p-3">
            <h6 className="text-white mb-3 font-title">Recent Chats</h6>
            {sessions.length === 0 ? (
              <p className="text-muted small">No previous sessions.</p>
            ) : (
              sessions.slice(0, 8).map(s => (
                <button
                  key={s.id}
                  onClick={() => loadSession(s.id)}
                  className={`btn w-100 text-start mb-2 py-2 px-3 rounded-3 small ${
                    activeSession?.id === s.id ? 'text-primary' : 'text-secondary'
                  }`}
                  style={{
                    background: activeSession?.id === s.id ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}
                >
                  {s.title?.substring(0, 40) || `Session #${s.id}`}
                </button>
              ))
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="col-12 col-lg-9">
          <div className="glass-card d-flex flex-column" style={{ height: '65vh' }}>
            {/* Messages */}
            <div className="flex-grow-1 overflow-auto p-4">
              {messages.length === 0 ? (
                <div className="text-center text-muted py-5">
                  <Sparkles className="text-primary mb-3" size={40} />
                  <p>Upload documents first, then ask anything about their content.</p>
                  <small>Example: "What are the deployment steps?" or "Summarize the RAG pipeline"</small>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`mb-4 d-flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div
                      className={`rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 ${
                        msg.role === 'user' ? 'bg-primary bg-opacity-20 text-primary' : 'bg-success bg-opacity-20 text-success'
                      }`}
                      style={{ width: 36, height: 36 }}
                    >
                      {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                    </div>
                    <div style={{ maxWidth: '80%' }}>
                      <div
                        className="p-3 rounded-3"
                        style={{
                          background: msg.role === 'user' ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.05)',
                          border: '1px solid rgba(255,255,255,0.08)',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        <span className="text-white small">{msg.content}</span>
                      </div>
                      {/* Source references for assistant messages */}
                      {msg.sources?.length > 0 && (
                        <div className="mt-2">
                          <small className="text-muted d-flex align-items-center gap-1 mb-1">
                            <BookOpen size={12} /> Sources:
                          </small>
                          {msg.sources.map((src, i) => (
                            <div
                              key={i}
                              className="small p-2 rounded-2 mb-1 text-secondary"
                              style={{ background: 'rgba(6,182,212,0.08)', border: '1px solid rgba(6,182,212,0.15)' }}
                            >
                              <strong className="text-info">{src.document_title}</strong>
                              <span className="text-muted"> — chunk {src.chunk_index}</span>
                              <div className="mt-1" style={{ fontSize: '0.75rem' }}>{src.excerpt}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="d-flex align-items-center gap-2 text-muted">
                  <Loader2 size={16} className="spin-slow" /> Searching documents...
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-3 border-top border-secondary border-opacity-10">
              <div className="d-flex gap-2">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ask a question about your documents..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  disabled={loading}
                />
                <button type="submit" className="btn glow-btn px-4 rounded-3" disabled={loading || !question.trim()}>
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChatPage;
