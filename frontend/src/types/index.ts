export interface MP3 {
  id: number
  file_path: string
  title: string | null
  artist: string | null
  album: string | null
  genre: string | null
  year: number | null
  duration: number
  track_number: number | null
  language: string | null
  bitrate: number | null
  created_at: string
  updated_at: string
}

export interface PlaylistItem {
  id: number
  position: number
  mp3: MP3
}

export interface Playlist {
  id: number
  name: string
  criteria: Record<string, unknown>
  created_at: string
  items: PlaylistItem[]
  total_duration: number
  total_tracks: number
}

export interface GenerateRequest {
  duration_minutes: number
  name?: string
  genre?: string
  artist?: string
  language?: string
  year?: number
  exclusions?: string[]
}

export interface MP3Filters {
  title?: string
  artist?: string
  genre?: string
  year?: number
  language?: string
}
