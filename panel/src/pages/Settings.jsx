import { useEffect, useState } from 'react';
import Button from '../components/Button';
import { fetchAdminStats, restartBot } from '../services/api';

export default function Settings() {
  const [apiUrl, setApiUrl] = useState('http://localhost:3001');
  const [adminStats, setAdminStats] = useState(null);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await fetchAdminStats();
        setAdminStats(data);
      } catch (err) {
        setError(err.message);
      }
    }

    loadStats();
  }, []);

  const handleRestart = async () => {
    try {
      setError(null);
      const result = await restartBot();
      setMessage(result.message || 'Redémarrage demandé.');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="animate-page panel-grid">
      {error && (
        <section className="card animate-item">
          <div className="card-title">Erreur</div>
          <p style={{ color: 'var(--red)' }}>{error}</p>
        </section>
      )}

      {message && (
        <section className="card animate-item">
          <div className="card-title">Succès</div>
          <p style={{ color: 'var(--green)' }}>{message}</p>
        </section>
      )}

      <section className="card animate-item">
        <div className="card-title">Paramètres du panel</div>
        <div className="input-group">
          <label className="input-label">URL de l'API</label>
          <input
            className="input-field"
            value={apiUrl}
            onChange={(event) => setApiUrl(event.target.value)}
          />
        </div>
        <div className="button-row">
          <Button variant="secondary">Sauvegarder</Button>
        </div>
      </section>

      <section className="card animate-item">
        <div className="card-title">État du bot</div>
        <div className="grid-2">
          <div className="card card-soft">
            <p className="hero-label">Uptime</p>
            <strong className="hero-value">{adminStats?.uptime?.formatted ?? 'N/A'}</strong>
          </div>
          <div className="card card-soft">
            <p className="hero-label">Latence</p>
            <strong className="hero-value">{adminStats?.latency ? `${adminStats.latency} ms` : 'N/A'}</strong>
          </div>
          <div className="card card-soft">
            <p className="hero-label">Guildes</p>
            <strong className="hero-value">{adminStats?.guilds?.total ?? 'N/A'}</strong>
          </div>
          <div className="card card-soft">
            <p className="hero-label">Membres</p>
            <strong className="hero-value">{adminStats?.members?.total ?? 'N/A'}</strong>
          </div>
        </div>
        <div className="button-row" style={{ marginTop: '16px' }}>
          <Button variant="danger" onClick={handleRestart}>Redémarrer le bot</Button>
          <Button variant="secondary">Exporter la config</Button>
        </div>
      </section>
    </div>
  );
}
