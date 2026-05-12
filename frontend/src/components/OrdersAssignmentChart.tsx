import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { useOrders } from '../hooks/useStats'
import './OrdersAssignmentChart.css'

const COLORS = ['#43e97b', '#cbd5e0']

interface OrderRow {
  specialist_id?: number | null
  specialist?: { id: number } | null
}

export default function OrdersAssignmentChart() {
  const { data: orders, isLoading, error } = useOrders()

  if (isLoading) {
    return <div className="orders-assignment--state">Загрузка заказов…</div>
  }

  if (error) {
    return <div className="orders-assignment--state orders-assignment--error">{error.message}</div>
  }

  const list = (orders || []) as OrderRow[]
  let withSpec = 0
  let without = 0
  for (const o of list) {
    const sid = o.specialist?.id ?? o.specialist_id
    if (sid != null && sid !== undefined) withSpec += 1
    else without += 1
  }

  const chartData = [
    { name: 'С исполнителем', value: withSpec },
    { name: 'Без исполнителя', value: without },
  ]

  if (list.length === 0) {
    return <div className="orders-assignment--state">Нет заказов для анализа назначений.</div>
  }

  return (
    <div className="orders-assignment">
      <p className="orders-assignment__caption">
        Отражает работу генератора и микросервиса подбора: заказы со статусом назначения и привязкой к{' '}
        <code>specialist_id</code>.
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={95} label>
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => [v, 'Заказов']} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
