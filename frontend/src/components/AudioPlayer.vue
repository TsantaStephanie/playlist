<script setup lang="ts">
import { ref, watch } from 'vue'
import { api } from '@/api/client'
import type { PlaylistItem } from '@/types'

const props = defineProps<{ items: PlaylistItem[] }>()

const currentIndex = ref(0)
const audioRef = ref<HTMLAudioElement | null>(null)
const playing = ref(false)
const currentTime = ref(0)
const totalDuration = ref(0)

const current = () => props.items[currentIndex.value]!

function formatTime(s: number): string {
  if (!s || isNaN(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function play(index: number) {
  currentIndex.value = index
}

function togglePlay() {
  if (!audioRef.value) return
  if (playing.value) audioRef.value.pause()
  else audioRef.value.play()
}

function prev() {
  if (currentIndex.value > 0) currentIndex.value--
}

function next() {
  if (currentIndex.value < props.items.length - 1) currentIndex.value++
}

function seek(e: Event) {
  if (!audioRef.value) return
  audioRef.value.currentTime = Number((e.target as HTMLInputElement).value)
}

function playAll() {
  currentIndex.value = 0
  setTimeout(() => audioRef.value?.play(), 50)
}

function pause() {
  audioRef.value?.pause()
}

watch(currentIndex, () => {
  currentTime.value = 0
  totalDuration.value = 0
  setTimeout(() => audioRef.value?.play(), 50)
})

const emit = defineEmits<{ 'update:playing': [boolean] }>()
defineExpose({ playAll, pause, togglePlay })
</script>

<template>
  <div class="player" v-if="items.length">
    <audio
      ref="audioRef"
      :src="api.mp3.streamUrl(current().mp3.id)"
      @play="playing = true; emit('update:playing', true)"
      @pause="playing = false; emit('update:playing', false)"
      @ended="next"
      @timeupdate="currentTime = audioRef?.currentTime ?? 0"
      @loadedmetadata="totalDuration = audioRef?.duration ?? 0"
      style="display:none"
    />

    <!-- En cours de lecture -->
    <div class="now-playing">
      <div class="cover-art">
        <span class="cover-note">♪</span>
        <div class="cover-eq" v-if="playing">
          <span></span><span></span><span></span>
        </div>
      </div>
      <div class="track-info">
        <div class="track-title">{{ current().mp3.title ?? current().mp3.file_path.split(/[\\/]/).pop() }}</div>
        <div class="track-meta">
          <span class="track-artist">{{ current().mp3.artist ?? 'Artiste inconnu' }}</span>
          <span v-if="current().mp3.genre" class="track-genre">{{ current().mp3.genre }}</span>
        </div>
      </div>
      <div class="track-dur">{{ formatTime(current().mp3.duration) }}</div>
    </div>

    <!-- Barre de progression -->
    <div class="progress-section">
      <span class="time-label">{{ formatTime(currentTime) }}</span>
      <div class="progress-wrap">
        <input
          type="range"
          class="progress-bar"
          :max="totalDuration || 1"
          :value="currentTime"
          @input="seek"
          :style="`--pct: ${totalDuration ? (currentTime / totalDuration) * 100 : 0}%`"
        />
      </div>
      <span class="time-label">{{ formatTime(totalDuration) }}</span>
    </div>

    <!-- Contrôles -->
    <div class="controls">
      <button @click="prev" :disabled="currentIndex === 0" class="ctrl-btn">⏮</button>
      <button @click="togglePlay" class="ctrl-btn play-btn">
        {{ playing ? '⏸' : '▶' }}
      </button>
      <button @click="next" :disabled="currentIndex === items.length - 1" class="ctrl-btn">⏭</button>
    </div>

    <!-- Liste des pistes -->
    <div class="track-list-header">
      <span>Piste</span>
      <span>Durée</span>
    </div>
    <ul class="track-list">
      <li
        v-for="(item, i) in items"
        :key="item.id"
        :class="{ active: i === currentIndex }"
        @click="play(i)"
      >
        <span class="pos">
          <span v-if="playing && i === currentIndex" class="playing-dot">●</span>
          <span v-else>{{ item.position }}</span>
        </span>
        <div class="tl-info">
          <span class="tl-title">{{ item.mp3.title ?? '(sans titre)' }}</span>
          <span class="tl-artist">{{ item.mp3.artist ?? '—' }}</span>
        </div>
        <span class="tl-dur">{{ formatTime(item.mp3.duration) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.player {
  color: var(--text);
}

/* Cover art */
.now-playing {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-2);
  border-radius: var(--radius);
  margin-bottom: 1rem;
  border: 1px solid var(--border);
}

.cover-art {
  flex-shrink: 0;
  width: 58px;
  height: 58px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4c1d95, #1e3a5f);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.cover-note { font-size: 1.5rem; opacity: 0.7; }

.cover-eq {
  position: absolute;
  bottom: 6px;
  right: 6px;
  display: flex;
  align-items: flex-end;
  gap: 2px;
}

.cover-eq span {
  display: block;
  width: 3px;
  background: var(--accent-light);
  border-radius: 2px;
  animation: eq-bar 0.8s ease-in-out infinite alternate;
}
.cover-eq span:nth-child(1) { height: 8px; animation-delay: 0s; }
.cover-eq span:nth-child(2) { height: 14px; animation-delay: 0.2s; }
.cover-eq span:nth-child(3) { height: 6px; animation-delay: 0.4s; }

@keyframes eq-bar {
  from { transform: scaleY(0.3); }
  to { transform: scaleY(1); }
}

.track-info { flex: 1; min-width: 0; }

.track-title {
  font-weight: 700;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
  margin-bottom: 0.25rem;
}

.track-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.track-artist {
  font-size: 0.82rem;
  color: var(--text-2);
}

.track-genre {
  font-size: 0.72rem;
  color: var(--accent-light);
  background: var(--accent-dim);
  padding: 0.1rem 0.5rem;
  border-radius: 99px;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

.track-dur {
  font-size: 0.82rem;
  color: var(--text-3);
  flex-shrink: 0;
}

/* Progress */
.progress-section {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
  padding: 0 0.25rem;
}

.time-label {
  font-size: 0.75rem;
  color: var(--text-3);
  width: 2.8rem;
  flex-shrink: 0;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.progress-wrap { flex: 1; }

.progress-bar {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 99px;
  background: linear-gradient(to right, var(--accent) var(--pct), var(--surface-3) var(--pct));
  cursor: pointer;
  outline: none;
  border: none;
}

.progress-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent-light);
  box-shadow: 0 0 6px var(--accent-glow);
  cursor: pointer;
  transition: transform 0.15s;
}

.progress-bar:hover::-webkit-slider-thumb { transform: scale(1.3); }

/* Controls */
.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.ctrl-btn {
  background: var(--surface-3);
  border: 1px solid var(--border);
  color: var(--text-2);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.ctrl-btn:hover:not(:disabled) {
  background: var(--border);
  color: var(--text);
}

.ctrl-btn:disabled { opacity: 0.25; cursor: default; }

.play-btn {
  background: var(--accent) !important;
  border-color: transparent !important;
  color: #fff !important;
  width: 48px !important;
  height: 48px !important;
  font-size: 1.1rem !important;
  box-shadow: 0 0 18px var(--accent-glow);
}

.play-btn:hover:not(:disabled) {
  background: var(--accent-2) !important;
  box-shadow: 0 0 28px var(--accent-glow);
  transform: scale(1.05);
}

/* Track list */
.track-list-header {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0.75rem;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-3);
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.25rem;
}

.track-list {
  list-style: none;
  max-height: 300px;
  overflow-y: auto;
}

.track-list li {
  display: grid;
  grid-template-columns: 2rem 1fr 3.5rem;
  gap: 0.5rem;
  padding: 0.55rem 0.75rem;
  cursor: pointer;
  border-radius: 8px;
  align-items: center;
  transition: var(--transition);
}

.track-list li:hover { background: var(--surface-2); }

.track-list li.active {
  background: var(--accent-dim);
  border: 1px solid rgba(124, 58, 237, 0.2);
}

.track-list li.active .tl-title { color: var(--accent-light); }

.pos {
  font-size: 0.78rem;
  color: var(--text-3);
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.playing-dot {
  color: var(--accent-light);
  font-size: 0.6rem;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.tl-info { min-width: 0; }

.tl-title {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
  margin-bottom: 0.1rem;
}

.tl-artist {
  display: block;
  font-size: 0.75rem;
  color: var(--text-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tl-dur {
  font-size: 0.78rem;
  color: var(--text-3);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
