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
    <div class="page-header">
      <div>
        <h1>Bibliothèque</h1>
        <p class="page-sub">{{ store.songs.length }} morceau(x)</p>
      </div>

      <form class="search-bar" @submit.prevent="search">
        <input v-model="filters.title" placeholder="Titre…" />
        <input v-model="filters.artist" placeholder="Artiste…" />
        <input v-model="filters.genre" placeholder="Genre…" />
        <input v-model="filters.language" placeholder="Langue…" />
        <button type="submit" class="btn-search">Rechercher</button>
        <button type="button" class="btn-reset"
          @click="filters.title = filters.artist = filters.genre = filters.language = ''; store.fetchAll()">
          ✕
        </button>
      </form>
    </div>

    <p v-if="store.loading" class="state-msg">Chargement…</p>
    <p v-else-if="store.error" class="state-msg error">{{ store.error }}</p>
    <p v-else-if="!store.songs.length" class="state-msg">Aucun MP3 trouvé.</p>

    <div v-else class="table-card">
      <table>
        <colgroup>
          <col style="width:3.5rem" />
          <col style="width:18%" />
          <col style="width:15%" />
          <col style="width:14%" />
          <col style="width:9%" />
          <col style="width:6%" />
          <col style="width:6%" />
          <col style="width:7%" />
          <col style="width:110px" />
        </colgroup>
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
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="mp3 in store.songs" :key="mp3.id">
            <tr v-if="editingId !== mp3.id" class="data-row">
              <td class="col-id-cell">{{ mp3.id }}</td>
              <td class="col-title-cell">{{ mp3.title ?? '(sans titre)' }}</td>
              <td class="col-artist-cell">{{ mp3.artist ?? '—' }}</td>
              <td class="muted">{{ mp3.album ?? '—' }}</td>
              <td>
                <span v-if="mp3.genre" class="badge-genre">{{ mp3.genre }}</span>
                <span v-else class="muted">—</span>
              </td>
              <td class="col-year-cell">{{ mp3.year ?? '—' }}</td>
              <td class="col-dur-cell">{{ formatTime(mp3.duration) }}</td>
              <td class="col-lang-cell">{{ mp3.language ?? '—' }}</td>
              <td>
                <div class="actions-cell">
                  <button class="btn-edit" @click="startEdit(mp3)">Modifier</button>
                  <button class="btn-del" @click="store.remove(mp3.id)" title="Supprimer">✕</button>
                </div>
              </td>
            </tr>
            <tr v-else class="edit-row">
              <td class="col-id-cell">{{ mp3.id }}</td>
              <td><input v-model="editForm.title" placeholder="Titre" /></td>
              <td><input v-model="editForm.artist" placeholder="Artiste" /></td>
              <td><input v-model="editForm.album" placeholder="Album" /></td>
              <td><input v-model="editForm.genre" placeholder="Genre" /></td>
              <td><input v-model="editForm.year" type="number" placeholder="Année" /></td>
              <td class="col-dur-cell">{{ formatTime(mp3.duration) }}</td>
              <td><input v-model="editForm.language" placeholder="Langue" /></td>
              <td>
                <div class="actions-cell">
                  <button class="btn-save" @click="saveEdit(mp3.id)" :disabled="saving">
                    {{ saving ? '…' : '✓' }}
                  </button>
                  <button class="btn-cancel" @click="cancelEdit">✕</button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem 1.5rem; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

h1 {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--text) 0%, var(--text-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-sub {
  font-size: 0.82rem;
  color: var(--text-3);
  margin-top: 0.2rem;
}

/* Search bar */
.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.search-bar input {
  padding: 0.45rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-2);
  color: var(--text);
  font-size: 0.85rem;
  outline: none;
  transition: var(--transition);
  min-width: 110px;
}

.search-bar input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.search-bar input::placeholder { color: var(--text-3); }

.btn-search {
  padding: 0.45rem 1rem;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: var(--transition);
}

.btn-search:hover { background: var(--accent-2); }

.btn-reset {
  padding: 0.45rem 0.65rem;
  background: var(--surface-3);
  color: var(--text-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: var(--transition);
}

.btn-reset:hover { color: var(--red); background: var(--red-dim); border-color: transparent; }

/* Table */
.table-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  table-layout: fixed;
}

colgroup .col-id    { width: 3.5rem; }
colgroup .col-title { width: 18%; }
colgroup .col-artist{ width: 15%; }
colgroup .col-album { width: 14%; }
colgroup .col-genre { width: 9%; }
colgroup .col-year  { width: 6%; }
colgroup .col-dur   { width: 6%; }
colgroup .col-lang  { width: 7%; }
colgroup .col-act   { width: 110px; }

thead { position: sticky; top: 0; z-index: 5; }

th {
  text-align: left;
  padding: 0.65rem 0.75rem;
  background: var(--surface-2);
  color: var(--text-3);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  overflow: hidden;
}

td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  vertical-align: middle;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: var(--surface);
}

tbody tr:last-child td { border-bottom: none; }
.data-row:hover td { background: var(--surface-2); }
.edit-row td { background: rgba(124, 58, 237, 0.06); border-bottom-color: rgba(124, 58, 237, 0.2); }

.col-id-cell { color: var(--text-3); font-size: 0.78rem; }
.col-title-cell { font-weight: 500; color: var(--text); }
.col-artist-cell { color: var(--text-2); }
.col-dur-cell { color: var(--text-3); font-variant-numeric: tabular-nums; }
.col-year-cell { color: var(--text-3); }
.col-lang-cell { color: var(--text-3); }
.muted { color: var(--text-3); }

.badge-genre {
  background: var(--accent-dim);
  color: var(--accent-light);
  border: 1px solid rgba(124, 58, 237, 0.25);
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 500;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Edit row inputs */
.edit-row input {
  padding: 0.28rem 0.45rem;
  border: 1px solid var(--accent);
  border-radius: 6px;
  background: var(--surface-3);
  color: var(--text);
  font-size: 0.82rem;
  width: 100%;
  outline: none;
}

.edit-row input:focus { box-shadow: 0 0 0 2px var(--accent-glow); }

/* Action cell */
.actions-cell {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-edit {
  background: rgba(59, 130, 246, 0.12);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.22);
  padding: 0.22rem 0.55rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 600;
  transition: var(--transition);
  white-space: nowrap;
}

.btn-edit:hover { background: rgba(59, 130, 246, 0.25); }

.btn-del {
  background: none;
  border: none;
  color: var(--text-3);
  cursor: pointer;
  font-size: 0.75rem;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  flex-shrink: 0;
}

.btn-del:hover { color: var(--red); background: var(--red-dim); }

.btn-save {
  background: var(--green-dim);
  color: var(--green);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 0.22rem 0.55rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
  transition: var(--transition);
}

.btn-save:disabled { opacity: 0.4; cursor: default; }

.btn-cancel {
  background: var(--surface-3);
  color: var(--text-2);
  border: 1px solid var(--border);
  width: 22px;
  height: 22px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  flex-shrink: 0;
}

.btn-cancel:hover { background: var(--border); color: var(--text); }

.state-msg {
  color: var(--text-2);
  text-align: center;
  padding: 3rem;
}

.state-msg.error { color: var(--red); }
</style>
