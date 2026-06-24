<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePlaylistStore } from '@/stores/playlist'
import { api } from '@/api/client'
import type { PlaylistProposal } from '@/types'

const store = usePlaylistStore()
const router = useRouter()

const form = reactive({
  duration_minutes: 35,
  name: 'Ma playlist',
  language: '',
  year_from: '' as number | '',
  year_to: '' as number | '',
})

// États tri-state par artiste et genre : 'include' | 'exclude' | null
const artistStates = ref<Record<string, 'include' | 'exclude'>>({})
const genreStates = ref<Record<string, 'include' | 'exclude'>>({})
const availableArtists = ref<string[]>([])
const availableGenres = ref<string[]>([])

onMounted(async () => {
  availableArtists.value = await api.mp3.artists()
  availableGenres.value = await api.mp3.genres()
  console.log('[PlaylistBuilder] artistes:', availableArtists.value, 'genres:', availableGenres.value)
})

function toggleArtist(artist: string) {
  if (!artistStates.value[artist]) artistStates.value[artist] = 'include'
  else if (artistStates.value[artist] === 'include') artistStates.value[artist] = 'exclude'
  else delete artistStates.value[artist]
}

function toggleGenre(genre: string) {
  if (!genreStates.value[genre]) genreStates.value[genre] = 'include'
  else if (genreStates.value[genre] === 'include') genreStates.value[genre] = 'exclude'
  else delete genreStates.value[genre]
}

function stateClass(state: 'include' | 'exclude' | undefined) {
  if (state === 'include') return 'state-include'
  if (state === 'exclude') return 'state-exclude'
  return ''
}

function formatTime(s: number) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}min ${sec}s`
}

async function generate() {
  const artists = Object.entries(artistStates.value).filter(([, s]) => s === 'include').map(([a]) => a)
  const excludedArtists = Object.entries(artistStates.value).filter(([, s]) => s === 'exclude').map(([a]) => a)
  const genres = Object.entries(genreStates.value).filter(([, s]) => s === 'include').map(([g]) => g)
  const excludedGenres = Object.entries(genreStates.value).filter(([, s]) => s === 'exclude').map(([g]) => g)

  console.log('[PlaylistBuilder] generate', { artists, excludedArtists, genres, excludedGenres })

  await store.generate({
    duration_minutes: form.duration_minutes,
    name: form.name || 'Ma playlist',
    artists: artists.length ? artists : undefined,
    excluded_artists: excludedArtists.length ? excludedArtists : undefined,
    genres: genres.length ? genres : undefined,
    excluded_genres: excludedGenres.length ? excludedGenres : undefined,
    language: form.language || undefined,
    year_from: form.year_from !== '' ? Number(form.year_from) : undefined,
    year_to: form.year_to !== '' ? Number(form.year_to) : undefined,
  })
}

const saving = ref<string | null>(null)

async function save(proposal: PlaylistProposal) {
  saving.value = proposal.name
  try {
    await api.playlist.save(proposal.name, {}, proposal.items.map(mp3 => mp3.id))
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
        <label>
          Langue
          <input type="text" v-model="form.language" placeholder="ex: mg" />
        </label>
        <label>
          Année de
          <input type="number" v-model="form.year_from" placeholder="ex: 2000" />
        </label>
        <label>
          Année à
          <input type="number" v-model="form.year_to" placeholder="ex: 2010" />
        </label>
      </div>

      <p class="hint">Cliquez une fois pour <span class="inc">inclure</span>, deux fois pour <span class="exc">exclure</span>, trois fois pour désélectionner.</p>

      <div class="multiselect-block">
        <div class="ms-section">
          <div class="ms-label">Artistes</div>
          <div class="ms-tags">
            <span
              v-for="a in availableArtists" :key="a"
              class="ms-tag" :class="stateClass(artistStates[a])"
              @click="toggleArtist(a)"
            >
              <span class="ms-icon">{{ artistStates[a] === 'include' ? '✓' : artistStates[a] === 'exclude' ? '✕' : '+' }}</span>
              {{ a }}
            </span>
          </div>
        </div>

        <div class="ms-section">
          <div class="ms-label">Genres</div>
          <div class="ms-tags">
            <span
              v-for="g in availableGenres" :key="g"
              class="ms-tag" :class="stateClass(genreStates[g])"
              @click="toggleGenre(g)"
            >
              <span class="ms-icon">{{ genreStates[g] === 'include' ? '✓' : genreStates[g] === 'exclude' ? '✕' : '+' }}</span>
              {{ g }}
            </span>
          </div>
        </div>
      </div>

      <button type="submit" class="btn-generate" :disabled="store.loading">
        {{ store.loading ? 'Génération…' : 'Générer' }}
      </button>
    </form>

    <p v-if="store.error" class="error">{{ store.error }}</p>

    <div v-if="store.candidates.length" class="results">
      <h2>{{ store.candidates.length }} proposition(s)</h2>
      <div v-for="pl in store.candidates" :key="pl.name" class="candidate">
        <div class="candidate-header">
          <span class="candidate-name">{{ pl.name }}</span>
          <span class="candidate-meta">{{ pl.total_tracks }} titres · {{ formatTime(pl.total_duration) }}</span>
          <button class="btn-save" @click="save(pl)" :disabled="saving === pl.name">
            {{ saving === pl.name ? 'Sauvegarde…' : 'Sauvegarder' }}
          </button>
        </div>
        <ul class="track-list">
          <li v-for="(mp3, idx) in pl.items" :key="mp3.id">
            <span class="pos">{{ idx + 1 }}</span>
            <span class="title">{{ mp3.title ?? '(sans titre)' }}</span>
            <span class="artist">{{ mp3.artist ?? '—' }}</span>
            <span class="genre">{{ mp3.genre ?? '—' }}</span>
            <span class="year">{{ mp3.year ?? '—' }}</span>
            <span class="dur">{{ formatTime(mp3.duration) }}</span>
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
.hint { font-size: 0.8rem; color: #6b7280; margin-bottom: 0.75rem; }
.inc { color: #34d399; font-weight: 600; }
.exc { color: #f87171; font-weight: 600; }
.multiselect-block { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.25rem; }
.ms-section { }
.ms-label { font-size: 0.82rem; color: #9ca3af; margin-bottom: 0.4rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.ms-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.ms-tag { display: flex; align-items: center; gap: 0.3rem; padding: 0.3rem 0.7rem; border-radius: 20px; font-size: 0.83rem; cursor: pointer; background: #2a2a3e; color: #9ca3af; border: 1px solid #374151; user-select: none; transition: background 0.15s; }
.ms-tag:hover { background: #374151; color: #eee; }
.ms-tag.state-include { background: #064e3b; color: #6ee7b7; border-color: #065f46; }
.ms-tag.state-exclude { background: #450a0a; color: #fca5a5; border-color: #7f1d1d; }
.ms-icon { font-size: 0.75rem; }
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
.track-list li { display: grid; grid-template-columns: 2rem 1fr 1fr 1fr 3rem 4rem; gap: 0.5rem; padding: 0.4rem 0.3rem; font-size: 0.85rem; border-top: 1px solid #2a2a3e; }
.pos { color: #6b7280; text-align: right; }
.artist { color: #9ca3af; }
.genre { color: #a78bfa; }
.year { color: #6b7280; text-align: center; }
.dur { color: #6b7280; text-align: right; }
</style>
