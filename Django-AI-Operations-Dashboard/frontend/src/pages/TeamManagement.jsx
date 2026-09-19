import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { UserSquare2, Save, X, PlusCircle, Edit, Trash2, AlertCircle } from 'lucide-react';

const TeamManagement = () => {
  const { hasRole } = useAuth();
  const [teams, setTeams] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTeam, setEditingTeam] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    department: '',
    leader: ''
  });
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [teamsRes, deptsRes, usersRes] = await Promise.all([
        api.get('teams/'),
        api.get('departments/'),
        api.get('users/')
      ]);
      setTeams(teamsRes.data.results || teamsRes.data);
      setDepartments(deptsRes.data.results || deptsRes.data);
      const allUsers = usersRes.data.results || usersRes.data;
      setLeaders(allUsers.filter(u => u.role === 'ADMIN' || u.role === 'MANAGER'));
    } catch (e) {
      console.error(e);
      setError('Failed to fetch teams data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartCreate = () => {
    setEditingTeam(null);
    setFormData({ name: '', department: '', leader: '' });
    setShowForm(true);
  };

  const handleStartEdit = (team) => {
    setEditingTeam(team);
    setFormData({
      name: team.name,
      department: team.department || '',
      leader: team.leader || ''
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTeam(null);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.name || !formData.department) {
      setError('Team Name and Department are required.');
      return;
    }

    const payload = {
      name: formData.name,
      department: parseInt(formData.department),
      leader: formData.leader === '' ? null : parseInt(formData.leader)
    };

    try {
      if (editingTeam) {
        const res = await api.put(`teams/${editingTeam.id}/`, payload);
        // We re-fetch or mapping updated values. Since response contains direct ids, we load to refresh details
        loadData();
        setSuccess(`Successfully updated team '${payload.name}'.`);
      } else {
        const res = await api.post('teams/', payload);
        loadData();
        setSuccess(`Successfully created team '${payload.name}'.`);
      }
      setShowForm(false);
      setEditingTeam(null);
    } catch (err) {
      console.error(err);
      setError('Failed to save team. Ensure the team name is unique inside the department.');
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete team '${name}'?`)) return;
    setError('');
    setSuccess('');
    try {
      await api.delete(`teams/${id}/`);
      setTeams(teams.filter(t => t.id !== id));
      setSuccess(`Successfully deleted team '${name}'.`);
    } catch (err) {
      console.error(err);
      setError('Failed to delete team.');
    }
  };

  const isWriteAllowed = hasRole(['ADMIN', 'MANAGER']);

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center min-vh-50">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading teams...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title">Teams Directory</h2>
          <p className="text-muted">Manage department taskforce squads, lead developers and engineers.</p>
        </div>
        {isWriteAllowed && !showForm && (
          <button 
            onClick={handleStartCreate}
            className="btn glow-btn py-2 px-3 rounded-3 d-flex align-items-center gap-2"
          >
            <PlusCircle size={16} />
            <span>Create Team</span>
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
          <UserSquare2 size={16} />
          <span className="small">{success}</span>
        </div>
      )}

      {/* Input Form */}
      {showForm && (
        <div className="glass-card p-4 mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="text-white font-title m-0">{editingTeam ? 'Update Team' : 'Create New Team'}</h5>
            <button className="btn btn-link text-muted p-0" onClick={handleCancel}><X size={20} /></button>
          </div>
          <form onSubmit={handleSubmit} className="row g-3">
            <div className="col-md-4">
              <label className="form-label">Team Name</label>
              <input 
                type="text" 
                name="name" 
                className="form-control" 
                placeholder="e.g. RAG Systems Team"
                value={formData.name}
                onChange={handleChange}
              />
            </div>
            <div className="col-md-4">
              <label className="form-label">Parent Department</label>
              <select name="department" className="form-select" value={formData.department} onChange={handleChange}>
                <option value="">Select Department</option>
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Team Leader</label>
              <select name="leader" className="form-select" value={formData.leader} onChange={handleChange}>
                <option value="">Select Leader</option>
                {leaders.map(l => (
                  <option key={l.id} value={l.id}>{l.first_name} {l.last_name}</option>
                ))}
              </select>
            </div>
            <div className="col-12 d-flex gap-2 justify-content-end mt-4">
              <button type="submit" className="btn glow-btn py-2 px-4 rounded-3 d-flex align-items-center gap-2">
                <Save size={16} />
                <span>Save Team</span>
              </button>
              <button type="button" onClick={handleCancel} className="btn btn-outline-secondary py-2 px-3 rounded-3 text-light border-opacity-25">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Directory Cards */}
      <div className="row g-4">
        {teams.length === 0 ? (
          <div className="col-12 text-center text-muted py-5">No teams found.</div>
        ) : (
          teams.map((team) => (
            <div key={team.id} className="col-12 col-md-6 col-xl-4">
              <div className="glass-card p-4 d-flex flex-column justify-content-between h-100">
                <div>
                  <div className="d-flex justify-content-between align-items-start">
                    <h5 className="text-white font-title mb-1 fw-bold">{team.name}</h5>
                    <UserSquare2 className="text-primary" size={20} />
                  </div>
                  <span className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 mt-2" style={{ fontSize: '0.75rem' }}>
                    {team.department_detail?.name || 'Unknown Dept'}
                  </span>
                </div>

                <div className="mt-4 border-top border-secondary border-opacity-10 pt-3">
                  <div className="d-flex justify-content-between text-secondary small mb-2">
                    <span>Team Lead:</span>
                    <span className="text-white fw-medium">
                      {team.leader_detail ? `${team.leader_detail.first_name} ${team.leader_detail.last_name}` : 'Unassigned'}
                    </span>
                  </div>
                  <div className="d-flex justify-content-between text-secondary small mb-3">
                    <span>Members:</span>
                    <span className="text-white fw-medium">{team.users_count} Members</span>
                  </div>

                  {isWriteAllowed && (
                    <div className="d-flex gap-2 mt-2">
                      <button 
                        onClick={() => handleStartEdit(team)}
                        className="btn btn-outline-primary btn-sm rounded-3 flex-grow-1 d-flex align-items-center justify-content-center gap-1 border-opacity-25"
                      >
                        <Edit size={14} />
                        <span>Edit</span>
                      </button>
                      <button 
                        onClick={() => handleDelete(team.id, team.name)}
                        className="btn btn-outline-danger btn-sm rounded-3 d-flex align-items-center justify-content-center border-opacity-25"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TeamManagement;
export { TeamManagement };
