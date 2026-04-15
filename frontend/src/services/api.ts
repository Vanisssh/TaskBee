import axios, { AxiosInstance } from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  async get<T>(url: string, config = {}): Promise<T> {
    const response = await this.client.get<T>(url, config)
    const payload: any = response.data
    // Backend wraps responses as { data: ... } — unwrap if present
    return payload && typeof payload === 'object' && 'data' in payload ? (payload.data as T) : (payload as T)
  }

  async post<T>(url: string, data?: unknown, config = {}): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    const payload: any = response.data
    return payload && typeof payload === 'object' && 'data' in payload ? (payload.data as T) : (payload as T)
  }

  async put<T>(url: string, data?: unknown, config = {}): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    const payload: any = response.data
    return payload && typeof payload === 'object' && 'data' in payload ? (payload.data as T) : (payload as T)
  }

  async delete<T>(url: string, config = {}): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    const payload: any = response.data
    return payload && typeof payload === 'object' && 'data' in payload ? (payload.data as T) : (payload as T)
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
