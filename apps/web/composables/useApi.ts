import type { NitroFetchOptions } from 'nitropack'

export function useApi() {
  const config = useRuntimeConfig()
  const supabase = useSupabaseClient()
  const toast = useToast()

  const baseUrl = config.public.apiBaseUrl || 'http://localhost:8000'

  async function request<T>(endpoint: string, options: NitroFetchOptions<any> = {}): Promise<T> {
    const url = `${baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

    // Attach user auth token if present
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    }

    try {
      const { data } = await supabase.auth.getSession()
      if (data?.session?.access_token) {
        headers.Authorization = `Bearer ${data.session.access_token}`
      }
    } catch {
      // In guest mode, session is null
    }

    try {
      const response = await $fetch<T>(url, {
        ...options,
        headers,
      })
      return response
    } catch (err: any) {
      const detail = err?.data?.detail || err?.data?.message || err?.message || 'An error occurred'
      const readableError = typeof detail === 'string' ? detail : JSON.stringify(detail)
      toast.error(readableError)
      throw new Error(readableError)
    }
  }

  return {
    get: <T>(endpoint: string, params?: Record<string, any>) =>
      request<T>(endpoint, { method: 'GET', query: params }),
    post: <T>(endpoint: string, body?: any, query?: Record<string, any>) =>
      request<T>(endpoint, { method: 'POST', body, query }),
    delete: <T>(endpoint: string) =>
      request<T>(endpoint, { method: 'DELETE' }),
  }
}

