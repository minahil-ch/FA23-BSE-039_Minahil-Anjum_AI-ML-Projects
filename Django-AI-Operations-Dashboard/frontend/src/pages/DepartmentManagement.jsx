import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Building2, Save, X, PlusCircle, Edit, Trash2, AlertCircle } from 'lucide-react';

const DepartmentManagement = () => {
  const { hasRole } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDept, setEditingDept] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    manager: ''
  });
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [deptsRes, usersRes] = await Promise.all([
        api.get('departments/'),
        api.get('users/')
      ]);
      setDepartments(deptsRes.data.results || deptsRes.data);
      // Filter potential managers (Admins/Managers)
      const allUsers = usersRes.data.results || usersRes.data;
      setManagers(allUsers.filter(u => u.role === 'ADMIN' || u.role === 'MANAGER'));
    } catch (e) {
      console.error(e);
      setError('Failed to fetch departments directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartCreate = () => {
    setEditingDept(null);
    setFormData({ name: '', description: '', manager: '' });
    setShowForm(true);
  };

  const handleStartEdit = (dept) => {
    setEditingDept(dept);
    setFormData({
      name: dept.name,
      description: dept.description || '',
      manager: dept.manager || ''
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingDept(null);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.name) {
      setError('Department Name is required.');
      return;
    }

    const payload = {
      name: formData.name,
      description: formData.description,
      manager: formData.manager === '' ? null : parseInt(formData.manager)
    };

    try {
      if (editingDept) {
        const res = await api.put(`departments/${editingDept.id}/`, payload);
        setDepartments(departments.map(d => d.id === editingDept.id ? res.data : d));
        setSuccess(`Successfully updated department '${payload.name}'.`);
      } else {
        const res = await api.post('departments/', payload);
        setDepartments([...departments, res.data]);
        setSuccess(`Successfully created department '${payload.name}'.`);
      }
      setShowForm(false);
      setEditingDept(null);
    } catch (err) {
      console.error(err);
      setError('Failed to save department. Ensure department name is unique.');
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete the department '${name}'?`)) return;
    setError('');
    setSuccess('');
    try {
      await api.delete(`departments/${id}/`);
      setDepartments(departments.filter(d => d.id !== id));
      setSuccess(`Successfully deleted department '${name}'.`);
    } catch (err) {
      console.error(err);
      setError('Failed to delete department. Some records might depend on this department.');
    }
  };

  const isWriteAllowed = hasRole(['ADMIN', 'MANAGER']);

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center min-vh-50">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading departments...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0 font-title">Department Directory</h2>
          <p className="text-muted">Review divisions and operational heads, or assign managers.</p>
        </div>
        {isWriteAllowed && !showForm && (
          <button 
            onClick={handleStartCreate}
            className="btn glow-btn py-2 px-3 rounded-3 d-flex align-items-center gap-2"
          >
            <PlusCircle size={16} />
            <span>Create Department</span>
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
          <Building2 size={16} />
          <span className="small">{success}</span>
        </div>
      )}

      {/* Input Form */}
      {showForm && (
        <div className="glass-card p-4 mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="text-white font-title m-0">{editingDept ? 'Update Department' : 'Create New Department'}</h5>
            <button className="btn btn-link text-muted p-0" onClick={handleCancel}><X size={20} /></button>
          </div>
          <form onSubmit={handleSubmit} className="row g-3">
            <div className="col-md-4">
              <label className="form-label">Department Name</label>
              <input 
                type="text" 
                name="name" 
                className="form-control" 
                placeholder="e.g. Artificial Intelligence"
                value={formData.name}
                onChange={handleChange}
              />
            </div>
            <div className="col-md-4">
              <label className="form-label">Department Manager</label>
              <select name="manager" className="form-select" value={formData.manager} onChange={handleChange}>
                <option value="">Select Manager</option>
                {managers.map(m => (
                  <option key={m.id} value={m.id}>{m.first_name} {m.last_name} (@{m.username})</option>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Description</label>
              <input 
                type="text" 
                name="description" 
                className="form-control" 
                placeholder="Brief summary"
                value={formData.description}
                onChange={handleChange}
              />
            </div>
            <div className="col-12 d-flex gap-2 justify-content-end mt-4">
              <button type="submit" className="btn glow-btn py-2 px-4 rounded-3 d-flex align-items-center gap-2">
                <Save size={16} />
                <span>Save Department</span>
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
        {departments.length === 0 ? (
          <div className="col-12 text-center text-muted py-5">No departments found.</div>
        ) : (
          departments.map((dept) => (
            <div key={dept.id} className="col-12 col-md-6 col-xl-4">
              <div className="glass-card p-4 d-flex flex-column justify-content-between h-100">
                <div>
                  <div className="d-flex justify-content-between align-items-start">
                    <h5 className="text-white font-title mb-1 fw-bold">{dept.name}</h5>
                    <Building2 className="text-primary" size={20} />
                  </div>
                  <p className="text-muted small mt-2">{dept.description || 'No description provided.'}</p>
                </div>

                <div className="mt-4 border-top border-secondary border-opacity-10 pt-3">
                  <div className="d-flex justify-content-between text-secondary small mb-2">
                    <span>Manager:</span>
                    <span className="text-white fw-medium">
                      {dept.manager_detail ? `${dept.manager_detail.first_name} ${dept.manager_detail.last_name}` : 'Unassigned'}
                    </span>
                  </div>
                  <div className="d-flex justify-content-between text-secondary small mb-3">
                    <span>Teams / Operators:</span>
                    <span className="text-white fw-medium">{dept.teams_count} Teams / {dept.users_count} Users</span>
                  </div>

                  {isWriteAllowed && (
                    <div className="d-flex gap-2 mt-2">
                      <button 
                        onClick={() => handleStartEdit(dept)}
                        className="btn btn-outline-primary btn-sm rounded-3 flex-grow-1 d-flex align-items-center justify-content-center gap-1 border-opacity-25"
                      >
                        <Edit size={14} />
                        <span>Edit</span>
                      </button>
                      <button 
                        onClick={() => handleDelete(dept.id, dept.name)}
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

export default DepartmentManagement;
export { DepartmentManagement };
