import './GeneratorStatusPanel.css'
import { useApi } from '../hooks/useApi'
import type { GeneratorStatusResponse } from '../types'

export default function GeneratorStatusPanel() {
  const { data, isLoading, error, isFetching } = useApi<GeneratorStatusResponse>('generator-status', '/generator/status', {
    refetchInterval: 4000,
  })

  if (isLoading && !data) {
    return <div className="generator-panel generator-panel--muted">Загрузка статуса генератора…</div>
  }

  if (error) {
    return (
      <div className="generator-panel generator-panel--error">
        Не удалось получить статус: {error.message}
      </div>
    )
  }

  const g = data?.generator
  const live = data?.reachable && g

  return (
    <div className="generator-panel">
      <div className="generator-panel__toolbar">
        <span className={`generator-panel__dot ${live ? 'generator-panel__dot--ok' : 'generator-panel__dot--off'}`} />
        <strong>{live ? 'Генератор доступен' : 'Генератор недоступен'}</strong>
        {isFetching && <span className="generator-panel__fetching">обновление…</span>}
      </div>

      {!data?.reachable && (
        <p className="generator-panel__hint">
          Backend не достучался до <code>http://generator:8000/stats</code>
          {data?.detail ? `: ${data.detail}` : ''}. Запустите сервис <code>generator</code> в Docker Compose.
        </p>
      )}

      {live && (
        <>
          <p className="generator-panel__hint">
            Микросервис создаёт заказы в PostgreSQL и вызывает подбор исполнителей каждые{' '}
            <strong>{g.interval_seconds}</strong> с. Метрики снимаются с HTTP-интерфейса генератора.
          </p>
          <div className="generator-panel__grid">
            <div className="generator-metric">
              <span className="generator-metric__value">{g.orders_created}</span>
              <span className="generator-metric__label">Заказов создано</span>
            </div>
            <div className="generator-metric">
              <span className="generator-metric__value">{g.match_calls}</span>
              <span className="generator-metric__label">Вызовов matching</span>
            </div>
            <div className="generator-metric">
              <span className="generator-metric__value">{g.assignments}</span>
              <span className="generator-metric__label">Назначений</span>
            </div>
            <div className="generator-metric">
              <span className="generator-metric__value">{g.iterations_ok}</span>
              <span className="generator-metric__label">Успешных циклов</span>
            </div>
            <div className="generator-metric">
              <span className="generator-metric__value">{g.iterations_failed}</span>
              <span className="generator-metric__label">Ошибок цикла</span>
            </div>
          </div>
          <dl className="generator-panel__dl">
            <dt>ID сервиса</dt>
            <dd>
              <code>{g.service_id}</code>
            </dd>
            <dt>Последний заказ</dt>
            <dd>{g.last_order_id != null ? `#${g.last_order_id}` : '—'}</dd>
            <dt>Последний исполнитель</dt>
            <dd>{g.last_specialist_id != null ? `#${g.last_specialist_id}` : '—'}</dd>
            <dt>Источник подбора</dt>
            <dd>{g.last_match_source ?? '—'}</dd>
            <dt>Старт HTTP</dt>
            <dd>{g.started_at_iso ?? '—'}</dd>
          </dl>
          {g.last_error && (
            <div className="generator-panel__last-error">
              <strong>Последняя ошибка:</strong> {g.last_error}
            </div>
          )}
        </>
      )}
    </div>
  )
}
