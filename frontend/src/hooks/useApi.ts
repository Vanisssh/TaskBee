import { useQuery, UseQueryResult } from '@tanstack/react-query'
import { apiClient } from '../services/api'

export function useApi<T>(
  key: string | string[],
  url: string,
  options = {}
): UseQueryResult<T, Error> {
  return useQuery({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn: async () => {
      return apiClient.get<T>(url)
    },
    ...options,
  })
}
