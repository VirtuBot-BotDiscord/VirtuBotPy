import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';

const routeTitles = {
  '/dashboard': 'Dashboard',
  '/commands': 'Commandes',
  '/members': 'Membres',
  '/logs': 'Logs',
  '/keys': 'Générateur de clés',
  '/settings': 'Paramètres',
  '/setup': 'Configuration initiale',
  '/setup/bot': 'Configuration du bot'
};

export default function Topbar() {
  const location = useLocation();

  const title = useMemo(() => {
    return routeTitles[location.pathname] || 'Dashboard';
  }, [location.pathname]);

  return (
    <div className="topbar-shell">
      <div>
        <p className="eyebrow">Espace de contrôle</p>
        <h1>{title}</h1>
      </div>
      <div className="topbar-actions">
        <span className="status-chip online">En ligne</span>
      </div>
    </div>
  );
}
