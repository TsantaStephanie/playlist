<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePlaylistStore } from '@/stores/playlist'
import { api } from '@/api/client'
import type { Playlist } from '@/types'

const store = usePlaylistStore()
const router = useRouter()

const form = reactive({
  duration_minutes: 35,
  name: 'Ma playlist',
  genre: '',
  artist: '',
  language: '',
  year: '' as number | '',
  exclusionInput: '',
  exclusions: [] as string[],
})

function addExclusion() {
  const val = form.exclusionInput.trim()
  if (val && !form.exclusions.includes(val)) form.exclusions.push(val)
  form.exclusionInput = ''
}

function removeExclusion(ex: string) {
  form.exclusions = form.exclusions.filter((e) => e !== ex)
}

function formatTime(s: number) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}min ${sec}s`
}

async function generate() {
  await store.generate({
    duration_minutes: form.duration_minutes,
    name: form.name || 'Ma playlist',
    genre: form.genre || undefined,
    artist: form.artist || undefined,
    language: form.language || undefined,
    year: form.year !== '' ? Number(form.year) : undefined,
    exclusions: form.exclusions.length ? form.exclusions : undefined,
  })
}

const saving = ref<number | null>(null)

async function save(playlist: Playlist) {
  saving.value = playlist.id
  try {
    await api.playlist.save(
      playlist.name,
      playlist.criteria,
      playlist.items.map((i) => i.mp3.id),
    )
    router.push('/playlists')
  } finally {
    saving.value = null
  }
}
</script>

<template>
  <div class="page">
    <h1>Générer une playlist</h1>

    <form class="builder" @submit.prevent="generate">
      <div class="row">
        <label>
          Durée cible (minutes) <span class="req">*</span>
          <input type="number" v-model.number="form.duration_minutes" min="1" required />
        </label>
        <label>
          Nom de la playlist
          <input type="text" v-model="form.name" placeholder="Ma playlist" />
        </label>
      </div>

      <div class="row">
        <label>Genre <input v-model="form.genre" placeholder="ex: malagasy" /></label>
        <label>Artiste <input v-model="form.artist" placeholder="ex: Mahaleo" /></label>
        <label>Langue <input v-model="form.language" placeholder="ex: mg" /></label>
        <label>Année <input type="number" v-model="form.year" placeholder="ex: 2000" /></label>
      </div>

      <div class="exclusions-block">
        <label>Exclusions</label>
        <div class="excl-row">
          <input
            v-model="form.exclusionInput"
            placeholder="ex: rock"
            @keydown.enter.prevent="addExclusion"
          />
          <button type="button" @click="addExclusion">Ajouter</button>
        </div>
        <div class="tags">
          <span v-for="ex in form.exclusions" :key="ex" class="tag">
            {{ ex }} <button @click="removeExclusion(ex)">✕</button>
          </span>
        </div>
      </div>

      <button type="submit" class="btn-generate" :disabled="store.loading">
        {{ store.loading ? 'Génération…' : 'Générer' }}
      </button>
    </form>

    <p v-if="store.error" class="error">{{ store.error }}</p>

    <div v-if="store.candidates.length" class="results">
      <h2>{{ store.candidates.length }} proposition(s)</h2>
      <div v-for="pl in store.candidates" :key="pl.id" class="candidate">
        <div class="candidate-header">
          <span class="candidate-name">{{ pl.name }}</span>
          <span class="candidate-meta">{{ pl.total_tracks }} titres · {{ formatTime(pl.total_duration) }}</span>
          <button class="btn-save" @click="save(pl)" :disabled="saving === pl.id">
            {{ saving === pl.id ? 'Sauvegarde…' : 'Sauvegarder' }}
          </button>
        </div>
        <ul class="track-list">
          <li v-for="item in pl.items" :key="item.id">
            <span class="pos">{{ item.position }}</span>
            <span class="title">{{ item.mp3.title ?? '(sans titre)' }}</span>
            <span class="artist">{{ item.mp3.artist ?? '—' }}</span>
            <span class="dur">{{ formatTime(item.mp3.duration) }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem; }
h1 { margin-bottom: 1.25rem; font-size: 1.5rem; }
.builder { background: #1a1a2e; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }
.row { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; }
label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.85rem; color: #9ca3af; flex: 1; min-width: 160px; }
.req { color: #f87171; }
input[type="text"], input[type="number"] { padding: 0.45rem 0.75rem; border: 1px solid #374151; border-radius: 6px; background: #111827; color: #eee; font-size: 0.9rem; }
.exclusions-block { margin-bottom: 1rem; }
.exclusions-block label { color: #9ca3af; font-size: 0.85rem; margin-bottom: 0.4rem; display: block; }
.excl-row { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
.excl-row input { flex: 1; padding: 0.45rem 0.75rem; border: 1px solid #374151; border-radius: 6px; background: #111827; color: #eee; font-size: 0.9rem; }
.excl-row button { background: #374151; color: #eee; border: none; border-radius: 6px; padding: 0.45rem 0.9rem; cursor: pointer; }
.tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag { background: #2d2d4e; color: #c4b5fd; padding: 0.25rem 0.6rem; border-radius: 20px; font-size: 0.8rem; display: flex; align-items: center; gap: 0.3rem; }
.tag button { background: none; border: none; color: #c4b5fd; cursor: pointer; font-size: 0.75rem; padding: 0; }
.btn-generate { background: #7c3aed; color: #fff; border: none; padding: 0.6rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
.btn-generate:disabled { opacity: 0.5; cursor: default; }
.error { color: #f87171; margin-bottom: 1rem; }
.results h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #c4b5fd; }
.candidate { background: #1a1a2e; border-radius: 10px; padding: 1rem; margin-bottom: 1.25rem; }
.candidate-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.candidate-name { font-weight: 700; font-size: 1rem; }
.candidate-meta { color: #9ca3af; font-size: 0.85rem; flex: 1; }
.btn-save { background: #059669; color: #fff; border: none; padding: 0.4rem 0.9rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-save:disabled { opacity: 0.5; cursor: default; }
.track-list { list-style: none; padding: 0; margin: 0; }
.track-list li { display: grid; grid-template-columns: 2rem 1fr 1fr 4rem; gap: 0.5rem; padding: 0.4rem 0.3rem; font-size: 0.85rem; border-top: 1px solid #2a2a3e; }
.pos { color: #6b7280; text-align: right; }
.artist { color: #9ca3af; }
.dur { color: #6b7280; text-align: right; }
</style>
