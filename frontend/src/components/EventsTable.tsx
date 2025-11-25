import { EventItem } from '../types';

interface Props {
  events: EventItem[];
}

const listLabels: Record<string, string> = {
  white: 'Белый',
  black: 'Чёрный',
  info: 'Информационный'
};

export function EventsTable({ events }: Props) {
  return (
    <div className="card">
      <table className="table">
        <thead>
          <tr>
            <th>Номер</th>
            <th>Канал</th>
            <th>Уверенность</th>
            <th>Список</th>
            <th>Время</th>
          </tr>
        </thead>
        <tbody>
          {events.map((evt) => (
            <tr key={evt.id}>
              <td className="mono">{evt.plate}</td>
              <td>{evt.channel}</td>
              <td>{Math.round(evt.confidence * 100)}%</td>
              <td>{evt.list ? listLabels[evt.list] : '—'}</td>
              <td>{new Date(evt.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
