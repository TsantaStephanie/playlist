<script setup lang="ts"></script>

<template>
  <nav class="navbar">
    <span class="brand">
      <span class="brand-icon">♫</span>
      <span class="brand-text">Playlist & Download</span>
    </span>
    <div class="nav-links">
      <router-link to="/mp3">
        <span class="nav-icon">◈</span> Bibliothèque
      </router-link>
      <router-link to="/generate">
        <span class="nav-icon">✦</span> Générer
      </router-link>
      <router-link to="/playlists">
        <span class="nav-icon">▶</span> Playlists
      </router-link>
    </div>
  </nav>
  <main>
    <router-view />
  </main>
</template>

<style>
:root {
  --bg: #09090f;
  --surface: #111119;
  --surface-2: #1a1a28;
  --surface-3: #232336;
  --border: #2a2a40;
  --border-light: #35354f;
  --accent: #7c3aed;
  --accent-2: #8b5cf6;
  --accent-light: #a78bfa;
  --accent-glow: rgba(124, 58, 237, 0.25);
  --accent-dim: rgba(124, 58, 237, 0.12);
  --text: #e4e4f0;
  --text-2: #8888a8;
  --text-3: #4a4a68;
  --green: #10b981;
  --green-dim: rgba(16, 185, 129, 0.15);
  --red: #f43f5e;
  --red-dim: rgba(244, 63, 94, 0.15);
  --blue: #3b82f6;
  --radius: 10px;
  --radius-lg: 16px;
  --shadow: 0 4px 24px rgba(0, 0, 0, 0.5);
  --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.3);
  --transition: all 0.18s ease;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  background-image:
    radial-gradient(ellipse at 15% 40%, rgba(124, 58, 237, 0.07) 0%, transparent 55%),
    radial-gradient(ellipse at 85% 10%, rgba(59, 130, 246, 0.05) 0%, transparent 45%);
  color: var(--text);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  line-height: 1.5;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-light); }

input, select, button { font-family: inherit; }
</style>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 62px;
  background: rgba(9, 9, 15, 0.82);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.brand-icon {
  font-size: 1.4rem;
  background: linear-gradient(135deg, var(--accent-light), #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-text {
  font-size: 1.1rem;
  font-weight: 800;
  background: linear-gradient(135deg, #c4b5fd, #93c5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-links a {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-2);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  transition: var(--transition);
  letter-spacing: 0.01em;
}

.nav-links a:hover { color: var(--text); background: var(--surface-2); }

.nav-links a.router-link-active {
  color: var(--accent-light);
  background: var(--accent-dim);
  border: 1px solid rgba(124, 58, 237, 0.25);
}

.nav-icon { font-size: 0.75rem; opacity: 0.7; }

main { max-width: 1400px; margin: 0 auto; padding: 0 1rem; }
</style>
