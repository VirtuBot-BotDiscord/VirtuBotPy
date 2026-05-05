import { useMemo, useState } from 'react';
import Button from '../components/Button';

const types = [
  { id: 'silver', label: 'Silver', color: 'badge-neutral', description: 'Accès fonctionnalités de base' },
  { id: 'gold', label: 'Gold', color: 'badge-warning', description: 'Fonctionnalités avancées' },
  { id: 'diamond', label: 'Diamond', color: 'badge-info', description: 'Accès complet' },
  { id: 'premium', label: 'Premium', color: 'badge-success', description: 'Support prioritaire' },
  { id: 'lifetime', label: 'Lifetime', color: 'badge-danger', description: 'Accès permanent' }
];

const generateKey = () => Array.from({ length: 20 }, () => Math.random().toString(36)[2] || 'A').join('').toUpperCase();

export default function KeyGenerator() {
  const [selectedType, setSelectedType] = useState('silver');
  const [duration, setDuration] = useState(30);
  const [quantity, setQuantity] = useState(5);
  const [note, setNote] = useState('');
  const [keys, setKeys] = useState([]);

  const selected = useMemo(() => types.find((item) => item.id === selectedType), [selectedType]);

  const handleGenerate = () => {
    const newKeys = Array.from({ length: quantity }, () => ({
      code: generateKey(),
      type: selected.label,
      expires: selected.id === 'lifetime' ? '♾ Illimité' : `dans ${duration} jours`,
      status: 'Active'
    }));
    setKeys((prev) => [...newKeys, ...prev]);
  };

  return (
    <div className="animate-page panel-grid">
      <section className="card animate-item">
        <div className="card-title">Générer des clés</div>
        <div className="control-bar" style={{ flexWrap: 'wrap' }}>
          {types.map((type) => (
            <button
              key={type.id}
              type="button"
              className={`button button-ghost ${selectedType === type.id ? 'active' : ''}`}
              onClick={() => setSelectedType(type.id)}
            >
              {type.label}
            </button>
          ))}
        </div>

        <div className="input-group">
          {selected.id !== 'lifetime' ? (
            <>
              <label className="input-label">Durée (jours)</label>
              <input
                className="input-field"
                type="number"
                min="1"
                max="365"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </>
          ) : (
            <div className="hero-meta">♾ Illimité — aucune expiration</div>
          )}

          <label className="input-label">Quantité</label>
          <input
            className="input-field"
            type="number"
            min="1"
            max="100"
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
          />

          <label className="input-label">Note</label>
          <textarea
            className="textarea-field"
            rows="3"
            placeholder="Note interne (optionnel)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />

          <Button type="button" variant="primary" onClick={handleGenerate}>Générer</Button>
        </div>
      </section>

      <section className="card animate-item">
        <div className="card-title">Clés générées</div>
        <div className="hero-meta" style={{ marginBottom: '16px' }}>Les dernières clés générées apparaissent ici.</div>
        <table className="table">
          <thead>
            <tr>
              <th>Clé</th>
              <th>Type</th>
              <th>Statut</th>
              <th>Expiration</th>
            </tr>
          </thead>
          <tbody>
            {keys.length > 0 ? (
              keys.map((entry, index) => (
                <tr key={`${entry.code}-${index}`}>
                  <td>{entry.code}</td>
                  <td>{entry.type}</td>
                  <td><span className="badge badge-success">{entry.status}</span></td>
                  <td>{entry.expires}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">Aucune clé générée pour l'instant.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
