import { useEffect, useState } from 'react'
import { useCategories, useServices } from '../hooks/useStats'
import { apiClient } from '../services/api'

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

function slugify(s: string) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9а-яё\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
}

function CategoriesOverview() {
  const categoriesQuery = useCategories()
  const servicesQuery = useServices()
  const categories = categoriesQuery.data || []
  const services = servicesQuery.data || []

  const [categoryData, setCategoryData] = useState<Array<{ name: string; count: number; id: number }>>([])

  // form state
  const [newCategoryName, setNewCategoryName] = useState('')
  const [newCategorySlug, setNewCategorySlug] = useState('')
  const [newServiceName, setNewServiceName] = useState('')
  const [newServiceCategoryId, setNewServiceCategoryId] = useState<number | ''>('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const counts: { [key: number]: number } = {}
    categories.forEach((cat: Category) => {
      counts[cat.id] = 0
    })

    services.forEach((service: Service) => {
      if (counts[service.category_id] !== undefined) counts[service.category_id]++
    })

    const data = categories.map((cat: Category) => ({
      id: cat.id,
      name: cat.name,
      count: counts[cat.id] || 0,
    }))

    setCategoryData(data)
  }, [categories, services])

  async function handleCreateCategory(e: React.FormEvent) {
    e.preventDefault()
    if (!newCategoryName.trim()) return alert('Введите имя категории')
    setSaving(true)
    try {
      await apiClient.post('/categories', { name: newCategoryName.trim(), slug: newCategorySlug.trim() || slugify(newCategoryName) })
      setNewCategoryName('')
      setNewCategorySlug('')
      await categoriesQuery.refetch()
    } catch (err: any) {
      alert(err?.message || 'Ошибка при создании категории')
    } finally {
      setSaving(false)
    }
  }

  async function handleCreateService(e: React.FormEvent) {
    e.preventDefault()
    if (!newServiceName.trim()) return alert('Введите имя услуги')
    if (!newServiceCategoryId) return alert('Выберите категорию для услуги')
    setSaving(true)
    try {
      await apiClient.post('/services', { name: newServiceName.trim(), category_id: Number(newServiceCategoryId) })
      setNewServiceName('')
      setNewServiceCategoryId('')
      await servicesQuery.refetch()
      await categoriesQuery.refetch()
    } catch (err: any) {
      alert(err?.message || 'Ошибка при создании услуги')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
      <div style={{ display: 'flex', gap: '20px', marginBottom: '16px' }}>
        <form onSubmit={handleCreateCategory} style={{ flex: 1, padding: '12px', border: '1px solid #eee', borderRadius: 6 }}>
          <h3>Создать категорию</h3>
          <div style={{ marginBottom: 8 }}>
            <input placeholder="Название категории" value={newCategoryName} onChange={e => setNewCategoryName(e.target.value)} style={{ width: '100%', padding: 8 }} />
          </div>
          <div style={{ marginBottom: 8 }}>
            <input placeholder="Slug (необязательно)" value={newCategorySlug} onChange={e => setNewCategorySlug(e.target.value)} style={{ width: '100%', padding: 8 }} />
          </div>
          <button type="submit" disabled={saving} style={{ padding: '8px 12px' }}>Создать</button>
        </form>

        <form onSubmit={handleCreateService} style={{ flex: 1, padding: '12px', border: '1px solid #eee', borderRadius: 6 }}>
          <h3>Создать услугу</h3>
          <div style={{ marginBottom: 8 }}>
            <input placeholder="Название услуги" value={newServiceName} onChange={e => setNewServiceName(e.target.value)} style={{ width: '100%', padding: 8 }} />
          </div>
          <div style={{ marginBottom: 8 }}>
            <select value={newServiceCategoryId as any} onChange={e => setNewServiceCategoryId(e.target.value ? Number(e.target.value) : '')} style={{ width: '100%', padding: 8 }}>
              <option value="">-- Выберите категорию --</option>
              {categories.map((c: Category) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <button type="submit" disabled={saving} style={{ padding: '8px 12px' }}>Создать</button>
        </form>
      </div>

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
            {categoryData.map((cat) => (
              <tr key={cat.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
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
