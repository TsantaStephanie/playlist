import type { GenerateRequest, MP3, MP3Filters, Playlist } from '@/types'

const BASE = 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Erreur serveur')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  mp3: {
    list: (filters?: MP3Filters): Promise<MP3[]> => {
      const params = new URLSearchParams()
      if (filters?.title) params.set('title', filters.title)
      if (filters?.artist) params.set('artist', filters.artist)
      if (filters?.genre) params.set('genre', filters.genre)
      if (filters?.year) params.set('year', String(filters.year))
      if (filters?.language) params.set('language', filters.language)
      const qs = params.toString()
      return request(`/api/mp3${qs ? '?' + qs : ''}`)
    },
    get: (id: number): Promise<MP3> => request(`/api/mp3/${id}`),
    delete: (id: number): Promise<void> => request(`/api/mp3/${id}`, { method: 'DELETE' }),
    streamUrl: (id: number): string => `${BASE}/api/mp3/${id}/stream`,
  },

  playlist: {
    list: (): Promise<Playlist[]> => request('/api/playlist'),
    get: (id: number): Promise<Playlist> => request(`/api/playlist/${id}`),
    generate: (body: GenerateRequest): Promise<Playlist[]> =>
      request('/api/playlist/generate', { method: 'POST', body: JSON.stringify(body) }),
    save: (name: string, criteria: object, mp3_ids: number[]): Promise<Playlist> =>
      request('/api/playlist', { method: 'POST', body: JSON.stringify({ name, criteria, mp3_ids }) }),
    delete: (id: number): Promise<void> => request(`/api/playlist/${id}`, { method: 'DELETE' }),
  },
}
