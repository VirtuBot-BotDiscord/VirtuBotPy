import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Command, Users, LogIn, Key, Settings } from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/commands', label: 'Commandes', icon: Command },
  { path: '/members', label: 'Membres', icon: Users },
  { path: '/logs', label: 'Logs', icon: LogIn },
  { path: '/keys', label: 'Clés', icon: Key },
  { path: '/settings', label: 'Paramètres', icon: Settings }
];

export default function Sidebar() {
  return (
    <div className="sidebar-shell">
      <div className="brand-block">
        <div className="brand-label">
          <span className="brand-mark" />
          <div>
            <p className="brand-overline">VirtuBot</p>
            <h2>Panel</h2>
          </div>
        </div>
      </div>

      <nav className="nav-list">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-foot">
        <div className="user-card">
          <div className="user-avatar">V</div>
          <div>
            <div className="user-name">Admin</div>
            <div className="user-meta">Super accès</div>
          </div>
        </div>
        <button className="ghost-button">Déconnexion</button>
      </div>
    </div>
  );
}
