import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { MP3, MP3Filters } from '@/types'

export const useMp3Store = defineStore('mp3', () => {
  const songs = ref<MP3[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll(filters?: MP3Filters) {
    loading.value = true
    error.value = null
    try {
      songs.value = await api.mp3.list(filters)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Erreur inconnue'
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    await api.mp3.delete(id)
    songs.value = songs.value.filter((s) => s.id !== id)
  }

  return { songs, loading, error, fetchAll, remove }
})
