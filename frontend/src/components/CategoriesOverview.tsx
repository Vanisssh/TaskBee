import { useEffect, useState } from 'react'
import { useApi } from '../hooks/useApi'

interface Category {
  id: number
  name: string
  slug: string
}

interface Service {
  id: number
  category_id: number
  name: string
}

function CategoriesOverview() {
  const { data: categories } = useApi<Category[]>('categories', '/categories')
  const { data: services } = useApi<Service[]>('services', '/services')
  const [categoryData, setCategoryData] = useState<Array<{ name: string; count: number }>>([])

  useEffect(() => {
    if (categories && services) {
      const counts: { [key: number]: number } = {}
      categories.forEach(cat => {
        counts[cat.id] = 0
      })

      services.forEach(service => {
        if (counts[service.category_id] !== undefined) {
          counts[service.category_id]++
        }
      })

      const data = categories.map(cat => ({
        name: cat.name,
        count: counts[cat.id] || 0,
      }))

      setCategoryData(data)
    }
  }, [categories, services])

  return (
    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
      {categoryData.length === 0 ? (
        <p>Нет данных о категориях</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #f0f0f0' }}>
              <th style={{ textAlign: 'left', padding: '10px' }}>Категория</th>
              <th style={{ textAlign: 'right', padding: '10px' }}>Услуг</th>
            </tr>
          </thead>
          <tbody>
            {categoryData.map((cat, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #f0f0f0' }}>
                <td style={{ padding: '10px' }}>{cat.name}</td>
                <td style={{ textAlign: 'right', padding: '10px', fontWeight: 'bold', color: '#667eea' }}>
                  {cat.count}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default CategoriesOverview
