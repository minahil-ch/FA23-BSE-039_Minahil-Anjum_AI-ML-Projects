import React, { useState, useEffect } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, BarChart, Bar, Cell 
} from 'recharts';
import api from '../services/api';
import { 
  CheckSquare, HelpCircle, FolderClosed, Activity, 
  Cpu, Database, TrendingUp, RefreshCw, Zap, Bot
} from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalTasks: 0, todoTasks: 0, inProgressTasks: 0, doneTasks: 0,
    openTickets: 0, totalDocuments: 0, aiInteractions: 0,
  });
  const [activities, setActivities] = useState([]);
  const [aiLogs, setAiLogs] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [tasksRes, ticketsRes, docsRes, logsRes, aiRes, agentRes] = await Promise.all([
        api.get('tasks/'),
        api.get('tickets/'),
        api.get('documents/'),
        api.get('activity-logs/'),
        api.get('ai/interactions/').catch(() => ({ data: [] })),
        api.get('ai/agent/runs/').catch(() => ({ data: [] })),
      ]);

      const tasks = tasksRes.data.results || tasksRes.data;
      const tickets = ticketsRes.data.results || ticketsRes.data;
      const docs = docsRes.data.results || docsRes.data;
      const logs = logsRes.data.results || logsRes.data;
      const aiInteractions = aiRes.data.results || aiRes.data || [];
      const agentRuns = agentRes.data.results || agentRes.data || [];

      setStats({
        totalTasks: tasks.length,
        todoTasks: tasks.filter(t => t.status === 'TODO').length,
        inProgressTasks: tasks.filter(t => ['IN_PROGRESS', 'REVIEW'].includes(t.status)).length,
        doneTasks: tasks.filter(t => t.status === 'DONE').length,
        openTickets: tickets.filter(t => ['OPEN', 'IN_PROGRESS'].includes(t.status)).length,
        totalDocuments: docs.length,
        aiInteractions: aiInteractions.length,
      });
      setActivities(logs.slice(0, 5));

      // Real AI agent activity from database
      setAiLogs(agentRuns.slice(0, 5).map(run => ({
        id: run.id,
        agent: run.selected_tool?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'AI Agent',
        action: run.user_request?.substring(0, 60) || run.final_answer?.substring(0, 60) || 'Processing...',
        time: new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        status: run.status === 'COMPLETED' ? 'SUCCESS' : run.status === 'AWAITING_APPROVAL' ? 'PENDING' : run.status,
      })));

      // Chart from AI interaction logs grouped by type
      const typeCounts = {};
      aiInteractions.forEach(i => {
        typeCounts[i.interaction_type] = (typeCounts[i.interaction_type] || 0) + 1;
      });
      setChartData(Object.entries(typeCounts).map(([name, value]) => ({ name: name.replace(/_/g, ' '), value })));
    } catch (e) {
      console.error('Error loading dashboard:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDashboardData(); }, []);

  const taskDistribution = [
    { name: 'To Do', value: stats.todoTasks, color: '#f59e0b' },
    { name: 'In Progress', value: stats.inProgressTasks, color: '#6366f1' },
    { name: 'Completed', value: stats.doneTasks, color: '#10b981' },
  ];

  const StatCard = ({ icon: Icon, label, value, sub, iconBg, iconColor }) => (
    <div className="col-12 col-sm-6 col-xl-3">
      <div className="glass-card p-3 d-flex align-items-center gap-3">
        <div className={`${iconBg} ${iconColor} rounded-3 p-3`}>
          <Icon size={24} />
        </div>
        <div>
          <span className="text-muted small">{label}</span>
          <h3 className="m-0 text-white fw-bold mt-1" style={{ fontFamily: 'Outfit, sans-serif' }}>{value}</h3>
          <small className={iconColor}>{sub}</small>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center" style={{ minHeight: '60vh' }}>
        <div className="spinner-border text-primary" role="status" />
      </div>
    );
  }

  return (
    <div className="animate-slide-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="text-white m-0" style={{ fontFamily: 'Outfit, sans-serif' }}>Operations Console</h2>
          <p className="text-muted mb-0">Real-time overview — tasks, tickets, documents, and AI activity.</p>
        </div>
        <button onClick={loadDashboardData} className="btn btn-outline-secondary rounded-3 d-flex align-items-center gap-2 text-light"
          style={{ borderColor: 'rgba(255,255,255,0.15)' }}>
          <RefreshCw size={16} /><span className="d-none d-sm-inline">Refresh</span>
        </button>
      </div>

      <div className="row g-4 mb-4">
        <StatCard icon={CheckSquare} label="Active Tasks" value={stats.totalTasks}
          sub={<><TrendingUp size={12} className="me-1" />{stats.doneTasks} Completed</>}
          iconBg="bg-primary bg-opacity-15" iconColor="text-primary" />
        <StatCard icon={HelpCircle} label="Open Tickets" value={stats.openTickets}
          sub="Support Queue" iconBg="bg-danger bg-opacity-15" iconColor="text-danger" />
        <StatCard icon={FolderClosed} label="Documents" value={stats.totalDocuments}
          sub="Knowledge Base" iconBg="bg-info bg-opacity-15" iconColor="text-info" />
        <StatCard icon={Bot} label="AI Interactions" value={stats.aiInteractions}
          sub={<><Zap size={12} className="me-1" />Logged Operations</>}
          iconBg="bg-success bg-opacity-15" iconColor="text-success" />
      </div>

      <div className="row g-4 mb-4">
        <div className="col-12 col-xl-8">
          <div className="glass-card p-4 h-100">
            <h5 className="text-white mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>AI Activity by Type</h5>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#111425', borderColor: 'rgba(99,102,241,0.2)', color: '#fff', borderRadius: '8px' }} />
                  <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-muted py-5">No AI interactions yet. Upload documents or use the chatbot.</div>
            )}
          </div>
        </div>

        <div className="col-12 col-xl-4">
          <div className="glass-card p-4 h-100">
            <h5 className="text-white mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>Task Pipeline</h5>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={taskDistribution}>
                <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#111425', borderColor: 'rgba(99,102,241,0.1)', color: '#fff', borderRadius: '8px' }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {taskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-12 col-xl-6">
          <div className="glass-card p-4 h-100 ai-pulse-panel">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div className="d-flex align-items-center gap-2">
                <Cpu className="text-primary spin-slow" size={22} />
                <h5 className="text-white m-0" style={{ fontFamily: 'Outfit, sans-serif' }}>AI Agent Activity</h5>
              </div>
              <span className="badge text-primary border border-primary" style={{ backgroundColor: 'rgba(99,102,241,0.15)', fontSize: '0.7rem' }}>
                LIVE DATA
              </span>
            </div>
            <div className="d-flex flex-column gap-3">
              {aiLogs.length === 0 ? (
                <p className="text-muted small">No agent runs yet. Try the AI Agent page.</p>
              ) : aiLogs.map((log) => (
                <div key={log.id} className="d-flex align-items-center justify-content-between p-2 rounded-3"
                  style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                  <div className="d-flex align-items-center gap-2">
                    <div className="text-primary p-2 rounded-circle" style={{ backgroundColor: 'rgba(99,102,241,0.1)' }}>
                      <Database size={15} />
                    </div>
                    <div>
                      <div className="text-white fw-semibold small">{log.agent}</div>
                      <div className="text-muted" style={{ fontSize: '0.75rem' }}>{log.action}</div>
                    </div>
                  </div>
                  <div className="text-end">
                    <span className={`badge ${log.status === 'SUCCESS' ? 'text-success' : 'text-warning'} small`}
                      style={{ backgroundColor: log.status === 'SUCCESS' ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', fontSize: '0.65rem' }}>
                      {log.status}
                    </span>
                    <div className="text-muted mt-1" style={{ fontSize: '0.65rem' }}>{log.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-12 col-xl-6">
          <div className="glass-card p-4 h-100">
            <h5 className="text-white mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>Recent Activity Log</h5>
            <div className="d-flex flex-column gap-3">
              {activities.length === 0 ? (
                <div className="text-center text-muted py-4">No recent activity.</div>
              ) : activities.map((act) => (
                <div key={act.id} className="d-flex align-items-center justify-content-between pb-2"
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <div className="d-flex align-items-center gap-2">
                    <div className="text-secondary d-flex align-items-center justify-content-center rounded-3"
                      style={{ width: '32px', height: '32px', backgroundColor: 'rgba(107,114,128,0.1)' }}>
                      <Activity size={14} />
                    </div>
                    <div>
                      <div className="text-white small fw-medium">{act.action}</div>
                      <div className="text-muted" style={{ fontSize: '0.72rem' }}>{act.details?.message || 'System event'}</div>
                    </div>
                  </div>
                  <div className="text-muted" style={{ fontSize: '0.7rem' }}>
                    {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
