import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/api/client'
import type { MP3, MP3Filters } from '@/types'



export const useMp3Store = defineStore('mp3', () => {
  const songs = ref<MP3[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedIds = ref<number[]>([])
  const savedPlaylistId = ref<number | null>(null)
  const savedPlaylistName = ref<string>('Ma sélection')

  const selectedSongs = computed(() =>
    songs.value.filter((s) => selectedIds.value.includes(s.id)),
  )

  function isSelected(id: number) {
    return selectedIds.value.includes(id)
  }

  function include(id: number) {
    if (!selectedIds.value.includes(id)) selectedIds.value.push(id)
  }

  async function exclude(id: number) {
    selectedIds.value = selectedIds.value.filter((x) => x !== id)
    console.log('[mp3Store] exclude id=', id, 'savedPlaylistId=', savedPlaylistId.value, 'remaining=', selectedIds.value)
    if (savedPlaylistId.value !== null) {
      const result = await api.playlist.update(savedPlaylistId.value, savedPlaylistName.value, selectedIds.value)
      console.log('[mp3Store] PUT playlist résultat:', result)
    }
  }

  function setSavedPlaylist(id: number, name: string) {
    savedPlaylistId.value = id
    savedPlaylistName.value = name
    console.log('[mp3Store] setSavedPlaylist id=', id, 'name=', name)
  }

  function clearSelection() {
    selectedIds.value.splice(0)
    savedPlaylistId.value = null
  }

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
    exclude(id)
  }

  return { songs, loading, error, selectedIds, savedPlaylistId, selectedSongs, isSelected, include, exclude, setSavedPlaylist, clearSelection, fetchAll, remove }
})
