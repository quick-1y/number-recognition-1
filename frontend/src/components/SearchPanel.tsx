import { useState } from 'react';

export interface SearchFilters {
  plateMask: string;
  channel: string;
  list: 'white' | 'black' | 'info' | 'any';
  from: string;
  to: string;
}

interface Props {
  onSubmit: (filters: SearchFilters) => void;
}

export function SearchPanel({ onSubmit }: Props) {
  const [filters, setFilters] = useState<SearchFilters>({
    plateMask: '',
    channel: '',
    list: 'any',
    from: '',
    to: ''
  });

  return (
    <div className="card form-grid">
      <label>
        Маска номера
        <input
          type="text"
          placeholder="A123*77"
          value={filters.plateMask}
          onChange={(e) => setFilters({ ...filters, plateMask: e.target.value })}
        />
      </label>
      <label>
        Канал
        <input
          type="text"
          placeholder="cam-north"
          value={filters.channel}
          onChange={(e) => setFilters({ ...filters, channel: e.target.value })}
        />
      </label>
      <label>
        Список
        <select
          value={filters.list}
          onChange={(e) => setFilters({ ...filters, list: e.target.value as SearchFilters['list'] })}
        >
          <option value="any">Любой</option>
          <option value="white">Белый</option>
          <option value="black">Чёрный</option>
          <option value="info">Информационный</option>
        </select>
      </label>
      <label>
        Время от
        <input
          type="datetime-local"
          value={filters.from}
          onChange={(e) => setFilters({ ...filters, from: e.target.value })}
        />
      </label>
      <label>
        Время до
        <input
          type="datetime-local"
          value={filters.to}
          onChange={(e) => setFilters({ ...filters, to: e.target.value })}
        />
      </label>
      <div className="form-actions">
        <button className="btn primary" onClick={() => onSubmit(filters)}>
          Искать
        </button>
      </div>
    </div>
  );
}
