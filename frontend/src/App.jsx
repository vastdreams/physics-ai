/**
 * PATH: frontend/src/App.jsx
 * PURPOSE: Main application component with routing and authentication
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/layout/Layout';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Signup from './pages/Signup';
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
import Documentation from './pages/Documentation';
import NotFound from './pages/NotFound';
import UpdateBanner from './components/UpdateBanner';

/** Root application component — auth, routing, and global layout. */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <UpdateBanner />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/docs" element={<Documentation />} />

          {/* Protected app routes */}
          <Route element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route path="dashboard" element={<Dashboard />} />
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
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
