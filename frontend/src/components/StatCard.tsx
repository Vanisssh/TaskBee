import './StatCard.css'

interface StatCardProps {
  label: string
  value: number | string
  icon: string
  color?: string
}

function StatCard({ label, value, icon, color = '#667eea' }: StatCardProps) {
  return (
    <div className="stat-card" style={{ borderTopColor: color }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
      </div>
    </div>
  )
}

export default StatCard
