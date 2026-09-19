import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, Lock, User, AlertCircle } from 'lucide-react';

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    setLoading(true);
    const result = await login(username, password);
    setLoading(false);
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
  };

  const handleQuickLogin = (userType) => {
    setUsername(userType);
    setPassword(`${userType}123`);
  };

  return (
    <div className="d-flex align-items-center justify-content-center px-3" style={{ minHeight: '100vh' }}>
      <div className="glass-card p-4 p-md-5 w-100" style={{ maxWidth: '440px' }}>
        {/* Header */}
        <div className="text-center mb-4">
          <Cpu className="text-primary spin-slow mb-3" size={48} />
          <h3 className="text-white fw-bold m-0" style={{ fontFamily: 'Outfit, sans-serif' }}>AI Operations Portal</h3>
          <p className="text-muted small mt-1">Operations Control &amp; Agents Dashboard</p>
        </div>

        {error && (
          <div className="alert d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3" 
            role="alert"
            style={{ backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', color: '#f87171' }}>
            <AlertCircle size={16} />
            <span className="small">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
          <div>
            <label className="form-label">Username</label>
            <div className="position-relative">
              <span className="position-absolute top-50 translate-middle-y ps-3 text-muted" style={{ pointerEvents: 'none' }}>
                <User size={16} />
              </span>
              <input 
                type="text" 
                className="form-control ps-5" 
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </div>
          </div>

          <div>
            <label className="form-label">Password</label>
            <div className="position-relative">
              <span className="position-absolute top-50 translate-middle-y ps-3 text-muted" style={{ pointerEvents: 'none' }}>
                <Lock size={16} />
              </span>
              <input 
                type="password" 
                className="form-control ps-5" 
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="btn glow-btn w-100 py-2 rounded-3 mt-2"
            disabled={loading}
          >
            {loading ? (
              <><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />Authenticating...</>
            ) : 'Access Portal'}
          </button>
        </form>

        <div className="text-center mt-4">
          <span className="text-muted small">Don&apos;t have an account? </span>
          <Link to="/register" className="text-primary small text-decoration-none fw-semibold">Register Operator</Link>
        </div>

        {/* Demo Quick Login */}
        <div className="mt-4 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="text-center text-muted small mb-2">Quick Access Credentials:</div>
          <div className="d-flex gap-2 justify-content-center">
            <button onClick={() => handleQuickLogin('admin')} 
              className="btn btn-sm rounded-3 text-primary"
              style={{ backgroundColor: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', fontSize: '0.75rem' }}>
              Admin
            </button>
            <button onClick={() => handleQuickLogin('manager')} 
              className="btn btn-sm rounded-3 text-secondary"
              style={{ backgroundColor: 'rgba(107,114,128,0.12)', border: '1px solid rgba(107,114,128,0.25)', fontSize: '0.75rem' }}>
              Manager
            </button>
            <button onClick={() => handleQuickLogin('employee')} 
              className="btn btn-sm rounded-3 text-info"
              style={{ backgroundColor: 'rgba(6,182,212,0.12)', border: '1px solid rgba(6,182,212,0.25)', fontSize: '0.75rem' }}>
              Employee
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
