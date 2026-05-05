import { useEffect, useState } from 'react';
import { fetchGuilds } from '../services/api';

export default function Guilds() {
  const [guilds, setGuilds] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadGuilds() {
      try {
        const data = await fetchGuilds();
        setGuilds(data);
      } catch (err) {
        setError(err.message);
      }
    }

    loadGuilds();
  }, []);

  return (
    <div className="animate-page">
      <div className="section">
        <div className="section-title">Serveurs</div>
        <p className="feedback">Liste des guildes que le bot a rejoint.</p>
      </div>

      {error && (
        <div className="card">
          <strong>Erreur :</strong> {error}
        </div>
      )}

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Nom</th>
              <th>Membres</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            {guilds.length > 0 ? (
              guilds.map((guild) => (
                <tr key={guild.id}>
                  <td>{guild.name}</td>
                  <td>{guild.memberCount}</td>
                  <td>{guild.ownerId}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3">Chargement des serveurs...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
