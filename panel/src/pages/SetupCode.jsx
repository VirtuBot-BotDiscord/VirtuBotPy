import { useMemo, useState } from 'react';
import Button from '../components/Button';

const CODE_PATTERN = /^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/;

export default function SetupCode() {
  const [code, setCode] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const normalized = useMemo(() => code.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12), [code]);
  const formatted = useMemo(() => normalized.replace(/(.{4})/g, '$1-').trim().replace(/-$/, ''), [normalized]);
  const valid = CODE_PATTERN.test(formatted);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (valid) {
      setSubmitted(true);
    }
  };

  return (
    <div className="animate-page" style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: '40px' }}>
      <div className="card" style={{ maxWidth: 480, width: '100%' }}>
        <div className="card-title">Configuration initiale</div>
        <p className="hero-meta">Entrez le code d’activation affiché dans le terminal pour démarrer le panneau.</p>

        <form onSubmit={handleSubmit} className="input-group" style={{ marginTop: '24px' }}>
          <label className="input-label">Code d'activation</label>
          <input
            className="input-field"
            value={formatted}
            onChange={(event) => setCode(event.target.value)}
            placeholder="XXXX-XXXX-XXXX"
            autoFocus
          />
          <Button type="submit" variant="primary" disabled={!valid}>{submitted ? 'Validé' : 'Continuer'}</Button>
          {!valid && formatted.length >= 1 ? (
            <p className="hero-meta" style={{ color: 'var(--text-secondary)' }}>Le code doit être au format XXXX-XXXX-XXXX.</p>
          ) : null}
        </form>
      </div>
    </div>
  );
}
