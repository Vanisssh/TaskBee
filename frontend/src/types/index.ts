// Type definitions for TaskBee API responses

export interface User {
  id: number
  name: string
  email: string
  created_at: string
}

export interface Specialist {
  id: number
  user_id: number
  bio: string
  rating_avg: number
}

export interface Service {
  id: number
  category_id: number
  name: string
  description?: string
}

export interface ServiceCategory {
  id: number
  name: string
  slug: string
}

export interface Order {
  id: number
  client_id: number
  service_id: number
  specialist_id?: number
  status: 'new' | 'assigned' | 'in_progress' | 'completed' | 'cancelled'
  address: string
  description: string
  created_at: string
}

export interface Review {
  id: number
  order_id: number
  user_id: number
  rating: number
  comment?: string
  created_at: string
}

export interface StatsData {
  orders_by_status: {
    new: number
    assigned: number
    in_progress: number
    completed: number
    cancelled: number
  }
  total_users: number
  total_specialists: number
  total_categories: number
  total_services: number
  total_reviews: number
  avg_review_rating: number
  avg_specialist_rating: number
}
