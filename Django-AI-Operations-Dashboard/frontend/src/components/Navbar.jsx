import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { 
  Bell, 
  Menu, 
  Check, 
  AlertTriangle, 
  Info, 
  CheckCircle,
  X,
  Sun,
  Moon
} from 'lucide-react';

const Navbar = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [theme, setTheme] = useState(document.documentElement.getAttribute('data-theme') || localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const fetchNotifications = async () => {
    try {
      const response = await api.get('notifications/');
      setNotifications(response.data.results || response.data);
    } catch (e) {
      console.error("Failed to load notifications:", e);
    }
  };

  useEffect(() => {
    if (user) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const markAllAsRead = async () => {
    try {
      await api.post('notifications/mark_all_as_read/');
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
    } catch (e) {
      console.error(e);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.patch(`notifications/${id}/mark_as_read/`);
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (e) {
      console.error(e);
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'SUCCESS': return <CheckCircle className="text-success" size={16} />;
      case 'WARNING': return <AlertTriangle className="text-warning" size={16} />;
      case 'ALERT': return <AlertTriangle className="text-danger" size={16} />;
      default: return <Info className="text-info" size={16} />;
    }
  };

  return (
    <nav className="navbar navbar-expand-lg glass-card px-4 py-2 mb-4 d-flex justify-content-between align-items-center" style={{ borderRadius: '16px' }}>
      {/* Sidebar Toggle for Mobile */}
      <button 
        className="btn d-lg-none text-light border border-secondary border-opacity-25"
        onClick={onToggleSidebar}
      >
        <Menu size={20} />
      </button>

      {/* User Greeting */}
      <div className="d-none d-md-block">
        <h5 className="m-0 text-white">Welcome back, <span className="text-primary">{user?.first_name || 'Operator'}</span></h5>
        <small className="text-muted">Operations Status: <span className="text-success fw-semibold">ONLINE</span></small>
      </div>

      {/* Right Controls */}
      <div className="d-flex align-items-center gap-3 ms-auto position-relative">
        
        {/* Theme Toggle */}
        <button 
          className="btn btn-outline-secondary border-opacity-25 rounded-circle p-2 d-flex align-items-center justify-content-center text-light"
          onClick={toggleTheme}
          title={theme === 'dark' ? "Switch to Light Theme" : "Switch to Dark Theme"}
          style={{ width: '38px', height: '38px' }}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Notifications Trigger */}
        <div className="position-relative">
          <button 
            className="btn btn-outline-secondary border-opacity-25 rounded-circle p-2 d-flex align-items-center justify-content-center text-light"
            onClick={() => setShowNotifications(!showNotifications)}
            style={{ width: '38px', height: '38px' }}
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-dark" style={{ fontSize: '0.65rem', padding: '0.25em 0.5em' }}>
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Panel */}
          {showNotifications && (
            <div className="glass-card position-absolute end-0 mt-2 p-3 shadow-lg" style={{ width: '320px', zIndex: 1000 }}>
              <div className="d-flex justify-content-between align-items-center pb-2 mb-2 border-bottom border-secondary border-opacity-25">
                <h6 className="m-0 text-white fw-bold">Notifications</h6>
                <div className="d-flex gap-2 align-items-center">
                  {unreadCount > 0 && (
                    <button 
                      onClick={markAllAsRead} 
                      className="btn btn-link text-primary p-0 text-decoration-none"
                      style={{ fontSize: '0.75rem' }}
                    >
                      Mark all read
                    </button>
                  )}
                  <button className="btn btn-link text-muted p-0" onClick={() => setShowNotifications(false)}>
                    <X size={14} />
                  </button>
                </div>
              </div>

              {/* Notifications List */}
              <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
                {notifications.length === 0 ? (
                  <div className="text-center py-3 text-muted small">No notifications</div>
                ) : (
                  notifications.map((notification) => (
                    <div 
                      key={notification.id} 
                      className={`p-2 rounded-2 mb-2 d-flex gap-2 align-items-start border ${
                        notification.is_read 
                          ? 'border-0 bg-transparent' 
                          : 'border-primary border-opacity-10 bg-primary bg-opacity-10'
                      }`}
                    >
                      <div className="mt-1">{getNotificationIcon(notification.notification_type)}</div>
                      <div className="flex-grow-1" style={{ minWidth: 0 }}>
                        <div className={`small text-truncate ${notification.is_read ? 'text-secondary' : 'text-white fw-semibold'}`}>
                          {notification.title}
                        </div>
                        <div className="text-muted" style={{ fontSize: '0.75rem', wordBreak: 'break-word' }}>
                          {notification.message}
                        </div>
                      </div>
                      {!notification.is_read && (
                        <button 
                          onClick={() => markAsRead(notification.id)}
                          className="btn btn-link text-success p-0 mt-1 align-self-start"
                        >
                          <Check size={14} />
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Mini Profile */}
        {user && (
          <div className="d-flex align-items-center gap-2 border-start border-secondary border-opacity-25 ps-3">
            <div className="d-none d-sm-block text-end">
              <div className="text-white small fw-semibold">{user.username}</div>
              <small className="text-muted text-uppercase" style={{ fontSize: '0.7rem' }}>{user.role}</small>
            </div>
            <div 
              className="bg-primary bg-opacity-25 rounded-circle d-flex align-items-center justify-content-center text-primary fw-bold border border-primary border-opacity-20" 
              style={{ width: '36px', height: '36px' }}
            >
              {user.username.substring(0, 2).toUpperCase()}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
