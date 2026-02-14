/**
 * PATH: frontend/src/pages/Settings.jsx
 * PURPOSE: System configuration and settings
 */

import { useState } from 'react';
import {
  Settings as SettingsIcon,
  Server,
  Database,
  Bell,
  Shield,
  Palette,
  Save,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';
import { clsx } from 'clsx';
import { API_BASE } from '../config';

function SettingSection({ title, description, icon: Icon, children }) {
  return (
    <div className="card">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-10 h-10 rounded-lg bg-light-200 flex items-center justify-center flex-shrink-0">
          <Icon size={20} className="text-light-600" />
        </div>
        <div>
          <h3 className="font-medium text-light-800">{title}</h3>
          <p className="text-sm text-light-500">{description}</p>
        </div>
      </div>
      <div className="space-y-4 pl-14">
        {children}
      </div>
    </div>
  );
}

function Toggle({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between py-2">
      <div>
        <p className="text-sm text-light-700">{label}</p>
        {description && <p className="text-xs text-light-400">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={clsx(
          'relative w-11 h-6 rounded-full transition-colors',
          checked ? 'bg-accent-primary' : 'bg-light-300'
        )}
      >
        <span
          className={clsx(
            'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform shadow-sm',
            checked ? 'left-6' : 'left-1'
          )}
        />
      </button>
    </div>
  );
}

function Input({ label, description, value, onChange, type = 'text', placeholder }) {
  return (
    <div className="py-2">
      <label className="text-sm text-light-700 block mb-1">{label}</label>
      {description && <p className="text-xs text-light-400 mb-2">{description}</p>}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="input"
      />
    </div>
  );
}

function Select({ label, description, value, onChange, options }) {
  return (
    <div className="py-2">
      <label className="text-sm text-light-700 block mb-1">{label}</label>
      {description && <p className="text-xs text-light-400 mb-2">{description}</p>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input appearance-none"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

export default function Settings() {
  const [settings, setSettings] = useState({
    apiUrl: API_BASE || 'http://localhost:5002',
    autoConnect: true,
    enableWebSocket: true,
    logLevel: 'info',
    maxSimulationTime: 100,
    defaultIntegrationMethod: 'rk4',
    enableNotifications: true,
    soundEnabled: false,
    darkMode: false,
    compactView: false,
    enableEvolution: true,
    requireApproval: true,
  });

  const [saved, setSaved] = useState(false);

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    // Save to localStorage
    localStorage.setItem('beyondfrontier-settings', JSON.stringify(settings));
    // Also try to sync with backend
    try {
      await fetch(`${API_BASE}/api/v1/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
    } catch {
      // Backend unavailable — local save is enough
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    const defaultSettings = {
      apiUrl: API_BASE || 'http://localhost:5002',
      autoConnect: true,
      enableWebSocket: true,
      logLevel: 'info',
      maxSimulationTime: 100,
      defaultIntegrationMethod: 'rk4',
      enableNotifications: true,
      soundEnabled: false,
      darkMode: false,
      compactView: false,
      enableEvolution: true,
      requireApproval: true,
    };
    setSettings(defaultSettings);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-light-900">Settings</h1>
          <p className="text-light-500 text-sm">Configure your Beyond Frontier environment</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleReset} className="btn-secondary flex items-center gap-2">
            <RefreshCw size={16} />
            Reset
          </button>
          <button onClick={handleSave} className="btn-primary flex items-center gap-2">
            {saved ? <CheckCircle2 size={16} /> : <Save size={16} />}
            {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* API Settings */}
      <SettingSection
        title="API Connection"
        description="Configure backend API settings"
        icon={Server}
      >
        <Input
          label="API URL"
          description="The URL of the Beyond Frontier backend server"
          value={settings.apiUrl}
          onChange={(v) => updateSetting('apiUrl', v)}
          placeholder={API_BASE || "http://localhost:5002"}
        />
        <Toggle
          label="Auto Connect"
          description="Automatically connect to API on startup"
          checked={settings.autoConnect}
          onChange={(v) => updateSetting('autoConnect', v)}
        />
        <Toggle
          label="Enable WebSocket"
          description="Real-time updates via WebSocket connection"
          checked={settings.enableWebSocket}
          onChange={(v) => updateSetting('enableWebSocket', v)}
        />
        <Select
          label="Log Level"
          description="Verbosity of console logging"
          value={settings.logLevel}
          onChange={(v) => updateSetting('logLevel', v)}
          options={[
            { value: 'debug', label: 'Debug' },
            { value: 'info', label: 'Info' },
            { value: 'warn', label: 'Warning' },
            { value: 'error', label: 'Error' },
          ]}
        />
      </SettingSection>

      {/* Simulation Settings */}
      <SettingSection
        title="Simulation"
        description="Default simulation parameters"
        icon={Database}
      >
        <Input
          label="Max Simulation Time (s)"
          description="Maximum duration for simulations"
          value={settings.maxSimulationTime}
          onChange={(v) => updateSetting('maxSimulationTime', parseInt(v) || 100)}
          type="number"
        />
        <Select
          label="Default Integration Method"
          description="Numerical integration method for simulations"
          value={settings.defaultIntegrationMethod}
          onChange={(v) => updateSetting('defaultIntegrationMethod', v)}
          options={[
            { value: 'euler', label: 'Euler (Fast)' },
            { value: 'rk4', label: 'RK4 (Recommended)' },
            { value: 'rk45', label: 'RK45 (Adaptive)' },
          ]}
        />
      </SettingSection>

      {/* Notification Settings */}
      <SettingSection
        title="Notifications"
        description="Alert and notification preferences"
        icon={Bell}
      >
        <Toggle
          label="Enable Notifications"
          description="Show browser notifications for events"
          checked={settings.enableNotifications}
          onChange={(v) => updateSetting('enableNotifications', v)}
        />
        <Toggle
          label="Sound Alerts"
          description="Play sound for important events"
          checked={settings.soundEnabled}
          onChange={(v) => updateSetting('soundEnabled', v)}
        />
      </SettingSection>

      {/* Evolution Settings */}
      <SettingSection
        title="Self-Evolution"
        description="Configure AI self-modification behavior"
        icon={Shield}
      >
        <Toggle
          label="Enable Evolution"
          description="Allow AI to propose code modifications"
          checked={settings.enableEvolution}
          onChange={(v) => updateSetting('enableEvolution', v)}
        />
        <Toggle
          label="Require Approval"
          description="Require human approval before applying changes"
          checked={settings.requireApproval}
          onChange={(v) => updateSetting('requireApproval', v)}
        />
      </SettingSection>

      {/* Appearance Settings */}
      <SettingSection
        title="Appearance"
        description="Customize the interface"
        icon={Palette}
      >
        <Toggle
          label="Dark Mode"
          description="Use dark color scheme"
          checked={settings.darkMode}
          onChange={(v) => updateSetting('darkMode', v)}
        />
        <Toggle
          label="Compact View"
          description="Reduce spacing for more content"
          checked={settings.compactView}
          onChange={(v) => updateSetting('compactView', v)}
        />
      </SettingSection>
    </div>
  );
}
