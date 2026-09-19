import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  FolderClosed, Upload, Trash2, Eye, Plus, X, Lock, Globe, 
  AlertCircle, FileText, RefreshCw, Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const MEDIA_BASE = 'http://localhost:8000';

const DocumentManagement = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [title, setTitle] = useState('');
  const [file, setFile] = useState(null);
  const [department, setDepartment] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [docsRes, deptsRes] = await Promise.all([
        api.get('documents/'),
        api.get('departments/')
      ]);
      setDocuments(docsRes.data.results || docsRes.data);
      setDepartments(deptsRes.data.results || deptsRes.data);
    } catch (e) {
      setError('Failed to fetch documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!title || !file) {
      setError('Document title and file are required.');
      return;
    }
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      setError('Only PDF, DOCX, and TXT files are supported for AI processing.');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);
    formData.append('is_public', isPublic);
    if (department) formData.append('department', department);

    try {
      const response = await api.post('documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDocuments([response.data, ...documents]);
      setSuccess(`Uploaded '${title}'. AI processing started in background.`);
      setTitle('');
      setFile(null);
      setDepartment('');
      setIsPublic(true);
      setShowUploadForm(false);
    } catch (err) {
      setError(err.response?.data?.file?.[0] || err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete '${name}'?`)) return;
    try {
      await api.delete(`documents/${id}/`);
      setDocuments(documents.filter(d => d.id !== id));
      setSuccess(`Deleted '${name}'.`);
    } catch {
      setError('Delete failed — check permissions.');
    }
  };

  const handleReprocess = async (id) => {
    try {
      await api.post(`ai/documents/${id}/reprocess/`);
      setSuccess('Reprocessing queued.');
      loadData();
    } catch {
      setError('Failed to queue reprocessing.');
    }
  };

  const handleSummarize = async (id) => {
    try {
      const res = await api.post('ai/summarize/', { document_id: id });
      alert(res.data.summary);
    } catch {
      setError('Summary failed — document may still be processing.');
    }
  };

  const isDeletable = (doc) => user.role === 'ADMIN' || user.role === 'MANAGER' || doc.uploaded_by === user.id;

  const statusBadge = (status) => {
    const map = {
      PENDING: { cls: 'text-warning', label: 'Pending' },
      PROCESSING: { cls: 'text-info', label: 'Processing' },
      COMPLETED: { cls: 'text-success', label: 'Indexed' },
      FAILED: { cls: 'text-danger', label: 'Failed' },
    };
    const s = map[status] || map.PENDING;
    return <span className={`badge ${s.cls} bg-opacity-10`} style={{ fontSize: '0.65rem' }}>{s.label}</span>;
  };

  const fileUrl = (path) => path?.startsWith('http') ? path : `${MEDIA_BASE}${path}`;

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title">Document Repository</h2>
          <p className="text-muted mb-0">Upload PDF, DOCX, or TXT — auto-indexed for RAG chatbot.</p>
        </div>
        {!showUploadForm && (
          <button onClick={() => setShowUploadForm(true)} className="btn glow-btn py-2 px-3 rounded-3 d-flex align-items-center gap-2">
            <Plus size={16} /><span>Upload Document</span>
          </button>
        )}
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 text-danger mb-3 py-2 px-3 rounded-3">
          <AlertCircle size={16} className="me-2" />{error}
        </div>
      )}
      {success && (
        <div className="alert alert-success bg-success bg-opacity-10 text-success mb-3 py-2 px-3 rounded-3">
          <FolderClosed size={16} className="me-2" />{success}
        </div>
      )}

      {showUploadForm && (
        <div className="glass-card p-4 mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="text-white font-title m-0">Upload New File</h5>
            <button className="btn btn-link text-muted p-0" onClick={() => setShowUploadForm(false)}><X size={20} /></button>
          </div>
          <form onSubmit={handleUploadSubmit} className="row g-3">
            <div className="col-md-5">
              <label className="form-label">Document Title</label>
              <input type="text" className="form-control" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. RAG Pipeline Guide" />
            </div>
            <div className="col-md-4">
              <label className="form-label">Department</label>
              <select className="form-select" value={department} onChange={(e) => setDepartment(e.target.value)}>
                <option value="">All Departments</option>
                {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Visibility</label>
              <div className="d-flex gap-3 mt-2">
                <div className="form-check">
                  <input className="form-check-input" type="radio" checked={isPublic} onChange={() => setIsPublic(true)} />
                  <label className="form-check-label text-secondary small">Public</label>
                </div>
                <div className="form-check">
                  <input className="form-check-input" type="radio" checked={!isPublic} onChange={() => setIsPublic(false)} />
                  <label className="form-check-label text-secondary small">Private</label>
                </div>
              </div>
            </div>
            <div className="col-md-8">
              <label className="form-label">File (PDF, DOCX, TXT)</label>
              <input type="file" className="form-control" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0])} />
            </div>
            <div className="col-md-4 d-flex align-items-end">
              <button type="submit" className="btn glow-btn w-100 py-2 rounded-3" disabled={uploading}>
                <Upload size={16} className="me-2" />{uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-center py-5"><div className="spinner-border text-primary" /></div>
      ) : documents.length === 0 ? (
        <div className="text-center glass-card p-5 text-muted">No documents uploaded yet.</div>
      ) : (
        <div className="row g-4">
          {documents.map((doc) => (
            <div key={doc.id} className="col-12 col-md-6 col-lg-4">
              <div className="glass-card p-4 h-100 d-flex flex-column">
                <div className="flex-grow-1">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <div className="d-flex align-items-center gap-2">
                      <FileText className="text-primary" size={22} />
                      <h6 className="text-white m-0 text-truncate" style={{ maxWidth: '140px' }}>{doc.title}</h6>
                    </div>
                    {doc.is_public ? (
                      <span className="text-success small"><Globe size={12} /> Public</span>
                    ) : (
                      <span className="text-warning small"><Lock size={12} /> Private</span>
                    )}
                  </div>
                  <div className="d-flex gap-2 mb-2 flex-wrap">
                    {statusBadge(doc.processing_status || 'PENDING')}
                    {doc.chunk_count > 0 && (
                      <span className="badge text-info bg-info bg-opacity-10" style={{ fontSize: '0.65rem' }}>
                        {doc.chunk_count} chunks
                      </span>
                    )}
                  </div>
                  <small className="text-muted d-block">Dept: {doc.department_detail?.name || 'Global'}</small>
                  <small className="text-muted d-block">By: {doc.uploaded_by_detail?.username}</small>
                  {doc.ai_summary && (
                    <p className="text-secondary small mt-2 mb-0" style={{ fontSize: '0.75rem' }}>
                      {doc.ai_summary.substring(0, 120)}...
                    </p>
                  )}
                  {doc.error_message && (
                    <p className="text-danger small mt-1 mb-0">{doc.error_message}</p>
                  )}
                </div>
                <div className="mt-3 pt-3 border-top border-secondary border-opacity-10 d-flex gap-2 flex-wrap">
                  <a href={fileUrl(doc.file)} target="_blank" rel="noopener noreferrer"
                    className="btn btn-outline-info btn-sm rounded-3 flex-grow-1">
                    <Eye size={14} className="me-1" />View
                  </a>
                  {doc.processing_status === 'COMPLETED' && (
                    <button onClick={() => handleSummarize(doc.id)} className="btn btn-outline-primary btn-sm rounded-3">
                      <Sparkles size={14} />
                    </button>
                  )}
                  <button onClick={() => handleReprocess(doc.id)} className="btn btn-outline-secondary btn-sm rounded-3">
                    <RefreshCw size={14} />
                  </button>
                  {isDeletable(doc) && (
                    <button onClick={() => handleDelete(doc.id, doc.title)} className="btn btn-outline-danger btn-sm rounded-3">
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentManagement;
