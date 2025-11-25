export function SettingsPanel() {
  return (
    <div className="card settings-grid">
      <div>
        <h4>Общие</h4>
        <ul>
          <li>Хранение изображений: 90 дней (настраивается)</li>
          <li>Маскирование номеров для viewer: включено</li>
          <li>Шаблоны стран: RU, BY, KZ, UA, EU</li>
        </ul>
      </div>
      <div>
        <h4>API / Webhooks</h4>
        <ul>
          <li>Адрес API: переменная окружения <code>VITE_API_BASE_URL</code></li>
          <li>Webhooks с HMAC и backoff</li>
          <li>Метод аутентификации: Bearer JWT</li>
        </ul>
      </div>
      <div>
        <h4>Каналы и реле</h4>
        <ul>
          <li>Антидребезг реле: 200 мс (пример)</li>
          <li>Порог уверенности: 0.6 (пример)</li>
          <li>Антидубликаты: 30 с</li>
        </ul>
      </div>
    </div>
  );
}
