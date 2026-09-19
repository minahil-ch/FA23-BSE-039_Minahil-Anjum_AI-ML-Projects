import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ScrollText, Search, RefreshCw, AlertCircle } from 'lucide-react';

const ActivityLogList = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    setError('');
    try {
      let url = 'activity-logs/?';
      if (searchTerm) {
        url += `search=${searchTerm}`;
      }
      const response = await api.get(url);
      setLogs(response.data.results || response.data);
    } catch (e) {
      console.error(e);
      setError('Failed to fetch activity logs directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [searchTerm]);

  return (
    <div className="animate-slide-in">
      <div className="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
        <div>
          <h2 className="text-white m-0 font-title">System Activity Log</h2>
          <p className="text-muted">Audit trail tracking authentication, task mutations, and document uploads.</p>
        </div>
        <button 
          onClick={fetchLogs}
          className="btn btn-outline-secondary border-opacity-25 rounded-3 d-flex align-items-center gap-2 text-light hover-bg"
        >
          <RefreshCw size={16} />
          <span>Reload logs</span>
        </button>
      </div>

      {error && (
        <div className="alert alert-danger bg-danger bg-opacity-10 border-danger border-opacity-25 text-danger d-flex align-items-center gap-2 mb-4 py-2 px-3 rounded-3">
          <AlertCircle size={16} />
          <span className="small">{error}</span>
        </div>
      )}

      {/* Log Search */}
      <div className="glass-card p-3 mb-4 d-flex align-items-center gap-2">
        <Search className="text-muted" size={18} />
        <input 
          type="text" 
          className="form-control border-0 bg-transparent p-0 shadow-none text-white w-100" 
          placeholder="Search activity actions or details (e.g. USER_LOGIN)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ background: 'transparent !important', border: 'none !important' }}
        />
      </div>

      {/* Log Table List */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status"></div>
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center glass-card p-5 text-muted">No audit logs found.</div>
      ) : (
        <div className="glass-card overflow-hidden">
          <div className="table-responsive">
            <table className="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Operator</th>
                  <th>Action</th>
                  <th>Detail Audit Summary</th>
                  <th>IP Address</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="text-secondary small" style={{ whiteSpace: 'nowrap' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td>
                      <div className="d-flex align-items-center gap-2">
                        <div className="bg-secondary bg-opacity-20 text-secondary rounded-circle d-flex align-items-center justify-content-center fw-bold" style={{ width: '28px', height: '28px', fontSize: '0.8rem' }}>
                          {log.user_detail ? log.user_detail.username.substring(0, 2).toUpperCase() : 'SYS'}
                        </div>
                        <span className="text-white fw-semibold small">
                          {log.user_detail ? `${log.user_detail.first_name} ${log.user_detail.last_name}` : 'System Agent'}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="badge bg-secondary bg-opacity-15 text-secondary-emphasis border border-secondary border-opacity-35 px-2 py-0.5" style={{ fontSize: '0.7rem' }}>
                        {log.action}
                      </span>
                    </td>
                    <td className="text-secondary small" style={{ maxWidth: '350px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {log.details?.message || JSON.stringify(log.details)}
                    </td>
                    <td className="text-muted small">{log.ip_address || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityLogList;
export { ActivityLogList };
