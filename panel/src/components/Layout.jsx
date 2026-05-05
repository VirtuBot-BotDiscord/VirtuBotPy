import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function Layout({ children }) {
  return (
    <div className="page-container">
      <aside className="panel-sidebar">
        <Sidebar />
      </aside>
      <div className="main-frame">
        <Topbar />
        <main className="layout-main">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
}
