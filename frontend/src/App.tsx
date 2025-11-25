import { useMemo, useState } from 'react';
import { ChannelGrid } from './components/ChannelGrid';
import { EventsTable } from './components/EventsTable';
import { SearchPanel } from './components/SearchPanel';
import { ListsPanel } from './components/ListsPanel';
import { SettingsPanel } from './components/SettingsPanel';
import { DiagnosticsPanel } from './components/DiagnosticsPanel';
import { useAuthToken } from './hooks/useAuthToken';
import { Tab } from './types';
import { TopBar } from './components/TopBar';
import { Section } from './components/Section';

const initialChannels = [
  { id: 'cam-north', name: 'Cam North', fps: 12, status: 'online' as const },
  { id: 'cam-south', name: 'Cam South', fps: 11, status: 'online' as const },
  { id: 'cam-east', name: 'Cam East', fps: 9, status: 'degraded' as const },
  { id: 'cam-west', name: 'Cam West', fps: 12, status: 'offline' as const }
];

const sampleEvents = [
  {
    id: 'evt-1',
    plate: 'A123BC77',
    timestamp: '2024-05-20T08:12:00Z',
    channel: 'cam-north',
    confidence: 0.91,
    list: 'white'
  },
  {
    id: 'evt-2',
    plate: 'B456CD55',
    timestamp: '2024-05-20T08:13:10Z',
    channel: 'cam-east',
    confidence: 0.73,
    list: 'info'
  },
  {
    id: 'evt-3',
    plate: 'C789EF90',
    timestamp: '2024-05-20T08:14:32Z',
    channel: 'cam-west',
    confidence: 0.62,
    list: 'black'
  }
];

export default function App() {
  const { token, role, saveToken } = useAuthToken();
  const [activeTab, setActiveTab] = useState<Tab>('grid');
  const [layout, setLayout] = useState<'1x1' | '1x2' | '2x2' | '2x3' | '3x3'>('2x2');
  const [showMasked, setShowMasked] = useState<boolean>(role === 'viewer');

  const maskedEvents = useMemo(
    () =>
      sampleEvents.map((evt) => ({
        ...evt,
        plate:
          showMasked || role === 'viewer'
            ? evt.plate.replace(/[A-Z0-9]/g, '*')
            : evt.plate
      })),
    [showMasked, role]
  );

  const tabs: { id: Tab; label: string }[] = [
    { id: 'grid', label: 'Каналы' },
    { id: 'events', label: 'События' },
    { id: 'search', label: 'Поиск' },
    { id: 'lists', label: 'Списки' },
    { id: 'settings', label: 'Настройки' },
    { id: 'diagnostics', label: 'Диагностика' }
  ];

  return (
    <div className="app">
      <TopBar
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        token={token}
        role={role}
        onSaveToken={(value, userRole) => {
          saveToken(value, userRole);
          setShowMasked(userRole === 'viewer');
        }}
        onToggleMask={() => setShowMasked((prev) => !prev)}
        showMasked={showMasked}
      />

      <main className="content">
        {activeTab === 'grid' && (
          <Section title="Сетка каналов" subtitle="1×1, 1×2, 2×2, 2×3, 3×3">
            <ChannelGrid
              channels={initialChannels}
              layout={layout}
              onLayoutChange={setLayout}
            />
          </Section>
        )}

        {activeTab === 'events' && (
          <Section
            title="Последние события"
            subtitle="До 100 последних событий с учётом маскирования ролей"
          >
            <EventsTable events={maskedEvents} />
          </Section>
        )}

        {activeTab === 'search' && (
          <Section
            title="Поиск"
            subtitle="Фильтры: дата/время, канал, список, маска номера"
          >
            <SearchPanel onSubmit={(filters) => console.log('search', filters)} />
          </Section>
        )}

        {activeTab === 'lists' && (
          <Section
            title="Списки"
            subtitle="Белый/чёрный/информационный. Импорт/экспорт CSV/JSON"
          >
            <ListsPanel />
          </Section>
        )}

        {activeTab === 'settings' && (
          <Section
            title="Настройки"
            subtitle="Общие, каналы, реле, API/Webhooks, шаблоны стран"
          >
            <SettingsPanel />
          </Section>
        )}

        {activeTab === 'diagnostics' && (
          <Section
            title="Диагностика"
            subtitle="FPS, задержка, ошибки OCR, статусы сервисов"
          >
            <DiagnosticsPanel channels={initialChannels} />
          </Section>
        )}
      </main>
    </div>
  );
}
