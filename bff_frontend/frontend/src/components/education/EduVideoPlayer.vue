<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  src: String,
  title: String,
  durationSec: { type: Number, default: 0 },
  initialPosition: { type: Number, default: 0 },
})
const emit = defineEmits(['progress', 'complete'])

const SPEEDS = [0.5, 1, 1.25, 1.5, 2]

const videoRef = ref(null)
const containerRef = ref(null)
const seekBarRef = ref(null)

const isPlaying = ref(false)
const currentTime = ref(props.initialPosition)
const duration = ref(props.durationSec)
const volume = ref(1)
const isMuted = ref(false)
const speed = ref(1)
const showSpeedMenu = ref(false)
const isFullscreen = ref(false)
const controlsVisible = ref(true)
const hasError = ref(false)
const isDragging = ref(false)

let progressInterval = null
let hideControlsTimer = null
let watchedSeconds = 0
let completionFired = false

const progress = computed(() => duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0)

// Detect YouTube URL
const youtubeId = computed(() => {
  if (!props.src) return null
  // Match youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
  ]
  for (const p of patterns) {
    const m = props.src.match(p)
    if (m) return m[1]
  }
  return null
})

const isYouTube = computed(() => !!youtubeId.value)

function formatTime(s) {
  s = Math.floor(s)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

function togglePlay() {
  const v = videoRef.value
  if (!v) return
  if (v.paused) { v.play(); isPlaying.value = true }
  else { v.pause(); isPlaying.value = false }
}

function onTimeUpdate() {
  if (!isDragging.value && videoRef.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

function onLoadedMetadata() {
  if (videoRef.value) {
    duration.value = videoRef.value.duration || props.durationSec
    if (props.initialPosition > 0) videoRef.value.currentTime = props.initialPosition
  }
}

function onVideoEnded() {
  isPlaying.value = false
  if (!completionFired) {
    completionFired = true
    emit('complete')
  }
}

function onVideoError() { hasError.value = true }

function seekTo(e) {
  const bar = seekBarRef.value
  if (!bar || !videoRef.value) return
  const rect = bar.getBoundingClientRect()
  const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  videoRef.value.currentTime = pct * duration.value
  currentTime.value = pct * duration.value
}

function toggleMute() {
  isMuted.value = !isMuted.value
  if (videoRef.value) videoRef.value.muted = isMuted.value
}

function changeVolume(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  volume.value = pct
  if (videoRef.value) { videoRef.value.volume = pct; videoRef.value.muted = false }
  isMuted.value = false
}

function setSpeed(s) {
  speed.value = s
  if (videoRef.value) videoRef.value.playbackRate = s
  showSpeedMenu.value = false
}

function toggleFullscreen() {
  const el = containerRef.value
  if (!el) return
  if (!document.fullscreenElement) {
    el.requestFullscreen?.()
    isFullscreen.value = true
  } else {
    document.exitFullscreen?.()
    isFullscreen.value = false
  }
}

function resetHideTimer() {
  controlsVisible.value = true
  clearTimeout(hideControlsTimer)
  if (isPlaying.value) {
    hideControlsTimer = setTimeout(() => { controlsVisible.value = false }, 3000)
  }
}

function onKeydown(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  if (isYouTube.value) return
  const v = videoRef.value
  if (!v) return
  switch (e.key) {
    case ' ':
    case 'k': e.preventDefault(); togglePlay(); break
    case 'ArrowRight': e.preventDefault(); v.currentTime = Math.min(duration.value, v.currentTime + 10); break
    case 'ArrowLeft': e.preventDefault(); v.currentTime = Math.max(0, v.currentTime - 10); break
    case 'f': e.preventDefault(); toggleFullscreen(); break
    case 'm': e.preventDefault(); toggleMute(); break
  }
}

onMounted(() => {
  if (!isYouTube.value) {
    document.addEventListener('keydown', onKeydown)
    progressInterval = setInterval(() => {
      if (isPlaying.value && videoRef.value) {
        watchedSeconds++
        emit('progress', watchedSeconds, Math.floor(videoRef.value.currentTime))
      }
    }, 5000)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  clearInterval(progressInterval)
  clearTimeout(hideControlsTimer)
})
</script>

<template>
  <!-- YouTube embed -->
  <div v-if="isYouTube" ref="containerRef" class="edu-player edu-player--youtube">
    <iframe
      :src="`https://www.youtube.com/embed/${youtubeId}?rel=0&modestbranding=1`"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen
    />
  </div>

  <!-- Native video player -->
  <div
    v-else
    ref="containerRef"
    class="edu-player"
    :class="{ 'edu-player--controls-visible': controlsVisible || !isPlaying }"
    @mousemove="resetHideTimer"
    @mouseleave="isPlaying && (controlsVisible = false)"
  >
    <video
      ref="videoRef"
      :src="src"
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="onVideoEnded"
      @error="onVideoError"
      @click="togglePlay"
    />

    <!-- Error overlay -->
    <div v-if="hasError" style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.8); color: white; gap: 12px;">
      <span class="material-symbols-outlined" style="font-size: 48px; color: var(--edu-error);">error</span>
      <p style="font-size: 14px;">{{ t('education.player.videoError') }}</p>
    </div>

    <!-- Center play button when paused -->
    <div v-if="!isPlaying && !hasError" class="edu-player__center-play" @click="togglePlay">
      <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21" /></svg>
    </div>

    <!-- Controls -->
    <div class="edu-player__controls">
      <!-- Seek bar -->
      <div ref="seekBarRef" class="edu-player__seekbar" @click="seekTo">
        <div class="edu-player__seekbar-fill" :style="{ width: progress + '%' }" />
        <div class="edu-player__seekbar-thumb" :style="{ left: progress + '%' }" />
      </div>

      <!-- Controls row -->
      <div class="edu-player__row">
        <button class="edu-player__btn" @click="togglePlay">
          <span class="material-symbols-outlined">{{ isPlaying ? 'pause' : 'play_arrow' }}</span>
        </button>

        <button class="edu-player__btn" @click="toggleMute">
          <span class="material-symbols-outlined">{{ isMuted || volume === 0 ? 'volume_off' : 'volume_up' }}</span>
        </button>
        <div class="edu-player__volume" @click="changeVolume">
          <div class="edu-player__volume-fill" :style="{ width: (isMuted ? 0 : volume * 100) + '%' }" />
        </div>

        <span class="edu-player__time">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>

        <span style="flex: 1;" />

        <!-- Speed -->
        <div style="position: relative;">
          <button class="edu-player__btn" @click.stop="showSpeedMenu = !showSpeedMenu">
            {{ speed }}x
          </button>
          <div v-if="showSpeedMenu" class="edu-player__speed-menu">
            <button
              v-for="s in SPEEDS"
              :key="s"
              class="edu-player__speed-option"
              :class="{ 'edu-player__speed-option--active': speed === s }"
              @click="setSpeed(s)"
            >
              {{ s }}x
            </button>
          </div>
        </div>

        <button class="edu-player__btn" @click="toggleFullscreen">
          <span class="material-symbols-outlined">{{ isFullscreen ? 'fullscreen_exit' : 'fullscreen' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.edu-player--youtube {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: #000;
  border-radius: var(--edu-radius, 12px);
  overflow: hidden;
}
.edu-player--youtube iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
