import { apiClient, setAuthToken } from './api'
import type { User } from '../types'

type Role = 'customer' | 'executor'

interface AuthResponse {
  token: string
  user: User
}

export async function register(data: {
  name: string
  email: string
  password: string
  role: Role
}): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/register', data)
  setAuthToken(response.token)
  return response
}

export async function login(data: { email: string; password: string }): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/login', data)
  setAuthToken(response.token)
  return response
}

export async function me(): Promise<User> {
  return apiClient.get<User>('/auth/me')
}

export function logout() {
  setAuthToken(null)
}
