<script setup lang="ts"></script>

<template>
  <nav class="navbar">
    <span class="brand">🎵 Playlist Project </span>
    <router-link to="/mp3">Bibliothèque</router-link>
    <!-- <router-link to="/generate">Générer</router-link> -->
    <!-- <router-link to="/playlists">Playlists</router-link> -->
  </nav>
  <main>
    <router-view />
  </main>
</template>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #dedee8; color: #000000; font-family: system-ui, sans-serif; min-height: 100vh; }
</style>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.85rem 1.5rem;
  background: #1c1c1c;
  border-bottom: 1px solid #515188;
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand { font-weight: 700; font-size: 1.1rem; color: #c4b5fd; margin-right: auto; }
.navbar a { color: #9ca3af; text-decoration: none; font-size: 0.9rem; padding: 0.3rem 0.6rem; border-radius: 6px; transition: color 0.15s; }
.navbar a:hover { color: #e2e8f0; }
.navbar a.router-link-active { color: #c4b5fd; background: #2d2d4e; }
main { max-width: 1200px; margin: 0 auto; }
</style>
