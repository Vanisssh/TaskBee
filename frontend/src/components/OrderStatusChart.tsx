import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface OrderStatusChartProps {
  data?: {
    new?: number
    assigned?: number
    in_progress?: number
    completed?: number
    cancelled?: number
  } | null
}

function OrderStatusChart({ data }: OrderStatusChartProps) {
  const safeData = {
    new: data?.new ?? 0,
    assigned: data?.assigned ?? 0,
    in_progress: data?.in_progress ?? 0,
    completed: data?.completed ?? 0,
    cancelled: data?.cancelled ?? 0,
  }

  const chartData = [
    { name: 'Новые', value: safeData.new },
    { name: 'Назначены', value: safeData.assigned },
    { name: 'В процессе', value: safeData.in_progress },
    { name: 'Завершены', value: safeData.completed },
    { name: 'Отменены', value: safeData.cancelled },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill="#667eea" name="Количество" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default OrderStatusChart
