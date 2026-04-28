import { useApi } from '../hooks/useApi'
import useDiscoveryHeartbeat from '../hooks/useDiscoveryHeartbeat'

interface ServiceEntry {
  id: string
  name?: string
  address: string
  tags?: string[]
}

export default function ServiceSelector({ tag }: { tag?: string }) {
  const query = tag ? `/discovery/services?tag=${encodeURIComponent(tag)}` : '/discovery/services'
  const { data: services, isLoading } = useApi<ServiceEntry[]>('discovery-services', query)

  // Start heartbeat to keep frontend registration alive in Redis
  useDiscoveryHeartbeat({ id: `frontend-${Math.random().toString(36).slice(2, 8)}`, address: 'frontend:80', tags: ['frontend'] })

  if (isLoading) return <div>Загрузка сервисов...</div>

  return (
    <div>
      <h3>Доступные сервисы</h3>
      {(!services || services.length === 0) && <p>Сервисы не найдены</p>}
      <select style={{ width: '100%', padding: 8 }}>
        {services?.map(s => (
          <option key={s.id} value={s.address}>
            {s.id} {s.tags ? `(${s.tags.join(',')})` : ''}
          </option>
        ))}
      </select>
    </div>
  )
}
