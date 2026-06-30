<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
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

const targetPlaylistId = ref<number | 'new'>('new')
const targetPlaylist = computed(() =>
  targetPlaylistId.value === 'new'
    ? null
    : store.playlists.find(p => p.id === Number(targetPlaylistId.value)) ?? null
)

const artistStates = ref<Record<string, 'include' | 'exclude'>>({})
const genreStates = ref<Record<string, 'include' | 'exclude'>>({})
const availableArtists = ref<string[]>([])
const availableGenres = ref<string[]>([])

onMounted(async () => {
  await store.fetchAll()
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
    name: targetPlaylist.value?.name ?? form.name ?? 'Ma playlist',
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
    if (targetPlaylistId.value !== 'new' && targetPlaylist.value) {
      const pl = await api.playlist.get(Number(targetPlaylistId.value))
      const existingIds = pl.items.map(item => item.mp3.id)
      const newIds = proposal.items.map(mp3 => mp3.id)
      const mergedIds = [...existingIds, ...newIds.filter(id => !existingIds.includes(id))]
      await api.playlist.update(Number(targetPlaylistId.value), targetPlaylist.value.name, mergedIds)
    } else {
      await api.playlist.save(form.name || 'Ma playlist', {}, proposal.items.map(mp3 => mp3.id))
    }
    router.push('/playlists')
  } finally {
    saving.value = null
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>Générer une playlist</h1>
      <p class="page-sub">Sélectionne tes critères et laisse l'algorithme composer</p>
    </div>

    <div class="builder-grid">
      <!-- Formulaire -->
      <form class="form-card" @submit.prevent="generate">
        <div class="form-section">
          <div class="section-label">Configuration</div>
          <div class="form-row">
            <label class="field">
              <span class="field-label">Durée cible <span class="req">*</span></span>
              <div class="input-with-unit">
                <input type="number" v-model.number="form.duration_minutes" min="1" required />
                <span class="unit">min</span>
              </div>
            </label>

            <label class="field">
              <span class="field-label">Playlist cible</span>
              <select v-model="targetPlaylistId" class="select-field">
                <option value="new">+ Créer nouveau</option>
                <option v-for="pl in store.playlists" :key="pl.id" :value="pl.id">
                  {{ pl.name }} ({{ pl.total_tracks }} titres)
                </option>
              </select>
            </label>

            <label class="field" v-if="targetPlaylistId === 'new'">
              <span class="field-label">Nom</span>
              <input type="text" v-model="form.name" placeholder="Ma playlist" />
            </label>

            <label class="field">
              <span class="field-label">Langue</span>
              <input type="text" v-model="form.language" placeholder="ex: mg" />
            </label>
          </div>

          <div class="form-row">
            <label class="field">
              <span class="field-label">Année de</span>
              <input type="number" v-model="form.year_from" placeholder="2000" />
            </label>
            <label class="field">
              <span class="field-label">Année à</span>
              <input type="number" v-model="form.year_to" placeholder="2024" />
            </label>
          </div>
        </div>

        <div class="form-section">
          <div class="section-label">
            Artistes
            <span class="hint-inline">1× inclure · 2× exclure · 3× désélectionner</span>
          </div>
          <div class="tags-wrap" v-if="availableArtists.length">
            <span
              v-for="a in availableArtists" :key="a"
              class="tag" :class="stateClass(artistStates[a])"
              @click="toggleArtist(a)"
            >
              <span class="tag-icon">{{ artistStates[a] === 'include' ? '✓' : artistStates[a] === 'exclude' ? '✕' : '+' }}</span>
              {{ a }}
            </span>
          </div>
          <p v-else class="empty-tags">Aucun artiste disponible</p>
        </div>

        <div class="form-section">
          <div class="section-label">Genres</div>
          <div class="tags-wrap" v-if="availableGenres.length">
            <span
              v-for="g in availableGenres" :key="g"
              class="tag" :class="stateClass(genreStates[g])"
              @click="toggleGenre(g)"
            >
              <span class="tag-icon">{{ genreStates[g] === 'include' ? '✓' : genreStates[g] === 'exclude' ? '✕' : '+' }}</span>
              {{ g }}
            </span>
          </div>
          <p v-else class="empty-tags">Aucun genre disponible</p>
        </div>

        <button type="submit" class="btn-generate" :disabled="store.loading">
          <span v-if="store.loading" class="spinner">⟳</span>
          {{ store.loading ? 'Génération en cours…' : '✦ Générer la playlist' }}
        </button>
      </form>

      <!-- Résultats -->
      <div class="results" v-if="store.candidates.length || store.error">
        <p v-if="store.error" class="state-msg error">{{ store.error }}</p>

        <div v-for="pl in store.candidates" :key="pl.name" class="candidate-card">
          <div class="candidate-header">
            <div class="candidate-cover">♫</div>
            <div class="candidate-info">
              <div class="candidate-name">{{ pl.name }}</div>
              <div class="candidate-meta">{{ pl.total_tracks }} titres · {{ formatTime(pl.total_duration) }}</div>
            </div>
            <button class="btn-save" @click="save(pl)" :disabled="saving === pl.name">
              {{ saving === pl.name ? '…' : targetPlaylistId !== 'new' ? '+ Ajouter' : '↓ Sauvegarder' }}
            </button>
          </div>

          <div class="track-list-header">
            <span>#</span><span>Titre</span><span>Artiste</span><span>Genre</span><span>Année</span><span>Durée</span>
          </div>
          <ul class="track-list">
            <li v-for="(mp3, idx) in pl.items" :key="mp3.id">
              <span class="tl-pos">{{ idx + 1 }}</span>
              <span class="tl-title">{{ mp3.title ?? '(sans titre)' }}</span>
              <span class="tl-artist">{{ mp3.artist ?? '—' }}</span>
              <span class="tl-genre">{{ mp3.genre ?? '—' }}</span>
              <span class="tl-year">{{ mp3.year ?? '—' }}</span>
              <span class="tl-dur">{{ formatTime(mp3.duration) }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem 1.5rem; }

.page-header { margin-bottom: 2rem; }

h1 {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--text) 0%, var(--text-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.3rem;
}

.page-sub { font-size: 0.875rem; color: var(--text-3); }

.builder-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 900px) {
  .builder-grid { grid-template-columns: 1fr; }
}

/* Form card */
.form-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.form-section {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.form-section:last-of-type { border-bottom: none; }

.section-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-3);
  margin-bottom: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.hint-inline {
  font-size: 0.7rem;
  color: var(--text-3);
  text-transform: none;
  letter-spacing: 0;
  font-weight: 400;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin-bottom: 0.85rem;
}

.form-row:last-child { margin-bottom: 0; }

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 130px;
}

.field-label {
  font-size: 0.78rem;
  color: var(--text-2);
  font-weight: 500;
}

.req { color: var(--red); }

.field input, .select-field {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-2);
  color: var(--text);
  font-size: 0.875rem;
  outline: none;
  transition: var(--transition);
}

.field input:focus, .select-field:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.field input::placeholder { color: var(--text-3); }
.select-field { cursor: pointer; width: 100%; }

.input-with-unit { position: relative; }
.input-with-unit input { padding-right: 2.5rem; width: 100%; }
.unit {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.78rem;
  color: var(--text-3);
  pointer-events: none;
}

/* Tags */
.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.7rem;
  border-radius: 99px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  background: var(--surface-3);
  color: var(--text-2);
  border: 1px solid var(--border);
  user-select: none;
  transition: var(--transition);
}

.tag:hover { background: var(--border); color: var(--text); }

.tag.state-include {
  background: var(--green-dim);
  color: #6ee7b7;
  border-color: rgba(16, 185, 129, 0.3);
}

.tag.state-exclude {
  background: var(--red-dim);
  color: #fca5a5;
  border-color: rgba(244, 63, 94, 0.3);
}

.tag-icon { font-size: 0.7rem; opacity: 0.8; }
.empty-tags { font-size: 0.82rem; color: var(--text-3); }

/* Generate button */
.btn-generate {
  display: block;
  width: calc(100% - 3rem);
  margin: 1.25rem 1.5rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, var(--accent), #3b82f6);
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.35);
  transition: var(--transition);
}

.btn-generate:hover:not(:disabled) {
  box-shadow: 0 6px 28px rgba(124, 58, 237, 0.5);
  transform: translateY(-1px);
}

.btn-generate:disabled { opacity: 0.5; cursor: default; transform: none; }

.spinner { display: inline-block; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Results */
.results { display: flex; flex-direction: column; gap: 1rem; }

.state-msg { color: var(--text-2); }
.state-msg.error { color: var(--red); }

.candidate-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.candidate-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(to right, rgba(124, 58, 237, 0.08), transparent);
  border-bottom: 1px solid var(--border);
}

.candidate-cover {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4c1d95, #1e3a5f);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: var(--accent-light);
  flex-shrink: 0;
}

.candidate-info { flex: 1; }

.candidate-name {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text);
  margin-bottom: 0.2rem;
}

.candidate-meta { font-size: 0.8rem; color: var(--text-2); }

.btn-save {
  background: var(--green-dim);
  color: var(--green);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: var(--transition);
  white-space: nowrap;
}

.btn-save:hover:not(:disabled) { background: rgba(16, 185, 129, 0.25); }
.btn-save:disabled { opacity: 0.4; cursor: default; }

/* Track list */
.track-list-header {
  display: grid;
  grid-template-columns: 2rem 1fr 1fr 1fr 3rem 4rem;
  gap: 0.5rem;
  padding: 0.4rem 1.25rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-3);
  border-bottom: 1px solid var(--border);
}

.track-list { list-style: none; }

.track-list li {
  display: grid;
  grid-template-columns: 2rem 1fr 1fr 1fr 3rem 4rem;
  gap: 0.5rem;
  padding: 0.55rem 1.25rem;
  font-size: 0.83rem;
  border-bottom: 1px solid var(--border);
  align-items: center;
  transition: var(--transition);
}

.track-list li:last-child { border-bottom: none; }
.track-list li:hover { background: var(--surface-2); }

.tl-pos { color: var(--text-3); text-align: center; }
.tl-title { color: var(--text); font-weight: 500; }
.tl-artist { color: var(--text-2); }
.tl-genre { color: var(--accent-light); font-size: 0.78rem; }
.tl-year { color: var(--text-3); text-align: center; }
.tl-dur { color: var(--text-3); text-align: right; font-variant-numeric: tabular-nums; }
</style>
