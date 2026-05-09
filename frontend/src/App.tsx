import { useState } from 'react';
import { ChatAssistant } from './components/ChatAssistant';
import { Header } from './components/Header';
import { HistoryPanel } from './components/HistoryPanel';
import { InsightsPanel } from './components/InsightsPanel';
import { SettingsPanel } from './components/SettingsPanel';
import type { AssistantSettings, ChatMessage } from './types/api';
import './styles.css';

const defaultSettings: AssistantSettings = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
  apiKey: import.meta.env.VITE_ASSISTANT_API_KEY ?? 'dev-internal-key',
  role: 'analyst',
  year: 2025,
  month: '2025-12',
  isAuthenticated: false,
};

function App() {
  const [settings, setSettings] = useState<AssistantSettings>(defaultSettings);
  const [history, setHistory] = useState<ChatMessage[]>([]);

  return (
    <main className="app-shell">
      <Header />
      <div className="layout-grid">
        <aside className="sidebar">
          <SettingsPanel settings={settings} onChange={setSettings} />
          <HistoryPanel messages={history} />
        </aside>
        <ChatAssistant settings={settings} onHistoryChange={setHistory} />
        <InsightsPanel settings={settings} />
      </div>
    </main>
  );
}

export default App;