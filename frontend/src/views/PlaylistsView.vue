<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { usePlaylistStore } from '@/stores/playlist'
import { api } from '@/api/client'
import AudioPlayer from '@/components/AudioPlayer.vue'
import type { Playlist } from '@/types'

const store = usePlaylistStore()
const selected = ref<Playlist | null>(null)
const audioPlayerRef = ref<InstanceType<typeof AudioPlayer> | null>(null)
const isPlaying = ref(false)

function formatTime(s: number) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}min ${sec}s`
}

function togglePlayAll() {
  if (isPlaying.value) audioPlayerRef.value?.pause()
  else audioPlayerRef.value?.playAll()
}

watch(selected, () => {
  isPlaying.value = false
})

onMounted(() => store.fetchAll())
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>Mes playlists</h1>
      <span class="page-count" v-if="store.playlists.length">{{ store.playlists.length }} playlist{{ store.playlists.length > 1 ? 's' : '' }}</span>
    </div>

    <p v-if="store.loading" class="state-msg">Chargement…</p>
    <p v-else-if="store.error" class="state-msg error">{{ store.error }}</p>
    <p v-else-if="!store.playlists.length" class="state-msg">
      Aucune playlist.
      <router-link to="/generate">Créer une playlist →</router-link>
    </p>

    <div v-else class="layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-label">Mes playlists</div>
        <ul class="pl-list">
          <li
            v-for="pl in store.playlists"
            :key="pl.id"
            :class="{ active: selected?.id === pl.id }"
            @click="selected = pl"
          >
            <div class="pl-icon">♫</div>
            <div class="pl-body">
              <div class="pl-name">{{ pl.name }}</div>
              <div class="pl-meta">{{ pl.total_tracks }} titres · {{ formatTime(pl.total_duration) }}</div>
            </div>
            <button class="pl-del" @click.stop="store.remove(pl.id)" title="Supprimer">✕</button>
          </li>
        </ul>
      </aside>

      <!-- Détail -->
      <div class="detail" v-if="selected">
        <div class="detail-hero">
          <div class="hero-cover">
            <span class="hero-note">♫</span>
          </div>
          <div class="hero-info">
            <div class="hero-label">PLAYLIST</div>
            <h2 class="hero-title">{{ selected.name }}</h2>
            <div class="hero-meta">{{ selected.total_tracks }} titres · {{ formatTime(selected.total_duration) }}</div>
            <div class="hero-actions">
              <button @click="togglePlayAll" class="btn-play-all">
                <span class="btn-play-icon">{{ isPlaying ? '⏸' : '▶' }}</span>
                {{ isPlaying ? 'Pause' : 'Lire tout' }}
              </button>
              <a :href="api.playlist.downloadUrl(selected.id)" download class="btn-download">
                ↓ Télécharger ZIP
              </a>
            </div>
          </div>
        </div>

        <AudioPlayer
          ref="audioPlayerRef"
          :items="selected.items"
          @update:playing="isPlaying = $event"
        />
      </div>

      <div class="detail empty" v-else>
        <div class="empty-icon">♫</div>
        <p>Sélectionne une playlist pour l'écouter</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem 1.5rem; }

.page-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 2rem;
}

h1 {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--text) 0%, var(--text-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-count {
  font-size: 0.82rem;
  color: var(--text-3);
  background: var(--surface-2);
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
  border: 1px solid var(--border);
}

.state-msg {
  color: var(--text-2);
  padding: 3rem;
  text-align: center;
}
.state-msg a { color: var(--accent-light); text-decoration: none; }
.state-msg.error { color: var(--red); }

.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 1.5rem;
  align-items: start;
}

/* Sidebar */
.sidebar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.sidebar-label {
  padding: 0.75rem 1rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-3);
  border-bottom: 1px solid var(--border);
}

.pl-list { list-style: none; padding: 0.4rem; }

.pl-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}

.pl-list li:hover { background: var(--surface-2); }

.pl-list li.active {
  background: var(--accent-dim);
  border: 1px solid rgba(124, 58, 237, 0.2);
}

.pl-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: linear-gradient(135deg, #3b1f6e, #1e3a5f);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
  color: var(--accent-light);
}

.pl-body { flex: 1; min-width: 0; padding-right: 1.5rem; }

.pl-name {
  font-size: 0.87rem;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pl-meta {
  font-size: 0.75rem;
  color: var(--text-2);
  margin-top: 0.1rem;
}

.pl-del {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-3);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.25rem;
  border-radius: 4px;
  opacity: 0;
  transition: var(--transition);
}

.pl-list li:hover .pl-del { opacity: 1; }
.pl-del:hover { color: var(--red); background: var(--red-dim); }

/* Detail */
.detail {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.detail.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: var(--text-3);
  gap: 0.75rem;
}

.empty-icon { font-size: 2.5rem; opacity: 0.3; }

/* Hero */
.detail-hero {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.75rem;
  background: linear-gradient(to bottom, rgba(124, 58, 237, 0.12), transparent);
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
}

.hero-cover {
  width: 90px;
  height: 90px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4c1d95 0%, #1e3a8a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--shadow);
}

.hero-note { font-size: 2.5rem; color: rgba(196, 181, 253, 0.6); }

.hero-info { flex: 1; }

.hero-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-3);
  margin-bottom: 0.35rem;
}

.hero-title {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text);
  margin-bottom: 0.3rem;
}

.hero-meta {
  font-size: 0.82rem;
  color: var(--text-2);
  margin-bottom: 1rem;
}

.hero-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }

.btn-play-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: 99px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
  box-shadow: 0 0 20px var(--accent-glow);
  transition: var(--transition);
  letter-spacing: 0.01em;
}

.btn-play-all:hover {
  background: var(--accent-2);
  box-shadow: 0 0 32px var(--accent-glow);
  transform: translateY(-1px);
}

.btn-play-icon { font-size: 0.85rem; }

.btn-download {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--surface-3);
  color: var(--text-2);
  border: 1px solid var(--border);
  padding: 0.5rem 1rem;
  border-radius: 99px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  transition: var(--transition);
}

.btn-download:hover {
  background: var(--border);
  color: var(--text);
}

/* AudioPlayer inside detail */
.detail :deep(.player) { padding: 1.25rem; }
</style>
