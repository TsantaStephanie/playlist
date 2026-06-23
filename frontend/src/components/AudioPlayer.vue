<script setup lang="ts">
import { ref, watch } from 'vue'
import { api } from '@/api/client'
import type { PlaylistItem } from '@/types'

const props = defineProps<{ items: PlaylistItem[] }>()

const currentIndex = ref(0)
const audioRef = ref<HTMLAudioElement | null>(null)
const playing = ref(false)

const current = () => props.items[currentIndex.value]!


function formatTime(s: number): string {
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

watch(currentIndex, () => {
  setTimeout(() => audioRef.value?.play(), 50)
})
</script>

<template>
  <div class="player" v-if="items.length">
    <audio
      ref="audioRef"
      :src="api.mp3.streamUrl(current().mp3.id)"
      @play="playing = true"
      @pause="playing = false"
      @ended="next"
      controls
      class="audio-elem"
    />

    <div class="now-playing">
      <span class="track-title">{{ current().mp3.title ?? current().mp3.file_path.split(/[\\/]/).pop() }}</span>
      <span class="track-artist">{{ current().mp3.artist ?? '—' }}</span>
      <span class="track-duration">{{ formatTime(current().mp3.duration) }}</span>
    </div>

    <div class="controls">
      <button @click="prev" :disabled="currentIndex === 0">⏮</button>
      <button @click="togglePlay" class="play-btn">{{ playing ? '⏸' : '▶' }}</button>
      <button @click="next" :disabled="currentIndex === items.length - 1">⏭</button>
    </div>

    <ul class="track-list">
      <li
        v-for="(item, i) in items"
        :key="item.id"
        :class="{ active: i === currentIndex }"
        @click="play(i)"
      >
        <span class="pos">{{ item.position }}</span>
        <span class="name">{{ item.mp3.title ?? '(sans titre)' }}</span>
        <span class="artist">{{ item.mp3.artist ?? '—' }}</span>
        <span class="dur">{{ formatTime(item.mp3.duration) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.player { background: #1a1a2e; border-radius: 12px; padding: 1rem; color: #eee; }
.audio-elem { width: 100%; margin-bottom: 0.75rem; }
.now-playing { display: flex; gap: 1rem; align-items: baseline; margin-bottom: 0.5rem; flex-wrap: wrap; }
.track-title { font-weight: 700; font-size: 1rem; }
.track-artist { color: #aaa; font-size: 0.9rem; }
.track-duration { margin-left: auto; color: #888; font-size: 0.85rem; }
.controls { display: flex; gap: 0.75rem; justify-content: center; margin-bottom: 1rem; }
.controls button { background: #2d2d4e; border: none; color: #eee; padding: 0.4rem 0.9rem; border-radius: 6px; cursor: pointer; font-size: 1.1rem; }
.controls button:disabled { opacity: 0.3; cursor: default; }
.play-btn { background: #7c3aed !important; font-size: 1.3rem !important; }
.track-list { list-style: none; padding: 0; margin: 0; max-height: 280px; overflow-y: auto; }
.track-list li { display: grid; grid-template-columns: 2rem 1fr 1fr 3.5rem; gap: 0.5rem; padding: 0.5rem 0.4rem; cursor: pointer; border-radius: 6px; font-size: 0.85rem; align-items: center; }
.track-list li:hover { background: #2d2d4e; }
.track-list li.active { background: #3b1f6e; color: #c4b5fd; }
.pos { color: #666; text-align: right; }
.artist { color: #aaa; }
.dur { color: #888; text-align: right; }
</style>
