import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Users, Edit, Shield, Save, X, PlusCircle, AlertCircle } from 'lucide-react';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [editFormData, setEditFormData] = useState({
    role: '',
    department: '',
    team: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersRes, deptsRes, teamsRes] = await Promise.all([
        api.get('users/'),
        api.get('departments/'),
        api.get('teams/')
      ]);
      setUsers(usersRes.data.results || usersRes.data);
      setDepartments(deptsRes.data.results || deptsRes.data);
      setTeams(teamsRes.data.results || teamsRes.data);
    } catch (e) {
      console.error(e);
      setError('Failed to fetch user directory details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartEdit = (user) => {
    setEditingUser(user);
    setEditFormData({
      role: user.role,
      department: user.department || '',
      team: user.team || ''
    });
  };

  const handleCancelEdit = () => {
    setEditingUser(null);
  };

  const handleEditChange = (e) => {
    setEditFormData({
      ...editFormData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Clean up empty fields to avoid passing empty string as ID to ForeignKey
    const patchData = {
      role: editFormData.role,
      department: editFormData.department === '' ? null : editFormData.department,
      team: editFormData.team === '' ? null : editFormData.team
    };

    try {
      const response = await api.patch(`users/${editingUser.id}/`, patchData);
      setUsers(users.map(u => u.id === editingUser.id ? response.data : u));
      setSuccess(`Successfully updated configuration for operator '${editingUser.username}'.`);
      setEditingUser(null);
    } catch (err) {
      console.error(err);
      setError('Failed to update operator profile. Make sure database references are valid.');
    }
  };

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center min-vh-50">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading User Directory...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title">User Directory</h2>
          <p className="text-muted">Manage system operators, assign operational roles, departments, and teams.</p>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 border-danger border-opacity-25 text-danger d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3" role="alert">
          <AlertCircle size={16} />
          <span className="small">{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success bg-success bg-opacity-10 border-success border-opacity-25 text-success d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3" role="alert">
          <Shield size={16} />
          <span className="small">{success}</span>
        </div>
      )}

      {/* Edit Form Modal/Card */}
      {editingUser && (
        <div className="glass-card p-4 mb-4 border-primary border-opacity-20">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="text-white font-title m-0">Edit Permissions: {editingUser.first_name} {editingUser.last_name} ({editingUser.username})</h5>
            <button className="btn btn-link text-muted p-0" onClick={handleCancelEdit}><X size={20} /></button>
          </div>
          <form onSubmit={handleSave} className="row g-3 align-items-end">
            <div className="col-md-3">
              <label className="form-label">System Role</label>
              <select name="role" className="form-select" value={editFormData.role} onChange={handleEditChange}>
                <option value="ADMIN">Admin</option>
                <option value="MANAGER">Manager</option>
                <option value="EMPLOYEE">Employee</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Department Assignment</label>
              <select name="department" className="form-select" value={editFormData.department} onChange={handleEditChange}>
                <option value="">None</option>
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Team Assignment</label>
              <select name="team" className="form-select" value={editFormData.team} onChange={handleEditChange}>
                <option value="">None</option>
                {teams.filter(t => !editFormData.department || t.department === parseInt(editFormData.department)).map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
            <div className="col-md-3 d-flex gap-2">
              <button type="submit" className="btn glow-btn w-100 py-2 rounded-3 d-flex align-items-center justify-content-center gap-2">
                <Save size={16} />
                <span>Save Changes</span>
              </button>
              <button type="button" onClick={handleCancelEdit} className="btn btn-outline-secondary py-2 px-3 rounded-3 text-light border-opacity-25">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Directory Table */}
      <div className="glass-card overflow-hidden">
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th>Operator</th>
                <th>Email</th>
                <th>Role</th>
                <th>Department</th>
                <th>Team</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      <div className="bg-primary bg-opacity-20 text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold" style={{ width: '36px', height: '36px' }}>
                        {u.username.substring(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-white fw-semibold">{u.first_name} {u.last_name}</div>
                        <small className="text-muted">@{u.username}</small>
                      </div>
                    </div>
                  </td>
                  <td className="text-secondary">{u.email}</td>
                  <td>
                    <span className={`badge ${
                      u.role === 'ADMIN' ? 'bg-danger bg-opacity-10 text-danger border-danger border-opacity-20' : 
                      u.role === 'MANAGER' ? 'bg-secondary bg-opacity-10 text-secondary border-secondary border-opacity-20' : 
                      'bg-info bg-opacity-10 text-info border-info border-opacity-20'
                    } border px-3 py-1`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="text-secondary">{u.department_name || '-'}</td>
                  <td className="text-secondary">{u.team_name || '-'}</td>
                  <td>
                    <button 
                      onClick={() => handleStartEdit(u)}
                      className="btn btn-outline-primary btn-sm rounded-3 d-flex align-items-center gap-2 border-opacity-25"
                    >
                      <Edit size={14} />
                      <span>Edit</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
export { UserManagement };
