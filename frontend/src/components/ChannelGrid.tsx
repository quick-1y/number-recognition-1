import { ChannelInfo } from '../types';

interface Props {
  channels: ChannelInfo[];
  layout: '1x1' | '1x2' | '2x2' | '2x3' | '3x3';
  onLayoutChange: (value: Props['layout']) => void;
}

const layoutOptions: Props['layout'][] = ['1x1', '1x2', '2x2', '2x3', '3x3'];

export function ChannelGrid({ channels, layout, onLayoutChange }: Props) {
  const gridClass = `grid-${layout}`;
  const visibleByLayout: Record<Props['layout'], number> = {
    '1x1': 1,
    '1x2': 2,
    '2x2': 4,
    '2x3': 6,
    '3x3': 9
  };
  const visibleChannels = channels.slice(0, visibleByLayout[layout]);

  return (
    <div className="card">
      <div className="card-header">
        <div className="layout-options">
          {layoutOptions.map((opt) => (
            <button
              key={opt}
              className={opt === layout ? 'btn primary' : 'btn ghost'}
              onClick={() => onLayoutChange(opt)}
            >
              {opt}
            </button>
          ))}
        </div>
        <div className="legend">
          <span className="badge success">Online</span>
          <span className="badge warning">Degraded</span>
          <span className="badge error">Offline</span>
        </div>
      </div>
      <div className={`channel-grid ${gridClass}`}>
        {visibleChannels.map((ch) => (
          <div key={ch.id} className={`channel-tile status-${ch.status}`}>
            <div className="channel-name">{ch.name}</div>
            <div className="channel-meta">{ch.fps} fps</div>
            <div className="channel-status">{ch.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
