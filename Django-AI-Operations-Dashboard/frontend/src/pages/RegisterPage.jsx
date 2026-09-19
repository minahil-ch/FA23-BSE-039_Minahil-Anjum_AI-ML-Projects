import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, User, Mail, Lock, Phone, AlertCircle, CheckCircle } from 'lucide-react';

const RegisterPage = () => {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('Creating Account...');

  const validateForm = () => {
    const tempErrors = {};
    if (!formData.username) tempErrors.username = 'Username is required.';
    if (!formData.email) tempErrors.email = 'Email is required.';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) tempErrors.email = 'Email is invalid.';
    if (!formData.first_name) tempErrors.first_name = 'First name is required.';
    if (!formData.last_name) tempErrors.last_name = 'Last name is required.';
    if (!formData.password) tempErrors.password = 'Password is required.';
    else if (formData.password.length < 6) tempErrors.password = 'Password must be at least 6 characters.';
    if (formData.password !== formData.confirm_password) {
      tempErrors.confirm_password = 'Passwords do not match.';
    }
    setErrors(tempErrors);
    return Object.keys(tempErrors).length === 0;
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setGeneralError('');
    setErrors({});
    setLoading(true);
    setLoadingMsg('Creating Account...');
    const result = await register(formData);
    if (result.success) {
      // Auto login after successful registration
      setLoadingMsg('Logging you in...');
      const loginResult = await login(formData.username, formData.password);
      setLoading(false);
      if (loginResult.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/');
        }, 1500);
      } else {
        // Registration worked but auto-login failed — go to login page
        setSuccess(true);
        setTimeout(() => {
          navigate('/login');
        }, 1500);
      }
    } else {
      setLoading(false);
      setLoadingMsg('Creating Account...');
      const err = result.error;
      if (err && typeof err === 'object' && !Array.isArray(err)) {
        // Check if there are field-level DRF errors (e.g. {username: ["already exists"]})
        const fieldErrors = {};
        let generalMsg = '';
        Object.entries(err).forEach(([field, msgs]) => {
          const msg = Array.isArray(msgs) ? msgs[0] : msgs;
          if (['username','email','password','confirm_password','first_name','last_name'].includes(field)) {
            fieldErrors[field] = msg;
          } else {
            generalMsg = generalMsg || msg;
          }
        });
        if (Object.keys(fieldErrors).length > 0) {
          setErrors(fieldErrors);
        } else {
          setGeneralError(generalMsg || 'Registration failed. Please check your details.');
        }
      } else {
        setGeneralError(typeof err === 'string' ? err : 'Registration failed. Please try again.');
      }
    }
  };

  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100 px-3 py-5">
      <div className="glass-card p-4 p-md-5 w-100" style={{ maxWidth: '550px' }}>
        
        {/* Logo/Header */}
        <div className="text-center mb-4">
          <Cpu className="text-primary spin-slow mb-3" size={48} />
          <h3 className="text-white font-title fw-bold m-0">Register Operator</h3>
          <p className="text-muted small mt-1">Join the Operations Command Center</p>
        </div>

        {success ? (
          <div className="text-center py-4">
            <CheckCircle className="text-success mb-3" size={56} />
            <h5 className="text-white fw-bold">Registration Successful!</h5>
            <p className="text-muted">Logging you into the dashboard...</p>
            <div className="spinner-border spinner-border-sm text-primary mt-2" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : (
          <>
            {generalError && (
              <div className="alert alert-danger bg-danger bg-opacity-10 border-danger border-opacity-25 text-danger d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3" role="alert">
                <AlertCircle size={16} />
                <span className="small">{generalError}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">Username</label>
                  <div className="position-relative">
                    <span className="position-absolute top-50 translate-middle-y ps-3 text-muted">
                      <User size={16} />
                    </span>
                    <input 
                      type="text" 
                      name="username"
                      className={`form-control ps-5 ${errors.username ? 'is-invalid' : ''}`}
                      placeholder="Username"
                      value={formData.username}
                      onChange={handleChange}
                    />
                    {errors.username && <div className="invalid-feedback">{errors.username}</div>}
                  </div>
                </div>

                <div className="col-md-6">
                  <label className="form-label">Email</label>
                  <div className="position-relative">
                    <span className="position-absolute top-50 translate-middle-y ps-3 text-muted">
                      <Mail size={16} />
                    </span>
                    <input 
                      type="email" 
                      name="email"
                      className={`form-control ps-5 ${errors.email ? 'is-invalid' : ''}`}
                      placeholder="Email"
                      value={formData.email}
                      onChange={handleChange}
                    />
                    {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                  </div>
                </div>
              </div>

              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">First Name</label>
                  <input 
                    type="text" 
                    name="first_name"
                    className={`form-control ${errors.first_name ? 'is-invalid' : ''}`}
                    placeholder="First Name"
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                  {errors.first_name && <div className="invalid-feedback">{errors.first_name}</div>}
                </div>

                <div className="col-md-6">
                  <label className="form-label">Last Name</label>
                  <input 
                    type="text" 
                    name="last_name"
                    className={`form-control ${errors.last_name ? 'is-invalid' : ''}`}
                    placeholder="Last Name"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                  {errors.last_name && <div className="invalid-feedback">{errors.last_name}</div>}
                </div>
              </div>

              <div>
                <label className="form-label">Phone Number</label>
                <div className="position-relative">
                  <span className="position-absolute top-50 translate-middle-y ps-3 text-muted">
                    <Phone size={16} />
                  </span>
                  <input 
                    type="text" 
                    name="phone_number"
                    className="form-control ps-5"
                    placeholder="Phone Number (Optional)"
                    value={formData.phone_number}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">Password</label>
                  <div className="position-relative">
                    <span className="position-absolute top-50 translate-middle-y ps-3 text-muted">
                      <Lock size={16} />
                    </span>
                    <input 
                      type="password" 
                      name="password"
                      className={`form-control ps-5 ${errors.password ? 'is-invalid' : ''}`}
                      placeholder="Password"
                      value={formData.password}
                      onChange={handleChange}
                    />
                    {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                  </div>
                </div>

                <div className="col-md-6">
                  <label className="form-label">Confirm Password</label>
                  <div className="position-relative">
                    <span className="position-absolute top-50 translate-middle-y ps-3 text-muted">
                      <Lock size={16} />
                    </span>
                    <input 
                      type="password" 
                      name="confirm_password"
                      className={`form-control ps-5 ${errors.confirm_password ? 'is-invalid' : ''}`}
                      placeholder="Confirm Password"
                      value={formData.confirm_password}
                      onChange={handleChange}
                    />
                    {errors.confirm_password && <div className="invalid-feedback">{errors.confirm_password}</div>}
                  </div>
                </div>
              </div>

              <button 
                type="submit" 
                className="btn glow-btn w-100 py-2 rounded-3 mt-3"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                    {loadingMsg}
                  </>
                ) : 'Register Operator'}
              </button>
            </form>

            <div className="text-center mt-4">
              <span className="text-muted small">Already have an account? </span>
              <Link to="/login" className="text-primary small text-decoration-none fw-semibold">Access Portal</Link>
            </div>
          </>
        )}

      </div>
    </div>
  );
};

export default RegisterPage;
export { RegisterPage };
