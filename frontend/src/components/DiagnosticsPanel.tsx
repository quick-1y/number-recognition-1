import { ChannelInfo } from '../types';

interface Props {
  channels: ChannelInfo[];
}

const sampleMetrics = [
  { label: 'Средняя задержка', value: '420 ms' },
  { label: 'Ошибки OCR', value: '0.8% за 10 мин' },
  { label: 'Dropped frames', value: '0.5% за 10 мин' }
];

export function DiagnosticsPanel({ channels }: Props) {
  return (
    <div className="card">
      <div className="metrics">
        {sampleMetrics.map((m) => (
          <div key={m.label} className="metric">
            <div className="muted">{m.label}</div>
            <div className="metric-value">{m.value}</div>
          </div>
        ))}
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Канал</th>
            <th>FPS</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {channels.map((ch) => (
            <tr key={ch.id}>
              <td>{ch.name}</td>
              <td>{ch.fps}</td>
              <td>{ch.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
