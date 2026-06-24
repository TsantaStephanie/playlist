<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useMp3Store } from '@/stores/mp3'
import { api } from '@/api/client'
import type { MP3 } from '@/types'

const store = useMp3Store()
const filters = reactive({ title: '', artist: '', genre: '', language: '' })

const editingId = ref<number | null>(null)
const editForm = reactive({ title: '', artist: '', album: '', genre: '', year: '' as number | '', language: '' })
const saving = ref(false)

function formatTime(s: number) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function search() {
  const f = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ''))
  store.fetchAll(Object.keys(f).length ? f : undefined)
}

function startEdit(mp3: MP3) {
  editingId.value = mp3.id
  editForm.title = mp3.title ?? ''
  editForm.artist = mp3.artist ?? ''
  editForm.album = mp3.album ?? ''
  editForm.genre = mp3.genre ?? ''
  editForm.year = mp3.year ?? ''
  editForm.language = mp3.language ?? ''
  console.log('[MP3ListView] édition id=', mp3.id)
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(id: number) {
  saving.value = true
  try {
    const data: Partial<MP3> = {
      title: editForm.title || undefined,
      artist: editForm.artist || undefined,
      album: editForm.album || undefined,
      genre: editForm.genre || undefined,
      year: editForm.year !== '' ? Number(editForm.year) : undefined,
      language: editForm.language || undefined,
    }
    const updated = await api.mp3.update(id, data)
    console.log('[MP3ListView] mis à jour:', updated)
    const idx = store.songs.findIndex(s => s.id === id)
    if (idx !== -1) store.songs[idx] = updated
    editingId.value = null
  } finally {
    saving.value = false
  }
}

onMounted(() => store.fetchAll())
</script>

<template>
  <div class="page">
    <h1>Bibliothèque MP3</h1>

    <form class="filters" @submit.prevent="search">
      <input v-model="filters.title" placeholder="Titre…" />
      <input v-model="filters.artist" placeholder="Artiste…" />
      <input v-model="filters.genre" placeholder="Genre…" />
      <input v-model="filters.language" placeholder="Langue…" />
      <button type="submit">Rechercher</button>
      <button type="button" @click="filters.title = filters.artist = filters.genre = filters.language = ''; store.fetchAll()">
        Réinitialiser
      </button>
    </form>

    <p v-if="store.loading" class="info">Chargement…</p>
    <p v-else-if="store.error" class="error">{{ store.error }}</p>
    <p v-else-if="!store.songs.length" class="info">Aucun MP3 trouvé.</p>

    <div v-else class="table-wrap">
      <p class="count">{{ store.songs.length }} morceau(x)</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Titre</th>
            <th>Artiste</th>
            <th>Album</th>
            <th>Genre</th>
            <th>Année</th>
            <th>Durée</th>
            <th>Langue</th>
            <th class="th-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="mp3 in store.songs" :key="mp3.id">
            <!-- Ligne normale -->
            <tr v-if="editingId !== mp3.id">
              <td class="id">{{ mp3.id }}</td>
              <td>{{ mp3.title ?? '(sans titre)' }}</td>
              <td>{{ mp3.artist ?? '—' }}</td>
              <td>{{ mp3.album ?? '—' }}</td>
              <td>{{ mp3.genre ?? '—' }}</td>
              <td>{{ mp3.year ?? '—' }}</td>
              <td>{{ formatTime(mp3.duration) }}</td>
              <td>{{ mp3.language ?? '—' }}</td>
              <td class="actions">
                <button class="btn-edit" @click="startEdit(mp3)">Modifier</button>
                <button class="btn-del" @click="store.remove(mp3.id)" title="Supprimer">✕</button>
              </td>
            </tr>
            <!-- Ligne en mode édition -->
            <tr v-else class="editing-row">
              <td class="id">{{ mp3.id }}</td>
              <td><input v-model="editForm.title" placeholder="Titre" /></td>
              <td><input v-model="editForm.artist" placeholder="Artiste" /></td>
              <td><input v-model="editForm.album" placeholder="Album" /></td>
              <td><input v-model="editForm.genre" placeholder="Genre" /></td>
              <td><input v-model="editForm.year" type="number" placeholder="Année" style="width:70px" /></td>
              <td>{{ formatTime(mp3.duration) }}</td>
              <td><input v-model="editForm.language" placeholder="Langue" style="width:60px" /></td>
              <td class="actions">
                <button class="btn-save" @click="saveEdit(mp3.id)" :disabled="saving">
                  {{ saving ? '…' : 'Sauvegarder' }}
                </button>
                <button class="btn-cancel" @click="cancelEdit">Annuler</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem; }
h1 { margin-bottom: 1.25rem; font-size: 1.5rem; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem; }
.filters input { padding: 0.45rem 0.75rem; border: 1px solid #444; border-radius: 6px; background: #1e1e2e; color: #eee; font-size: 0.9rem; }
.filters button { padding: 0.45rem 1rem; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
.filters button[type="submit"] { background: #7c3aed; color: #fff; }
.filters button[type="button"] { background: #374151; color: #eee; }
.info { color: #aaa; }
.error { color: #f87171; }
.count { color: #aaa; font-size: 0.85rem; margin-bottom: 0.5rem; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
th { text-align: left; padding: 0.55rem 0.75rem; background: #1e1e2e; color: #9ca3af; font-weight: 600; border-bottom: 1px solid #333; }
.th-actions { text-align: center; }
td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #2a2a3e; color: #ddd; }
tr:hover td { background: #1e1e2e; }
.editing-row td { background: #1a1a3e; border-bottom-color: #4c1d95; }
.editing-row input { padding: 0.25rem 0.4rem; border: 1px solid #4c1d95; border-radius: 4px; background: #111827; color: #eee; font-size: 0.85rem; width: 100%; }
.id { color: #6b7280; }
.actions { display: flex; gap: 0.4rem; align-items: center; justify-content: center; white-space: nowrap; }
.btn-edit { background: #1d4ed8; color: #bfdbfe; border: none; padding: 0.25rem 0.6rem; border-radius: 5px; cursor: pointer; font-size: 0.8rem; }
.btn-edit:hover { background: #2563eb; }
.btn-del { background: none; border: none; color: #6b7280; cursor: pointer; font-size: 0.85rem; padding: 0.2rem 0.4rem; border-radius: 4px; }
.btn-del:hover { color: #ef4444; background: #450a0a; }
.btn-save { background: #059669; color: #fff; border: none; padding: 0.25rem 0.6rem; border-radius: 5px; cursor: pointer; font-size: 0.8rem; }
.btn-save:disabled { opacity: 0.5; cursor: default; }
.btn-cancel { background: #374151; color: #9ca3af; border: none; padding: 0.25rem 0.6rem; border-radius: 5px; cursor: pointer; font-size: 0.8rem; }
</style>
