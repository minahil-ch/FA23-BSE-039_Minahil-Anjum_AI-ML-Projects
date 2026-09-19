import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  CheckSquare, 
  PlusCircle, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  AlertCircle, 
  Calendar, 
  Clock,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';

const TaskManagement = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  // Filter States
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  // Form Fields
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'TODO',
    priority: 'MEDIUM',
    assigned_to: '',
    department: '',
    due_date: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      // Build filter parameters
      let url = 'tasks/?';
      if (statusFilter) url += `status=${statusFilter}&`;
      if (priorityFilter) url += `priority=${priorityFilter}&`;

      const [tasksRes, usersRes, deptsRes] = await Promise.all([
        api.get(url),
        api.get('users/'),
        api.get('departments/')
      ]);
      setTasks(tasksRes.data.results || tasksRes.data);
      setUsers(usersRes.data.results || usersRes.data);
      setDepartments(deptsRes.data.results || deptsRes.data);
    } catch (e) {
      console.error(e);
      setError('Failed to fetch tasks registry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, priorityFilter]);

  const handleStartCreate = () => {
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      status: 'TODO',
      priority: 'MEDIUM',
      assigned_to: '',
      department: '',
      due_date: ''
    });
    setShowForm(true);
  };

  const handleStartEdit = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      status: task.status,
      priority: task.priority,
      assigned_to: task.assigned_to || '',
      department: task.department || '',
      due_date: task.due_date ? new Date(task.due_date).toISOString().substring(0, 16) : ''
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.title) {
      setError('Task Title is required.');
      return;
    }

    const payload = {
      ...formData,
      assigned_to: formData.assigned_to === '' ? null : parseInt(formData.assigned_to),
      department: formData.department === '' ? null : parseInt(formData.department),
      due_date: formData.due_date === '' ? null : new Date(formData.due_date).toISOString()
    };

    try {
      if (editingTask) {
        await api.put(`tasks/${editingTask.id}/`, payload);
        setSuccess(`Successfully updated task '${payload.title}'.`);
      } else {
        await api.post('tasks/', payload);
        setSuccess(`Successfully created task '${payload.title}'.`);
      }
      setShowForm(false);
      setEditingTask(null);
      loadData();
    } catch (err) {
      console.error(err);
      setError('Failed to save task.');
    }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete task '${title}'?`)) return;
    setError('');
    setSuccess('');
    try {
      await api.delete(`tasks/${id}/`);
      setTasks(tasks.filter(t => t.id !== id));
      setSuccess(`Successfully deleted task '${title}'.`);
    } catch (err) {
      console.error(err);
      setError('Permission denied or network issue deleting task.');
    }
  };

  const handleQuickStatusChange = async (task, newStatus) => {
    try {
      await api.patch(`tasks/${task.id}/`, { status: newStatus });
      setSuccess(`Task status changed to ${newStatus}.`);
      loadData();
    } catch (err) {
      console.error(err);
      setError('Could not update task status.');
    }
  };

  const isEditable = (task) => {
    if (user.role === 'ADMIN' || user.role === 'MANAGER') return true;
    return task.created_by === user.id || task.assigned_to === user.id;
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'CRITICAL': return 'bg-danger text-danger bg-opacity-10 border-danger border-opacity-20';
      case 'HIGH': return 'bg-warning text-warning bg-opacity-10 border-warning border-opacity-20';
      case 'MEDIUM': return 'bg-info text-info bg-opacity-10 border-info border-opacity-20';
      default: return 'bg-secondary text-secondary bg-opacity-10 border-secondary border-opacity-20';
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'DONE': return 'bg-success text-success bg-opacity-10 border-success border-opacity-20';
      case 'REVIEW': return 'bg-primary text-primary bg-opacity-10 border-primary border-opacity-20';
      case 'IN_PROGRESS': return 'bg-info text-info bg-opacity-10 border-info border-opacity-20';
      default: return 'bg-secondary text-secondary bg-opacity-10 border-secondary border-opacity-20';
    }
  };

  return (
    <div className="animate-slide-in">
      <div className="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
        <div>
          <h2 className="text-white m-0 font-title">Task Management</h2>
          <p className="text-muted">Track sprints, assign tickets, set priorities, and complete activities.</p>
        </div>
        {!showForm && (
          <button 
            onClick={handleStartCreate}
            className="btn glow-btn py-2 px-3 rounded-3 d-flex align-items-center gap-2"
          >
            <PlusCircle size={16} />
            <span>Create Task</span>
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
          <CheckCircle2 size={16} />
          <span className="small">{success}</span>
        </div>
      )}

      {/* Task Filters */}
      {!showForm && (
        <div className="glass-card p-3 mb-4 d-flex flex-wrap gap-3 align-items-center">
          <span className="text-secondary small fw-bold">Filters:</span>
          <div>
            <select className="form-select form-select-sm border-opacity-20" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="REVIEW">Review</option>
              <option value="DONE">Done</option>
            </select>
          </div>
          <div>
            <select className="form-select form-select-sm border-opacity-20" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
              <option value="">All Priorities</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
        </div>
      )}

      {/* Task Creation/Editing Form */}
      {showForm && (
        <div className="glass-card p-4 mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="text-white font-title m-0">{editingTask ? 'Update Task' : 'Create New Task'}</h5>
            <button className="btn btn-link text-muted p-0" onClick={handleCancel}><X size={20} /></button>
          </div>
          <form onSubmit={handleSubmit} className="row g-3">
            <div className="col-md-6">
              <label className="form-label">Task Title</label>
              <input 
                type="text" 
                name="title" 
                className="form-control" 
                placeholder="e.g. Optimize Redis Caches"
                value={formData.title}
                onChange={handleChange}
              />
            </div>
            
            <div className="col-md-3">
              <label className="form-label">Priority</label>
              <select name="priority" className="form-select" value={formData.priority} onChange={handleChange}>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>

            <div className="col-md-3">
              <label className="form-label">Status</label>
              <select name="status" className="form-select" value={formData.status} onChange={handleChange}>
                <option value="TODO">To Do</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="REVIEW">Review</option>
                <option value="DONE">Done</option>
              </select>
            </div>

            <div className="col-md-4">
              <label className="form-label">Assigned Operator</label>
              <select name="assigned_to" className="form-select" value={formData.assigned_to} onChange={handleChange}>
                <option value="">Unassigned</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>{u.first_name} {u.last_name}</option>
                ))}
              </select>
            </div>

            <div className="col-md-4">
              <label className="form-label">Department Scope</label>
              <select name="department" className="form-select" value={formData.department} onChange={handleChange}>
                <option value="">All Departments</option>
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>

            <div className="col-md-4">
              <label className="form-label">Due Date</label>
              <input 
                type="datetime-local" 
                name="due_date" 
                className="form-control"
                value={formData.due_date}
                onChange={handleChange}
              />
            </div>

            <div className="col-12">
              <label className="form-label">Detailed Description</label>
              <textarea 
                name="description" 
                className="form-control" 
                rows="3"
                placeholder="Explain the objectives, targets, and parameters..."
                value={formData.description}
                onChange={handleChange}
              ></textarea>
            </div>

            <div className="col-12 d-flex gap-2 justify-content-end mt-4">
              <button type="submit" className="btn glow-btn py-2 px-4 rounded-3 d-flex align-items-center gap-2">
                <Save size={16} />
                <span>Save Task</span>
              </button>
              <button type="button" onClick={handleCancel} className="btn btn-outline-secondary py-2 px-3 rounded-3 text-light border-opacity-25">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Task List Grid */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status"></div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="text-center glass-card p-5 text-muted">No tasks found matching current filters.</div>
      ) : (
        <div className="row g-4">
          {tasks.map((task) => (
            <div key={task.id} className="col-12 col-md-6">
              <div className="glass-card p-4 d-flex flex-column justify-content-between h-100">
                <div>
                  <div className="d-flex justify-content-between align-items-start gap-2">
                    <h5 className="text-white font-title mb-1 fw-semibold text-truncate">{task.title}</h5>
                    <div className="d-flex gap-2 flex-shrink-0">
                      <span className={`badge ${getStatusBadgeClass(task.status)} border px-2 py-0.5`} style={{ fontSize: '0.7rem' }}>
                        {task.status}
                      </span>
                      <span className={`badge ${getPriorityBadgeClass(task.priority)} border px-2 py-0.5`} style={{ fontSize: '0.7rem' }}>
                        {task.priority}
                      </span>
                    </div>
                  </div>
                  <p className="text-muted small mt-3 mb-4 text-truncate-2" style={{ height: '38px', overflow: 'hidden' }}>{task.description || 'No description provided.'}</p>
                </div>

                <div className="border-top border-secondary border-opacity-10 pt-3">
                  <div className="row g-2 align-items-center small text-secondary">
                    <div className="col-6 d-flex align-items-center gap-2">
                      <Calendar size={14} />
                      <span className="text-truncate">
                        {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No deadline'}
                      </span>
                    </div>
                    <div className="col-6 text-end text-truncate">
                      Assignee: <span className="text-white fw-medium">{task.assigned_to_detail ? `${task.assigned_to_detail.first_name} ${task.assigned_to_detail.last_name.substring(0, 1)}.` : 'Unassigned'}</span>
                    </div>
                  </div>

                  <div className="d-flex justify-content-between align-items-center mt-3 pt-2">
                    <div className="d-flex gap-1">
                      {task.status !== 'DONE' && (
                        <button 
                          onClick={() => handleQuickStatusChange(task, 'DONE')}
                          className="btn btn-outline-success btn-xs px-2 py-1 rounded-3 border-opacity-25"
                          style={{ fontSize: '0.7rem' }}
                        >
                          Mark Done
                        </button>
                      )}
                      {task.status === 'TODO' && (
                        <button 
                          onClick={() => handleQuickStatusChange(task, 'IN_PROGRESS')}
                          className="btn btn-outline-info btn-xs px-2 py-1 rounded-3 border-opacity-25"
                          style={{ fontSize: '0.7rem' }}
                        >
                          Start Progress
                        </button>
                      )}
                    </div>
                    
                    {isEditable(task) && (
                      <div className="d-flex gap-2">
                        <button 
                          onClick={() => handleStartEdit(task)}
                          className="btn btn-outline-primary btn-sm rounded-circle p-2 border-opacity-25 d-flex align-items-center justify-content-center"
                        >
                          <Edit size={14} />
                        </button>
                        <button 
                          onClick={() => handleDelete(task.id, task.title)}
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

export default TaskManagement;
export { TaskManagement };
