import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { apiClient } from '../services/api'
import type { MatchingRecommendationResult, Specialist } from '../types'
import './MatchingRankingChart.css'

const BAR_COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#f6ad55', '#38b2ac']

function buildDemoPayload(specialists: Specialist[]) {
  const budget = 4500
  const candidates = specialists.slice(0, 10).map((s, i) => ({
    specialist_id: s.id,
    rating: typeof s.rating_avg === 'number' ? s.rating_avg : 4,
    response_time_min: 8 + (i % 5) * 6,
    active_orders: (i * 2) % 7,
    category_match: i % 3 !== 0,
    price: Math.round(budget * (0.75 + (i % 4) * 0.08)),
    location: {
      lat: 55.75 + (i % 5) * 0.02,
      lon: 37.61 + (i % 4) * 0.015,
    },
  }))

  return {
    order: {
      order_id: 0,
      budget,
      category: 'taskbee-services',
      client_location: { lat: 55.752, lon: 37.618 },
    },
    candidates,
  }
}

export default function MatchingRankingChart() {
  const matcherKey = import.meta.env.VITE_MATCHER_API_KEY as string | undefined

  const query = useQuery({
    queryKey: ['matching-ranking-demo', matcherKey ?? ''],
    queryFn: async () => {
      const specialists = await apiClient.get<Specialist[]>('/specialists')
      if (!specialists?.length) {
        return { result: null as MatchingRecommendationResult | null, empty: true as const }
      }
      const body = buildDemoPayload(specialists)
      const headers: Record<string, string> = {}
      if (matcherKey) headers['X-API-Key'] = matcherKey
      const result = await apiClient.post<MatchingRecommendationResult>('/matching/recommendations', body, { headers })
      return { result, empty: false as const }
    },
    refetchInterval: 25_000,
    staleTime: 10_000,
  })

  if (query.isLoading) {
    return <div className="matching-chart__state">Запрос демо-подбора исполнителей…</div>
  }

  if (query.isError) {
    return (
      <div className="matching-chart__state matching-chart__state--error">
        {query.error instanceof Error ? query.error.message : 'Ошибка запроса'}
        <p className="matching-chart__hint">
          Если backend требует ключ, задайте в <code>.env</code> переменную <code>VITE_MATCHER_API_KEY</code> (как{' '}
          <code>MATCHER_API_KEY</code> в Docker).
        </p>
      </div>
    )
  }

  const payload = query.data
  if (payload?.empty) {
    return <div className="matching-chart__state">Нет специалистов в базе — демо-подбор недоступен.</div>
  }

  const result = payload?.result
  const ranking = (result?.ranking || []).slice(0, 8).map(r => ({
    name: `#${r.specialist_id}`,
    score: r.score,
    specialist_id: r.specialist_id,
  }))

  if (!ranking.length) {
    return <div className="matching-chart__state">Пустой ответ подбора.</div>
  }

  const source = result?.meta?.source
  const model = result?.meta?.model

  return (
    <div className="matching-chart">
      <div className="matching-chart__meta">
        {source && (
          <span className="matching-chart__badge">
            Источник: <strong>{source}</strong>
          </span>
        )}
        {model && (
          <span className="matching-chart__badge matching-chart__badge--muted">
            Модель: <code>{model}</code>
          </span>
        )}
        {result?.best_match && (
          <span className="matching-chart__badge matching-chart__badge--best">
            Лучший: #{result.best_match.specialist_id} — {result.best_match.score}
          </span>
        )}
      </div>
      <p className="matching-chart__caption">
        Демо-запрос к <code>POST /matching/recommendations</code> на основе реальных специалистов (очередь RabbitMQ → matcher-service).
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={ranking} layout="vertical" margin={{ left: 16, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 'dataMax + 0.05']} tickFormatter={v => Number(v).toFixed(2)} />
          <YAxis type="category" dataKey="name" width={72} />
          <Tooltip formatter={(v: number) => [v.toFixed(4), 'Релевантность']} />
          <Bar dataKey="score" name="Релевантность" radius={[0, 6, 6, 0]}>
            {ranking.map((_, i) => (
              <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
