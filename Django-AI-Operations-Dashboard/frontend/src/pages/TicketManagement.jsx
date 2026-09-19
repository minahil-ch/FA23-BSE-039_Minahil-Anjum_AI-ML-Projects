import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  HelpCircle, 
  PlusCircle, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  AlertCircle, 
  CheckCircle,
  Clock,
  UserCheck
} from 'lucide-react';

const TicketManagement = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTicket, setEditingTicket] = useState(null);

  // Form Fields
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    status: 'OPEN',
    priority: 'MEDIUM',
    assigned_to: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [ticketsRes, usersRes] = await Promise.all([
        api.get('tickets/'),
        api.get('users/')
      ]);
      setTickets(ticketsRes.data.results || ticketsRes.data);
      const allUsers = usersRes.data.results || usersRes.data;
      // Filter potential assignees (Admins/Managers)
      setAgents(allUsers.filter(u => u.role === 'ADMIN' || u.role === 'MANAGER'));
    } catch (e) {
      console.error(e);
      setError('Failed to fetch support tickets catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartCreate = () => {
    setEditingTicket(null);
    setFormData({
      subject: '',
      description: '',
      status: 'OPEN',
      priority: 'MEDIUM',
      assigned_to: ''
    });
    setShowForm(true);
  };

  const handleStartEdit = (ticket) => {
    setEditingTicket(ticket);
    setFormData({
      subject: ticket.subject,
      description: ticket.description,
      status: ticket.status,
      priority: ticket.priority,
      assigned_to: ticket.assigned_to || ''
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTicket(null);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.subject || !formData.description) {
      setError('Ticket Subject and Description are required.');
      return;
    }

    const payload = {
      ...formData,
      assigned_to: formData.assigned_to === '' ? null : parseInt(formData.assigned_to)
    };

    try {
      if (editingTicket) {
        await api.put(`tickets/${editingTicket.id}/`, payload);
        setSuccess(`Successfully updated support ticket: '${payload.subject}'.`);
      } else {
        await api.post('tickets/', payload);
        setSuccess(`Successfully submitted support ticket: '${payload.subject}'.`);
      }
      setShowForm(false);
      setEditingTicket(null);
      loadData();
    } catch (err) {
      console.error(err);
      setError('Failed to save support ticket.');
    }
  };

  const handleDelete = async (id, subject) => {
    if (!window.confirm(`Are you sure you want to delete ticket '${subject}'?`)) return;
    setError('');
    setSuccess('');
    try {
      await api.delete(`tickets/${id}/`);
      setTickets(tickets.filter(t => t.id !== id));
      setSuccess(`Successfully deleted ticket '${subject}'.`);
    } catch (err) {
      console.error(err);
      setError('Permission denied or network issue deleting ticket.');
    }
  };

  const handleResolveTicket = async (ticket) => {
    try {
      await api.patch(`tickets/${ticket.id}/`, { status: 'RESOLVED' });
      setSuccess(`Ticket resolved.`);
      loadData();
    } catch (err) {
      console.error(err);
      setError('Failed to resolve ticket.');
    }
  };

  const isEditable = (ticket) => {
    if (user.role === 'ADMIN' || user.role === 'MANAGER') return true;
    return ticket.created_by === user.id;
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'HIGH': return 'bg-danger text-danger bg-opacity-10 border-danger border-opacity-20';
      case 'MEDIUM': return 'bg-warning text-warning bg-opacity-10 border-warning border-opacity-20';
      default: return 'bg-secondary text-secondary bg-opacity-10 border-secondary border-opacity-20';
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'RESOLVED': return 'bg-success text-success bg-opacity-10 border-success border-opacity-20';
      case 'CLOSED': return 'bg-secondary text-secondary bg-opacity-10 border-secondary border-opacity-20';
      case 'IN_PROGRESS': return 'bg-info text-info bg-opacity-10 border-info border-opacity-20';
      default: return 'bg-warning text-warning bg-opacity-10 border-warning border-opacity-20';
    }
  };

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title">Ticket Helpdesk</h2>
          <p className="text-muted">Report system failures, connection timeouts, or request administrative assistance.</p>
        </div>
        {!showForm && (
          <button 
            onClick={handleStartCreate}
            className="btn glow-btn py-2 px-3 rounded-3 d-flex align-items-center gap-2"
          >
            <PlusCircle size={16} />
            <span>Submit Ticket</span>
          </button>
        )}
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 border-danger border-opacity-25 text-danger d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3">
          <AlertCircle size={16} />
          <span className="small">{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success bg-success bg-opacity-10 border-success border-opacity-25 text-success d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3">
          <CheckCircle size={16} />
          <span className="small">{success}</span>
        </div>
      )}

      {/* Ticket form */}
      {showForm && (
        <div className="glass-card p-4 mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="text-white font-title m-0">{editingTicket ? 'Update Ticket details' : 'Raise Support Ticket'}</h5>
            <button className="btn btn-link text-muted p-0" onClick={handleCancel}><X size={20} /></button>
          </div>
          <form onSubmit={handleSubmit} className="row g-3">
            <div className="col-md-6">
              <label className="form-label">Subject</label>
              <input 
                type="text" 
                name="subject" 
                className="form-control" 
                placeholder="e.g. GPU Worker Memory Limit"
                value={formData.subject}
                onChange={handleChange}
              />
            </div>
            
            <div className="col-md-3">
              <label className="form-label">Priority</label>
              <select name="priority" className="form-select" value={formData.priority} onChange={handleChange}>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
              </select>
            </div>

            <div className="col-md-3">
              <label className="form-label">Status</label>
              <select name="status" className="form-select" value={formData.status} onChange={handleChange}>
                <option value="OPEN">Open</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </div>

            {user.role !== 'EMPLOYEE' && (
              <div className="col-md-6">
                <label className="form-label">Assign Agent</label>
                <select name="assigned_to" className="form-select" value={formData.assigned_to} onChange={handleChange}>
                  <option value="">Unassigned</option>
                  {agents.map(a => (
                    <option key={a.id} value={a.id}>{a.first_name} {a.last_name}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="col-12">
              <label className="form-label">Issue Description</label>
              <textarea 
                name="description" 
                className="form-control" 
                rows="3"
                placeholder="Provide details of the bug, logs, or assistance needed..."
                value={formData.description}
                onChange={handleChange}
              ></textarea>
            </div>

            <div className="col-12 d-flex gap-2 justify-content-end mt-4">
              <button type="submit" className="btn glow-btn py-2 px-4 rounded-3 d-flex align-items-center gap-2">
                <Save size={16} />
                <span>Submit Ticket</span>
              </button>
              <button type="button" onClick={handleCancel} className="btn btn-outline-secondary py-2 px-3 rounded-3 text-light border-opacity-25">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Ticket List Grid */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status"></div>
        </div>
      ) : tickets.length === 0 ? (
        <div className="text-center glass-card p-5 text-muted">No support tickets active.</div>
      ) : (
        <div className="row g-4">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="col-12 col-md-6">
              <div className="glass-card p-4 d-flex flex-column justify-content-between h-100">
                <div>
                  <div className="d-flex justify-content-between align-items-start gap-2">
                    <h5 className="text-white font-title mb-1 fw-semibold text-truncate">{ticket.subject}</h5>
                    <div className="d-flex gap-2 flex-shrink-0">
                      <span className={`badge ${getStatusBadgeClass(ticket.status)} border px-2 py-0.5`} style={{ fontSize: '0.7rem' }}>
                        {ticket.status}
                      </span>
                      <span className={`badge ${getPriorityBadgeClass(ticket.priority)} border px-2 py-0.5`} style={{ fontSize: '0.7rem' }}>
                        {ticket.priority}
                      </span>
                    </div>
                  </div>
                  <p className="text-muted small mt-3 mb-2 text-truncate-2" style={{ height: '38px', overflow: 'hidden' }}>{ticket.description}</p>
                  {/* AI classification badges — populated by Celery after ticket creation */}
                  {ticket.ai_category && (
                    <div className="d-flex flex-wrap gap-2 mb-2">
                      <span className="badge text-primary bg-primary bg-opacity-10" style={{ fontSize: '0.65rem' }}>
                        AI: {ticket.ai_category}
                      </span>
                      {ticket.ai_department && (
                        <span className="badge text-info bg-info bg-opacity-10" style={{ fontSize: '0.65rem' }}>
                          Dept: {ticket.ai_department}
                        </span>
                      )}
                      {ticket.ai_confidence > 0 && (
                        <span className="badge text-secondary bg-secondary bg-opacity-10" style={{ fontSize: '0.65rem' }}>
                          {Math.round(ticket.ai_confidence * 100)}% conf.
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="border-top border-secondary border-opacity-10 pt-3">
                  <div className="row g-2 align-items-center small text-secondary">
                    <div className="col-6 d-flex align-items-center gap-2">
                      <Clock size={14} />
                      <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="col-6 text-end text-truncate">
                      Agent: <span className="text-white fw-medium">{ticket.assigned_to_detail ? `${ticket.assigned_to_detail.first_name} ${ticket.assigned_to_detail.last_name.substring(0,1)}.` : 'Unassigned'}</span>
                    </div>
                  </div>

                  <div className="d-flex justify-content-between align-items-center mt-3 pt-2">
                    <div>
                      {ticket.status !== 'RESOLVED' && ticket.status !== 'CLOSED' && (user.role !== 'EMPLOYEE' || ticket.created_by === user.id) && (
                        <button 
                          onClick={() => handleResolveTicket(ticket)}
                          className="btn btn-outline-success btn-xs px-2 py-1 rounded-3 border-opacity-25"
                          style={{ fontSize: '0.7rem' }}
                        >
                          Resolve
                        </button>
                      )}
                    </div>
                    
                    {isEditable(ticket) && (
                      <div className="d-flex gap-2">
                        <button 
                          onClick={() => handleStartEdit(ticket)}
                          className="btn btn-outline-primary btn-sm rounded-circle p-2 border-opacity-25 d-flex align-items-center justify-content-center"
                        >
                          <Edit size={14} />
                        </button>
                        <button 
                          onClick={() => handleDelete(ticket.id, ticket.subject)}
                          className="btn btn-outline-danger btn-sm rounded-circle p-2 border-opacity-25 d-flex align-items-center justify-content-center"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TicketManagement;
export { TicketManagement };
