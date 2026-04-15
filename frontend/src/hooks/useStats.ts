import { useApi } from './useApi'
import { StatsData } from '../types'

export function useStats() {
  return useApi<StatsData>('stats', '/stats/summary')
}

export function useOrders() {
  return useApi<any[]>('orders', '/orders')
}

export function useCategories() {
  return useApi<any[]>('categories', '/categories')
}

export function useServices() {
  return useApi<any[]>('services', '/services')
}
