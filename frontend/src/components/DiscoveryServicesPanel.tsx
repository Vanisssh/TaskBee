import './DiscoveryServicesPanel.css'
import { useApi } from '../hooks/useApi'
import type { DiscoveryServiceEntry } from '../types'

function tagClass(tag: string) {
  if (tag.includes('matching') || tag.includes('generator')) return 'tag tag-accent'
  if (tag === 'frontend') return 'tag tag-frontend'
  return 'tag'
}

export default function DiscoveryServicesPanel() {
  const { data: services, isLoading, error } = useApi<DiscoveryServiceEntry[]>('discovery-panel', '/discovery/services')

  if (isLoading) {
    return <div className="discovery-panel discovery-panel--loading">Загрузка сервисов discovery…</div>
  }

  if (error) {
    return (
      <div className="discovery-panel discovery-panel--error">
        Не удалось загрузить <code>/discovery/services</code>: {error.message}
      </div>
    )
  }

  if (!services?.length) {
    return (
      <div className="discovery-panel discovery-panel--empty">
        Зарегистрированных сервисов пока нет. Запустите <code>generator</code> и <code>matcher-service</code> через Docker Compose.
      </div>
    )
  }

  return (
    <div className="discovery-panel">
      <p className="discovery-panel__hint">
        Регистрация из ЛР5: микросервисы публикуют <code>id</code>, <code>address</code> и <code>tags</code>.
      </p>
      <ul className="discovery-panel__list">
        {services.map(s => (
          <li key={s.id} className="discovery-card">
            <div className="discovery-card__header">
              <span className="discovery-card__id">{s.id}</span>
              {s.name && <span className="discovery-card__name">{s.name}</span>}
            </div>
            <div className="discovery-card__address">{s.address}</div>
            <div className="discovery-card__tags">
              {(s.tags || []).map(t => (
                <span key={t} className={tagClass(t)}>
                  {t}
                </span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
