import { Tab, UserRole } from '../types';

interface Props {
  tabs: { id: Tab; label: string }[];
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  token: string;
  role: UserRole;
  onSaveToken: (token: string, role: UserRole) => void;
  showMasked: boolean;
  onToggleMask: () => void;
}

export function TopBar({
  tabs,
  activeTab,
  onTabChange,
  token,
  role,
  onSaveToken,
  showMasked,
  onToggleMask
}: Props) {
  return (
    <header className="topbar">
      <div className="brand">Number Recognition</div>
      <nav className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={tab.id === activeTab ? 'tab active' : 'tab'}
          >
            {tab.label}
          </button>
        ))}
      </nav>
      <div className="auth-panel">
        <input
          className="token-input"
          type="text"
          placeholder="JWT токен"
          value={token}
          onChange={(e) => onSaveToken(e.target.value, role)}
        />
        <select value={role} onChange={(e) => onSaveToken(token, e.target.value as UserRole)}>
          <option value="admin">admin</option>
          <option value="operator">operator</option>
          <option value="viewer">viewer</option>
        </select>
        <label className="mask-toggle">
          <input type="checkbox" checked={showMasked} onChange={onToggleMask} />
          Маскирование
        </label>
      </div>
    </header>
  );
}
