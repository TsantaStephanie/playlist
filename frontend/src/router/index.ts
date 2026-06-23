import { createRouter, createWebHistory } from 'vue-router'
import MP3ListView from '@/views/MP3ListView.vue'
import PlaylistBuilderView from '@/views/PlaylistBuilderView.vue'
import PlaylistsView from '@/views/PlaylistsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/mp3' },
    { path: '/mp3', component: MP3ListView },
    { path: '/generate', component: PlaylistBuilderView },
    { path: '/playlists', component: PlaylistsView },
  ],
})

export default router
