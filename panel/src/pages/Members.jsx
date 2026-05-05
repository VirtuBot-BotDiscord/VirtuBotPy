import { useEffect, useState } from 'react';
import { fetchGuilds } from '../services/api';

const sampleMembers = [
  { id: '1', name: 'Aline', role: 'Admin', joined: 'Il y a 2 mois' },
  { id: '2', name: 'Niko', role: 'Modérateur', joined: 'Il y a 15 jours' },
  { id: '3', name: 'Lena', role: 'Membre', joined: 'Il y a 4 jours' },
  { id: '4', name: 'Kenza', role: 'Membre', joined: 'Il y a 1 jour' }
];

export default function Members() {
  const [guilds, setGuilds] = useState([]);
  const [selectedGuild, setSelectedGuild] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadGuilds() {
      try {
        const data = await fetchGuilds();
        setGuilds(data);
        if (data.length > 0) setSelectedGuild(data[0].id);
      } catch (err) {
        setError(err.message);
      }
    }
    loadGuilds();
  }, []);

  return (
    <div className="animate-page panel-grid">
      <section className="card animate-item">
        <div className="card-title">Membres</div>
        <p className="hero-meta">Sélectionnez un serveur pour consulter les membres et leurs actions.</p>
        <div className="control-bar">
          <select className="select-field" value={selectedGuild} onChange={(e) => setSelectedGuild(e.target.value)}>
            {guilds.map((guild) => (
              <option key={guild.id} value={guild.id}>{guild.name}</option>
            ))}
          </select>
          <span className="badge badge-neutral">{guilds.length} servers</span>
        </div>
      </section>

      {error && (
        <section className="card animate-item">
          <div className="card-title">Erreur</div>
          <p style={{ color: 'var(--red)' }}>{error}</p>
        </section>
      )}

      <section className="card animate-item">
        <table className="table">
          <thead>
            <tr>
              <th>Membre</th>
              <th>Rôle</th>
              <th>Rejoint</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sampleMembers.map((member) => (
              <tr key={member.id}>
                <td>{member.name}</td>
                <td>{member.role}</td>
                <td>{member.joined}</td>
                <td><button className="button button-ghost">Voir</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
