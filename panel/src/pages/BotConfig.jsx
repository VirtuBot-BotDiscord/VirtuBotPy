import { useState } from 'react';
import Button from '../components/Button';

export default function BotConfig() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ token: '', clientId: '', guildId: '', port: '3001', adminName: '', adminPassword: '', confirmPassword: '' });
  const [status, setStatus] = useState('');

  const handleChange = (key) => (event) => setForm((prev) => ({ ...prev, [key]: event.target.value }));
  const nextStep = () => setStep((current) => Math.min(current + 1, 3));

  return (
    <div className="animate-page" style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: '40px' }}>
      <div className="card" style={{ width: '100%', maxWidth: 640 }}>
        <div className="card-title">Configuration du bot</div>
        <div className="control-bar" style={{ marginBottom: '24px' }}>
          {['Code', 'Config', 'Terminé'].map((label, index) => (
            <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'center' }}>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: index + 1 <= step ? 'var(--accent)' : 'var(--bg-overlay)', display: 'grid', placeItems: 'center', color: index + 1 <= step ? 'var(--text-inverse)' : 'var(--text-secondary)' }}>{index + 1}</div>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{label}</span>
            </div>
          ))}
        </div>

        {step === 1 && (
          <div className="input-group">
            <label className="input-label">Token du bot</label>
            <input className="input-field" value={form.token} onChange={handleChange('token')} />
            <label className="input-label">Client ID</label>
            <input className="input-field" value={form.clientId} onChange={handleChange('clientId')} />
            <label className="input-label">Guild ID</label>
            <input className="input-field" value={form.guildId} onChange={handleChange('guildId')} />
            <Button type="button" variant="primary" onClick={nextStep}>Continuer</Button>
          </div>
        )}

        {step === 2 && (
          <div className="input-group">
            <label className="input-label">Port de l'API</label>
            <input className="input-field" value={form.port} onChange={handleChange('port')} />
            <label className="input-label">Nom admin</label>
            <input className="input-field" value={form.adminName} onChange={handleChange('adminName')} />
            <label className="input-label">Mot de passe</label>
            <input className="input-field" type="password" value={form.adminPassword} onChange={handleChange('adminPassword')} />
            <label className="input-label">Confirmer le mot de passe</label>
            <input className="input-field" type="password" value={form.confirmPassword} onChange={handleChange('confirmPassword')} />
            <Button type="button" variant="primary" onClick={() => { setStatus('Vérification du token…'); setTimeout(() => { setStatus('Connexion à Discord…'); setTimeout(() => { setStatus('Enregistrement des commandes…'); setTimeout(() => { setStep(3); setStatus('Prêt.'); }, 800); }, 800); }, 800); }}>Démarrer le bot</Button>
            {status && <p className="hero-meta">{status}</p>}
          </div>
        )}

        {step === 3 && (
          <div className="input-group">
            <div className="card card-soft">
              <div className="card-title">Statut</div>
              <p className="hero-meta">Votre configuration est prête. Le bot va démarrer automatiquement.</p>
            </div>
            <Button type="button" variant="primary">Retour au dashboard</Button>
          </div>
        )}
      </div>
    </div>
  );
}
