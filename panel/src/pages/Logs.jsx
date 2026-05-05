import { useEffect, useMemo, useState } from 'react';
import { fetchLogs, clearLogs } from '../services/api';

const logTypes = ['JOIN', 'LEAVE', 'COMMAND', 'ERROR', 'ADMIN'];

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [selectedTypes, setSelectedTypes] = useState(new Set(logTypes));
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    async function loadLogs() {
      try {
        const data = await fetchLogs();
        setLogs(data);
      } catch (err) {
        setError(err.message);
      }
    }
    loadLogs();
  }, []);

  const filteredLogs = useMemo(() => {
    return logs.filter((log) => selectedTypes.has(log.status?.toUpperCase() || 'COMMAND'));
  }, [logs, selectedTypes]);

  const toggleType = (type) => {
    setSelectedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  };

  const handleClear = async () => {
    try {
      const result = await clearLogs();
      setMessage(result.message || 'Logs effacés.');
      setLogs([]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="animate-page panel-grid">
      <section className="card animate-item">
        <div className="card-title">Flux de logs</div>
        <div className="control-bar">
          <div className="control-group">
            {logTypes.map((type) => (
              <button
                key={type}
                type="button"
                className={`button button-ghost ${selectedTypes.has(type) ? 'active' : ''}`}
                onClick={() => toggleType(type)}
              >
                {type}
              </button>
            ))}
          </div>
          <button className="button button-secondary" onClick={handleClear}>Effacer</button>
        </div>
      </section>

      {message && (
        <section className="card animate-item">
          <div className="card-title">Succès</div>
          <p style={{ color: 'var(--green)' }}>{message}</p>
        </section>
      )}

      {error && (
        <section className="card animate-item">
          <div className="card-title">Erreur</div>
          <p style={{ color: 'var(--red)' }}>{error}</p>
        </section>
      )}

      <section className="card animate-item">
        <div className="card-title">Détails</div>
        <div className="log-list">
          {filteredLogs.length > 0 ? (
            filteredLogs.map((log, index) => (
              <div key={`${log.command ?? log.error_code}-${index}`} className="log-line animate-item" style={{ animationDelay: `${index * 20}ms` }}>
                <span className="log-time">{new Date(log.timestamp).toLocaleTimeString('fr-FR')}</span>
                <span className={`badge ${log.status === 'ERROR' ? 'badge-danger' : log.status === 'JOIN' ? 'badge-success' : log.status === 'LEAVE' ? 'badge-warning' : 'badge-info'}`}>
                  {log.status ?? 'COMMAND'}
                </span>
                <span className="log-message">{log.command || log.error_message || 'Événement inconnu'}</span>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p className="hero-meta">Aucun log disponible.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
