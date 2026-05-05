import { Route, Routes, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import SetupCode from './pages/SetupCode';
import BotConfig from './pages/BotConfig';
import Dashboard from './pages/Dashboard';
import Commands from './pages/Commands';
import Members from './pages/Members';
import Logs from './pages/Logs';
import KeyGenerator from './pages/KeyGenerator';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/setup" element={<SetupCode />} />
        <Route path="/setup/bot" element={<BotConfig />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/commands" element={<Commands />} />
        <Route path="/members" element={<Members />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/keys" element={<KeyGenerator />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}
