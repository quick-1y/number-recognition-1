import { useState } from 'react';

interface ListItem {
  id: string;
  name: string;
  type: 'white' | 'black' | 'info';
  priority: number;
  ttlSeconds?: number;
}

const initial: ListItem[] = [
  { id: 'vip', name: 'VIP', type: 'white', priority: 10, ttlSeconds: 86400 },
  { id: 'blocked', name: 'Blocked', type: 'black', priority: 100 },
  { id: 'notify', name: 'Notify', type: 'info', priority: 1 }
];

export function ListsPanel() {
  const [items, setItems] = useState<ListItem[]>(initial);

  return (
    <div className="card">
      <div className="list-header">
        <div>
          <div className="muted">Активные списки</div>
          <div className="small">Импорт/экспорт CSV/JSON доступен из API</div>
        </div>
        <button
          className="btn ghost"
          onClick={() =>
            setItems((prev) => [
              ...prev,
              {
                id: `list-${prev.length + 1}`,
                name: `Новый список ${prev.length + 1}`,
                type: 'info',
                priority: 0
              }
            ])
          }
        >
          + Добавить
        </button>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Тип</th>
            <th>Приоритет</th>
            <th>TTL</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>{item.type}</td>
              <td>{item.priority}</td>
              <td>{item.ttlSeconds ? `${Math.round(item.ttlSeconds / 3600)} ч` : '∞'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
