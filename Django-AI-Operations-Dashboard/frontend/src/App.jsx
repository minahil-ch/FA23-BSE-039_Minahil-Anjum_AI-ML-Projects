import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import Dashboard from './pages/Dashboard';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UserManagement from './pages/UserManagement';
import DepartmentManagement from './pages/DepartmentManagement';
import TeamManagement from './pages/TeamManagement';
import TaskManagement from './pages/TaskManagement';
import DocumentManagement from './pages/DocumentManagement';
import TicketManagement from './pages/TicketManagement';
import ActivityLogList from './pages/ActivityLogList';
import AIChatPage from './pages/AIChatPage';
import AIReportsPage from './pages/AIReportsPage';
import AIAgentPage from './pages/AIAgentPage';

// Layout Components
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Private Route Guard
const PrivateRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, loading, hasRole } = useAuth();

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Validating session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !hasRole(allowedRoles)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Authenticated Layout Wrapper
const AppLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const toggleSidebar = () => setSidebarOpen(prev => !prev);

  return (
    <div className="app-container">
      <div className={`sidebar-wrapper ${sidebarOpen ? 'show' : ''}`}>
        <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
      </div>
      <div className="main-content d-flex flex-column" style={{ minHeight: '100vh' }}>
        <Navbar onToggleSidebar={toggleSidebar} />
        <div className="flex-grow-1">
          {children}
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* All-Role Protected Routes */}
          <Route path="/" element={
            <PrivateRoute>
              <AppLayout><Dashboard /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/tasks" element={
            <PrivateRoute>
              <AppLayout><TaskManagement /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/documents" element={
            <PrivateRoute>
              <AppLayout><DocumentManagement /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/tickets" element={
            <PrivateRoute>
              <AppLayout><TicketManagement /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/ai-chat" element={
            <PrivateRoute>
              <AppLayout><AIChatPage /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/ai-agent" element={
            <PrivateRoute>
              <AppLayout><AIAgentPage /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/ai-reports" element={
            <PrivateRoute allowedRoles={['ADMIN', 'MANAGER']}>
              <AppLayout><AIReportsPage /></AppLayout>
            </PrivateRoute>
          } />

          {/* Admin/Manager Only Routes */}
          <Route path="/users" element={
            <PrivateRoute allowedRoles={['ADMIN', 'MANAGER']}>
              <AppLayout><UserManagement /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/departments" element={
            <PrivateRoute allowedRoles={['ADMIN', 'MANAGER']}>
              <AppLayout><DepartmentManagement /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/teams" element={
            <PrivateRoute allowedRoles={['ADMIN', 'MANAGER']}>
              <AppLayout><TeamManagement /></AppLayout>
            </PrivateRoute>
          } />
          <Route path="/logs" element={
            <PrivateRoute allowedRoles={['ADMIN', 'MANAGER']}>
              <AppLayout><ActivityLogList /></AppLayout>
            </PrivateRoute>
          } />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
