import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { GenerateRequest, Playlist } from '@/types'

export const usePlaylistStore = defineStore('playlist', () => {
  const playlists = ref<Playlist[]>([])
  const candidates = ref<Playlist[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      playlists.value = await api.playlist.list()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Erreur inconnue'
    } finally {
      loading.value = false
    }
  }

  async function generate(req: GenerateRequest) {
    loading.value = true
    error.value = null
    candidates.value = []
    try {
      candidates.value = await api.playlist.generate(req)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Erreur inconnue'
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    await api.playlist.delete(id)
    playlists.value = playlists.value.filter((p) => p.id !== id)
  }

  return { playlists, candidates, loading, error, fetchAll, generate, remove }
})


