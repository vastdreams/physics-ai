/**
 * PATH: frontend/src/App.jsx
 * PURPOSE: Main application component with routing configuration
 * 
 * FLOW:
 * ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
 * │   Router    │───▶│    Layout    │───▶│    Pages    │
 * │   Config    │    │   (Sidebar)  │    │  (Content)  │
 * └─────────────┘    └──────────────┘    └─────────────┘
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Simulations from './pages/Simulations';
import Equations from './pages/Equations';
import Knowledge from './pages/Knowledge';
import Models from './pages/Models';
import Rules from './pages/Rules';
import Evolution from './pages/Evolution';
import Reasoning from './pages/Reasoning';
import Logs from './pages/Logs';
import Metrics from './pages/Metrics';
import Settings from './pages/Settings';
import About from './pages/About';
import NotFound from './pages/NotFound';
import UpdateBanner from './components/UpdateBanner';

/** Root application component — sets up routing and global layout. */
function App() {
  return (
    <BrowserRouter>
      <UpdateBanner />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="simulations" element={<Simulations />} />
          <Route path="equations" element={<Equations />} />
          <Route path="knowledge" element={<Knowledge />} />
          <Route path="models" element={<Models />} />
          <Route path="rules" element={<Rules />} />
          <Route path="evolution" element={<Evolution />} />
          <Route path="reasoning" element={<Reasoning />} />
          <Route path="logs" element={<Logs />} />
          <Route path="metrics" element={<Metrics />} />
          <Route path="settings" element={<Settings />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
