import { useEffect, useState } from 'react'
import './RecentOrdersTable.css'
import { useApi } from '../hooks/useApi'

interface Order {
  id: number
  client_id: number
  service_id: number
  specialist_id: number | null
  status: string
  address: string
  description: string
  created_at: string
}

function RecentOrdersTable() {
  const { data: orders, isLoading } = useApi<Order[]>('orders', '/orders')
  const [displayOrders, setDisplayOrders] = useState<Order[]>([])

  useEffect(() => {
    if (orders) {
      // Show only last 10 orders sorted by creation date
      const recent = orders.slice(0, 10)
      setDisplayOrders(recent)
    }
  }, [orders])

  const getStatusBadge = (status: string) => {
    const colors: { [key: string]: string } = {
      new: '#667eea',
      assigned: '#4facfe',
      in_progress: '#43e97b',
      completed: '#f093fb',
      cancelled: '#fa709a',
    }
    return colors[status] || '#999'
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ru-RU')
  }

  if (isLoading) {
    return <div>Загрузка...</div>
  }

  if (displayOrders.length === 0) {
    return <div className="no-data">Нет заказов</div>
  }

  return (
    <div className="table-wrapper">
      <table className="orders-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Адрес</th>
            <th>Описание</th>
            <th>Статус</th>
            <th>Дата создания</th>
          </tr>
        </thead>
        <tbody>
          {displayOrders.map(order => (
            <tr key={order.id}>
              <td>#{order.id}</td>
              <td>{order.address}</td>
              <td className="description-cell">{order.description.substring(0, 50)}...</td>
              <td>
                <span className="status-badge" style={{ backgroundColor: getStatusBadge(order.status) }}>
                  {order.status}
                </span>
              </td>
              <td>{formatDate(order.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RecentOrdersTable
