import './Dashboard.css'
import StatCard from './StatCard'
import OrderStatusChart from './OrderStatusChart'
import ReviewRatingsChart from './ReviewRatingsChart'
import SpecialistsRatingChart from './SpecialistsRatingChart'
import RecentOrdersTable from './RecentOrdersTable'
import CategoriesOverview from './CategoriesOverview'
import LoadingSpinner from './LoadingSpinner'
import { useStats } from '../hooks/useStats'

function Dashboard() {
  const { data: stats, isLoading, error } = useStats()

  if (isLoading) {
    return <LoadingSpinner message="Загрузка данных панели управления..." />
  }

  if (error || !stats) {
    return (
      <div className="dashboard-error">
        <h2>Ошибка загрузки данных</h2>
        <p>{error?.message || 'Backend не доступен. Убедитесь, что сервис запущен на http://localhost:5000'}</p>
        <p style={{ fontSize: '0.9em', color: '#666', marginTop: '10px' }}>
          Проверьте: docker-compose up или npm run dev (backend должен быть на :5000)
        </p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Панель управления TaskBee</h1>
        <p>Система управления профессиональными услугами</p>
      </div>

      {/* Main Stats Grid */}
      <div className="stats-grid">
        <StatCard
          label="Пользователи"
          value={stats?.total_users || 0}
          icon="👥"
          color="#667eea"
        />
        <StatCard
          label="Специалисты"
          value={stats?.total_specialists || 0}
          icon="⭐"
          color="#764ba2"
        />
        <StatCard
          label="Услуги"
          value={stats?.total_services || 0}
          icon="🛠️"
          color="#f093fb"
        />
        <StatCard
          label="Категории"
          value={stats?.total_categories || 0}
          icon="📂"
          color="#4facfe"
        />
        <StatCard
          label="Отзывы"
          value={stats?.total_reviews || 0}
          icon="⭐"
          color="#43e97b"
        />
        <StatCard
          label="Средняя оценка"
          value={(stats?.avg_review_rating || 0).toFixed(2)}
          icon="📈"
          color="#fa709a"
        />
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h2>Заказы по статусу</h2>
          {stats?.orders_by_status ? (
            <OrderStatusChart data={stats.orders_by_status} />
          ) : (
            <p>Нет данных о заказах</p>
          )}
        </div>
        <div className="chart-container">
          <h2>Рейтинг специалистов</h2>
          {stats ? (
            <SpecialistsRatingChart avgRating={stats.avg_specialist_rating} />
          ) : (
            <p>Нет данных</p>
          )}
        </div>
      </div>

      {/* Additional Charts */}
      <div className="charts-grid">
        <div className="chart-container">
          <h2>Распределение оценок отзывов</h2>
          {stats?.total_reviews ? (
            <ReviewRatingsChart totalReviews={stats.total_reviews} />
          ) : (
            <p>Нет данных об отзывах</p>
          )}
        </div>
        <div className="chart-container">
          <h2>Услуги по категориям</h2>
          <CategoriesOverview />
        </div>
      </div>

      {/* Recent Orders Table */}
      <div className="table-container">
        <h2>Недавние заказы</h2>
        <RecentOrdersTable />
      </div>
    </div>
  )
}

export default Dashboard
