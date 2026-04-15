import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

interface SpecialistsRatingChartProps {
  avgRating?: number | null
}

function SpecialistsRatingChart({ avgRating = 0 }: SpecialistsRatingChartProps) {
  const safeRating = avgRating ?? 0
  const ratingPercentage = (safeRating / 5) * 100
  const data = [
    { name: 'Рейтинг', value: ratingPercentage },
    { name: 'Остаток', value: 100 - ratingPercentage },
  ]

  const COLORS = ['#764ba2', '#e0e0e0']

  return (
    <div style={{ textAlign: 'center' }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <p style={{ marginTop: 10, fontSize: '1.2em', fontWeight: 'bold' }}>
        {(safeRating ?? 0).toFixed(2)} / 5.00 ⭐
      </p>
    </div>
  )
}

export default SpecialistsRatingChart
