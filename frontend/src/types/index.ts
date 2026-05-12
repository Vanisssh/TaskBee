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
  user?: { id: number; name: string; email: string }
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
  specialist_id?: number | null
  status: 'new' | 'assigned' | 'in_progress' | 'completed' | 'cancelled'
  address?: string | null
  description?: string | null
  created_at: string
  specialist?: { id: number; user_id?: number; rating_avg?: number } | null
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

/** Ответ микросервиса подбора (через POST /matching/recommendations). */
export interface MatchingRankEntry {
  specialist_id: number
  score: number
  details?: Record<string, number>
}

export interface MatchingRecommendationResult {
  best_match: MatchingRankEntry | null
  ranking: MatchingRankEntry[]
  meta?: {
    source?: string
    model?: string
    candidate_count?: number
    request_id?: string
    reason?: string
  }
  error?: string
  message?: string
}

export interface DiscoveryServiceEntry {
  id: string
  name?: string
  address: string
  tags?: string[]
}

/** Счётчики с GET http://generator:8000/stats (через backend GET /generator/status). */
export interface GeneratorRuntimeStats {
  service_id: string
  interval_seconds: number
  orders_created: number
  match_calls: number
  assignments: number
  iterations_ok: number
  iterations_failed: number
  last_order_id: number | null
  last_specialist_id: number | null
  last_match_source: string | null
  last_error: string | null
  started_at_iso: string | null
}

export interface GeneratorStatusResponse {
  reachable: boolean
  generator?: GeneratorRuntimeStats
  http_status?: number
  detail?: string
}
