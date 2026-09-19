import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Users, 
  Building2, 
  UserSquare2, 
  CheckSquare, 
  FolderClosed, 
  HelpCircle, 
  ScrollText,
  LogOut,
  Cpu,
  MessageSquare,
  FileBarChart,
  Bot
} from 'lucide-react';

const menuItems = [
  { path: '/', name: 'Dashboard', icon: LayoutDashboard, roles: ['ADMIN', 'MANAGER', 'EMPLOYEE'] },
  { path: '/tasks', name: 'Tasks', icon: CheckSquare, roles: ['ADMIN', 'MANAGER', 'EMPLOYEE'] },
  { path: '/documents', name: 'Documents', icon: FolderClosed, roles: ['ADMIN', 'MANAGER', 'EMPLOYEE'] },
  { path: '/ai-chat', name: 'AI Chat (RAG)', icon: MessageSquare, roles: ['ADMIN', 'MANAGER', 'EMPLOYEE'] },
  { path: '/ai-agent', name: 'AI Agent', icon: Bot, roles: ['ADMIN', 'MANAGER', 'EMPLOYEE'] },
  { path: '/tickets', name: 'Tickets', icon: HelpCircle, roles: ['ADMIN', 'MANAGER', 'EMPLOYEE'] },
  { path: '/ai-reports', name: 'AI Reports', icon: FileBarChart, roles: ['ADMIN', 'MANAGER'] },
  { path: '/users', name: 'User Directory', icon: Users, roles: ['ADMIN', 'MANAGER'] },
  { path: '/departments', name: 'Departments', icon: Building2, roles: ['ADMIN', 'MANAGER'] },
  { path: '/teams', name: 'Teams', icon: UserSquare2, roles: ['ADMIN', 'MANAGER'] },
  { path: '/logs', name: 'Activity Logs', icon: ScrollText, roles: ['ADMIN', 'MANAGER'] },
];

const Sidebar = ({ toggleSidebar }) => {
  const { user, logout, hasRole } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="glass-panel d-flex flex-column p-3 h-100">
      <div className="d-flex align-items-center gap-2 mb-4 px-2 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <Cpu className="text-primary spin-slow" size={28} />
        <div>
          <h5 className="m-0 text-white fw-bold" style={{ fontFamily: 'Outfit, sans-serif' }}>AI Ops Portal</h5>
          <small className="text-muted">Operations Dashboard</small>
        </div>
      </div>

      <ul className="nav nav-pills flex-column mb-auto gap-1" style={{ listStyle: 'none', padding: 0 }}>
        {menuItems.map((item) => {
          if (!hasRole(item.roles)) return null;
          const Icon = item.icon;
          return (
            <li key={item.path}>
              <NavLink 
                to={item.path} 
                className={({ isActive }) => 
                  `d-flex align-items-center gap-3 px-3 py-2 rounded-3 text-decoration-none fw-medium small ${
                    isActive ? 'text-primary' : 'text-secondary'
                  }`
                }
                style={({ isActive }) => isActive 
                  ? { backgroundColor: 'rgba(99,102,241,0.15)', borderLeft: '3px solid #6366f1' }
                  : { borderLeft: '3px solid transparent' }
                }
                onClick={toggleSidebar}
                end={item.path === '/'}
              >
                <Icon size={17} />
                <span>{item.name}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>

      {user && (
        <div className="mt-auto pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="d-flex align-items-center gap-2 px-2 py-2 mb-2">
            <div 
              className="bg-primary bg-opacity-10 text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold" 
              style={{ width: '40px', height: '40px', flexShrink: 0 }}
            >
              {user.username.substring(0, 2).toUpperCase()}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div className="text-white fw-semibold small text-truncate">{user.first_name} {user.last_name}</div>
              <span 
                className="badge bg-secondary bg-opacity-20 text-secondary border border-secondary border-opacity-50" 
                style={{ fontSize: '0.65rem' }}
              >
                {user.role}
              </span>
            </div>
          </div>
          <button 
            onClick={handleLogout} 
            className="btn btn-outline-danger w-100 d-flex align-items-center justify-content-center gap-2 py-2 rounded-3"
            style={{ borderOpacity: 0.25 }}
          >
            <LogOut size={16} />
            <span>Log Out</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
