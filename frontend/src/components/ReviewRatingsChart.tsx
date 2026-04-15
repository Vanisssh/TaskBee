import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface ReviewRatingsChartProps {
  totalReviews?: number | null
}

function ReviewRatingsChart({ totalReviews = 0 }: ReviewRatingsChartProps) {
  // Simulated rating distribution - in production would come from API
  const safeTotal = totalReviews ?? 0
  const averagePerRating = Math.floor(safeTotal / 5) || 0
  const chartData = [
    { rating: '⭐', value: Math.floor(averagePerRating * 0.8) },
    { rating: '⭐⭐', value: Math.floor(averagePerRating * 0.9) },
    { rating: '⭐⭐⭐', value: Math.floor(averagePerRating * 1.1) },
    { rating: '⭐⭐⭐⭐', value: Math.floor(averagePerRating * 1.2) },
    { rating: '⭐⭐⭐⭐⭐', value: Math.floor(averagePerRating * 1.3) },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="rating" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="value" fill="#43e97b" name="Отзывы" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default ReviewRatingsChart
