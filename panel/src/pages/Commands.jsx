import { useEffect, useMemo, useState } from 'react';
import { fetchCommands } from '../services/api';

const commandStatus = ['Active', 'Inactive'];

export default function Commands() {
  const [commands, setCommands] = useState([]);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('Toutes');
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadCommands() {
      try {
        const data = await fetchCommands();
        setCommands(data);
      } catch (err) {
        setError(err.message);
      }
    }
    loadCommands();
  }, []);

  const filteredCommands = useMemo(() => {
    return commands
      .filter((command) => command.name.toLowerCase().includes(search.toLowerCase()))
      .filter((command) => (filter === 'Toutes' ? true : command.category === filter));
  }, [commands, search, filter]);

  return (
    <div className="animate-page panel-grid">
      <section className="card animate-item">
        <div className="card-title">Commandes</div>
        <div className="control-bar">
          <input
            className="input-field"
            placeholder="Rechercher une commande..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select className="select-field" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option>Toutes</option>
            <option>Jeux</option>
            <option>Tickets</option>
            <option>Administration</option>
            <option>Utilitaires</option>
          </select>
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
              <th>Commande</th>
              <th>Description</th>
              <th>Catégorie</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {filteredCommands.length > 0 ? (
              filteredCommands.map((command, index) => (
                <tr key={command.name} style={{ animationDelay: `${index * 30}ms` }} className="animate-item">
                  <td><span className="member-name">/{command.name}</span></td>
                  <td>{command.description}</td>
                  <td>{command.category}</td>
                  <td>
                    <span className={`badge ${commandStatus[index % 2] === 'Active' ? 'badge-success' : 'badge-neutral'}`}>
                      {commandStatus[index % 2]}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">Chargement des commandes...</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
