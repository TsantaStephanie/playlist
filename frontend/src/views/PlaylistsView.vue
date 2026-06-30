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
    <h1>Mes playlists</h1>

    <p v-if="store.loading" class="info">Chargement…</p>
    <p v-else-if="store.error" class="error">{{ store.error }}</p>
    <p v-else-if="!store.playlists.length" class="info">
      Aucune playlist sauvegardée.
      <router-link to="/generate">Créer une playlist →</router-link>
    </p>

    <div v-else class="layout">
      <ul class="sidebar">
        <li
          v-for="pl in store.playlists"
          :key="pl.id"
          :class="{ active: selected?.id === pl.id }"
          @click="selected = pl"
        >
          <div class="pl-name">{{ pl.name }}</div>
          <div class="pl-meta">{{ pl.total_tracks }} titres · {{ formatTime(pl.total_duration) }}</div>
          <button class="del" @click.stop="store.remove(pl.id)" title="Supprimer">✕</button>
        </li>
      </ul>

      <div class="detail" v-if="selected">
        <div class="detail-header">
          <h2>{{ selected.name }}</h2>
          <span class="meta">{{ selected.total_tracks }} titres · {{ formatTime(selected.total_duration) }}</span>
          <button @click="togglePlayAll" class="btn-play-all">
            {{ isPlaying ? '⏸ Pause' : '▶ Lire tout' }}
          </button>
          <a :href="api.playlist.downloadUrl(selected.id)" download class="btn-download">
            Télécharger ZIP
          </a>
        </div>
        <AudioPlayer
          ref="audioPlayerRef"
          :items="selected.items"
          @update:playing="isPlaying = $event"
        />
      </div>
      <div class="detail empty" v-else>
        <p>Sélectionne une playlist pour l'écouter.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem; }
h1 { margin-bottom: 1.25rem; font-size: 1.5rem; }
.info { color: #aaa; }
.info a { color: #c4b5fd; }
.error { color: #f87171; }
.layout { display: grid; grid-template-columns: 280px 1fr; gap: 1.5rem; align-items: start; }
.sidebar { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.sidebar li { background: #1a1a2e; border-radius: 8px; padding: 0.75rem 1rem; cursor: pointer; position: relative; transition: background 0.15s; }
.sidebar li:hover { background: #2d2d4e; }
.sidebar li.active { background: #3b1f6e; border-left: 3px solid #7c3aed; }
.pl-name { font-weight: 600; font-size: 0.95rem; margin-bottom: 0.2rem; }
.pl-meta { font-size: 0.8rem; color: #9ca3af; }
.del { position: absolute; top: 0.6rem; right: 0.6rem; background: none; border: none; color: #ef4444; cursor: pointer; font-size: 0.85rem; padding: 0.15rem 0.35rem; border-radius: 4px; }
.del:hover { background: #450a0a; }
.detail { background: #1a1a2e; border-radius: 12px; padding: 1.25rem; }
.detail.empty { display: flex; align-items: center; justify-content: center; min-height: 200px; color: #6b7280; }
.detail-header { margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
h2 { font-size: 1.15rem; margin: 0; }
.meta { font-size: 0.85rem; color: #9ca3af; flex: 1; }
.btn-play-all { background: #7c3aed; color: #fff; border: none; padding: 0.4rem 1.1rem; border-radius: 6px; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
.btn-play-all:hover { background: #6d28d9; }
.btn-download { background: #1d4ed8; color: #bfdbfe; border: none; padding: 0.35rem 0.9rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; text-decoration: none; }
.btn-download:hover { background: #2563eb; }
</style>
