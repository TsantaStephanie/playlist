<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useMp3Store } from '@/stores/mp3'

const store = useMp3Store()
const filters = reactive({ title: '', artist: '', genre: '', language: '' })

function formatTime(s: number) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function search() {
  const f = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ''))
  store.fetchAll(Object.keys(f).length ? f : undefined)
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
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mp3 in store.songs" :key="mp3.id">
            <td class="id">{{ mp3.id }}</td>
            <td>{{ mp3.title ?? '(sans titre)' }}</td>
            <td>{{ mp3.artist ?? '—' }}</td>
            <td>{{ mp3.album ?? '—' }}</td>
            <td>{{ mp3.genre ?? '—' }}</td>
            <td>{{ mp3.year ?? '—' }}</td>
            <td>{{ formatTime(mp3.duration) }}</td>
            <td>{{ mp3.language ?? '—' }}</td>
            <td>
              <button class="del" @click="store.remove(mp3.id)" title="Supprimer">✕</button>
            </td>
          </tr>
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
td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #2a2a3e; color: #ddd; }
tr:hover td { background: #1e1e2e; }
.id { color: #6b7280; }
.del { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 0.95rem; padding: 0.2rem 0.4rem; border-radius: 4px; }
.del:hover { background: #450a0a; }
</style>
