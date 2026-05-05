import { useEffect, useState } from 'react';
import { fetchBotStats } from '../services/api';

const activityPoints = [24, 32, 28, 35, 42, 38, 44];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await fetchBotStats();
        setStats(data);
      } catch (err) {
        setError(err.message);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="animate-page panel-grid">
      <section className="card card-hero animate-item">
        <div className="card-title">Vue d’ensemble</div>
        <div className="hero-grid">
          <div>
            <p className="hero-label">Bot connecté</p>
            <h2 className="hero-value">{stats?.username ? `${stats.username}#${stats.discriminator}` : 'Chargement...'}</h2>
            <p className="hero-meta">ID : {stats?.id ?? '...'}</p>
          </div>
          <div className="status-stack">
            <span className="badge badge-success">En ligne</span>
            <span className="badge badge-neutral">{stats?.guilds ?? '...'} serveurs</span>
            <span className="badge badge-neutral">{stats?.users ?? '...'} membres</span>
          </div>
        </div>
      </section>

      {error && (
        <section className="card animate-item">
          <div className="card-title">Erreur</div>
          <p style={{ color: 'var(--red)' }}>{error}</p>
        </section>
      )}

      <section className="grid-4 animate-item">
        <div className="card">
          <div className="card-title">Serveurs</div>
          <p className="hero-value">{stats?.guilds ?? '...'}</p>
          <p className="hero-meta">Nombre de guildes actives</p>
        </div>
        <div className="card">
          <div className="card-title">Membres</div>
          <p className="hero-value">{stats?.users ?? '...'}</p>
          <p className="hero-meta">Total des membres servis</p>
        </div>
        <div className="card">
          <div className="card-title">Latence</div>
          <p className="hero-value">{stats?.latency ? `${stats.latency} ms` : '...'}</p>
          <p className="hero-meta">Round-trip du bot</p>
        </div>
        <div className="card">
          <div className="card-title">Commandes</div>
          <p className="hero-value">{stats ? stats.guilds * 4 : '...'}</p>
          <p className="hero-meta">Estimé actif</p>
        </div>
      </section>

      <section className="card animate-item">
        <div className="card-title">Activité récente</div>
        <div className="sparkline" role="img" aria-label="Graphique d'activité">
          {activityPoints.map((value, index) => (
            <div key={index} className="sparkline-bar" style={{ height: `${value}%` }} />
          ))}
        </div>
        <div className="control-bar" style={{ marginTop: '18px' }}>
          <span className="badge badge-info">+14% cette semaine</span>
          <span className="hero-meta">Messages et commandes</span>
        </div>
      </section>
    </div>
  );
}
