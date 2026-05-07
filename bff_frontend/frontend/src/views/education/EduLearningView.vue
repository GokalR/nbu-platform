<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BACKEND_URL } from '@/services/api'
import { formatDuration } from '@/utils/formatDuration'
import EduVideoPlayer from '@/components/education/EduVideoPlayer.vue'
import EduQuiz from '@/components/education/EduQuiz.vue'
import EduFlashcards from '@/components/education/EduFlashcards.vue'
import EduMindMap from '@/components/education/EduMindMap.vue'
import EduTest from '@/components/education/EduTest.vue'

const route = useRoute()
const router = useRouter()

const { locale } = useI18n()

const courseId = computed(() => route.params.courseId)
const videoId = computed(() => route.params.videoId)

const video = ref(null)
const content = ref(null)
const videos = ref([])
const loading = ref(true)
const activeTab = ref('quiz')

const tabs = [
  { key: 'quiz', labelKey: 'education.tabQuiz', icon: 'quiz' },
  { key: 'flashcards', labelKey: 'education.tabFlashcards', icon: 'style' },
  { key: 'mental_map', labelKey: 'education.tabMindMap', icon: 'account_tree' },
  { key: 'test', labelKey: 'education.tabTest', icon: 'assignment' },
]

const quizData = computed(() => content.value?.quiz)
const flashcardsData = computed(() => content.value?.flashcards)
const mindMapData = computed(() => content.value?.mental_map)
const testData = computed(() => content.value?.test)

const currentIndex = computed(() => videos.value.findIndex(v => v.id === videoId.value))
const nextVideo = computed(() => videos.value[currentIndex.value + 1] || null)
const prevVideo = computed(() => videos.value[currentIndex.value - 1] || null)

async function loadData() {
  loading.value = true
  try {
    const lang = locale.value
    const [videoRes, contentRes, videosRes] = await Promise.all([
      fetch(`${BACKEND_URL}/api/videos/${videoId.value}?lang=${lang}`),
      fetch(`${BACKEND_URL}/api/videos/${videoId.value}/content?lang=${lang}`),
      fetch(`${BACKEND_URL}/api/courses/${courseId.value}/videos?lang=${lang}`),
    ])
    if (videoRes.ok) video.value = await videoRes.json()
    if (contentRes.ok) content.value = await contentRes.json()
    if (videosRes.ok) videos.value = await videosRes.json()
  } catch (e) {
    console.error('Failed to load lesson data:', e)
  }
  loading.value = false
  activeTab.value = 'quiz'
}

onMounted(loadData)

// Reload data when navigating between lessons or switching language
watch(videoId, loadData)
watch(locale, loadData)

function goToVideo(vid) {
  router.push(`/education/courses/${courseId.value}/learn/${vid.id}`)
}

</script>

<template>
  <div class="learn">
    <!-- Loading skeleton -->
    <div v-if="loading" class="learn__skeleton">
      <div class="edu-skeleton" style="aspect-ratio: 16/9; border-radius: 16px;" />
      <div style="display: flex; gap: 16px; margin-top: 20px;">
        <div class="edu-skeleton" style="height: 32px; width: 300px; border-radius: 8px;" />
      </div>
    </div>

    <!-- Main content -->
    <div v-else-if="video" class="learn__grid">
      <!-- ─── Left: Video + Info + Tabs ─── -->
      <div class="learn__main">
        <!-- Video Player -->
        <div class="learn__player-wrap">
          <EduVideoPlayer
            :src="video.videoUrl"
            :title="video.title"
            :duration-sec="video.durationSec || 0"
          />
        </div>

        <!-- Video info -->
        <div class="learn__info">
          <div class="learn__info-top">
            <span class="learn__episode-badge">
              {{ $t('education.episodeOf', { current: currentIndex + 1, total: videos.length }) }}
            </span>
          </div>
          <h1 class="learn__title">{{ video.title }}</h1>
          <p v-if="video.description" class="learn__desc">{{ video.description }}</p>

          <!-- Prev / Next navigation -->
          <div class="learn__nav">
            <button
              class="learn__nav-btn"
              :disabled="!prevVideo"
              @click="prevVideo && goToVideo(prevVideo)"
            >
              <span class="material-symbols-outlined">arrow_back</span>
              {{ $t('education.previous') }}
            </button>
            <button
              class="learn__nav-btn learn__nav-btn--next"
              :disabled="!nextVideo"
              @click="nextVideo && goToVideo(nextVideo)"
            >
              {{ $t('education.next') }}
              <span class="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </div>

        <!-- Content Tabs -->
        <div v-if="content" class="learn__tabs-section">
          <div class="learn__tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="learn__tab"
              :class="{ 'learn__tab--active': activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              <span class="material-symbols-outlined learn__tab-icon">{{ tab.icon }}</span>
              <span class="learn__tab-label">{{ $t(tab.labelKey) }}</span>
            </button>
          </div>

          <div class="learn__panel">
            <EduQuiz
              v-if="activeTab === 'quiz' && quizData?.questions"
              :questions="quizData.questions"
            />
            <div v-else-if="activeTab === 'quiz'" class="learn__empty">
              <span class="material-symbols-outlined">quiz</span>
              <p>{{ $t('education.noQuiz') }}</p>
            </div>

            <EduFlashcards
              v-if="activeTab === 'flashcards' && flashcardsData?.cards"
              :cards="flashcardsData.cards"
            />
            <div v-else-if="activeTab === 'flashcards'" class="learn__empty">
              <span class="material-symbols-outlined">style</span>
              <p>{{ $t('education.noFlashcards') }}</p>
            </div>

            <EduMindMap
              v-if="activeTab === 'mental_map' && mindMapData?.root"
              :root="mindMapData.root"
            />
            <div v-else-if="activeTab === 'mental_map'" class="learn__empty">
              <span class="material-symbols-outlined">account_tree</span>
              <p>{{ $t('education.noMindMap') }}</p>
            </div>

            <EduTest
              v-if="activeTab === 'test' && testData?.questions"
              :questions="testData.questions"
            />
            <div v-else-if="activeTab === 'test'" class="learn__empty">
              <span class="material-symbols-outlined">assignment</span>
              <p>{{ $t('education.noTest') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Right: Lesson Sidebar ─── -->
      <aside class="learn__sidebar">
        <div class="learn__sidebar-header">
          <h3>{{ $t('education.courseContents') }}</h3>
          <span class="learn__sidebar-count">{{ videos.length }} {{ $t('education.lessonsCount') }}</span>
        </div>
        <div class="learn__lesson-list">
          <div
            v-for="(v, idx) in videos"
            :key="v.id"
            class="learn__lesson"
            :class="{
              'learn__lesson--active': v.id === videoId,
              'learn__lesson--done': idx < currentIndex,
            }"
            @click="goToVideo(v)"
          >
            <div class="learn__lesson-num">
              <span v-if="idx < currentIndex" class="material-symbols-outlined" style="font-size: 16px;">check</span>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div class="learn__lesson-body">
              <span class="learn__lesson-title">{{ v.title }}</span>
              <span class="learn__lesson-dur">{{ formatDuration(v.durationSec) }}</span>
            </div>
            <div v-if="v.id === videoId" class="learn__lesson-indicator" />
          </div>
        </div>
      </aside>
    </div>

    <!-- Error state -->
    <div v-else class="learn__error">
      <span class="material-symbols-outlined" style="font-size: 56px; color: var(--edu-text-muted);">error_outline</span>
      <p>{{ $t('education.videoNotFound') }}</p>
      <button class="edu-btn edu-btn--primary" @click="router.push('/education')">{{ $t('education.backToCourses') }}</button>
    </div>
  </div>
</template>

<style scoped>
.learn {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px 48px;
}

.learn__skeleton { max-width: 900px; }

/* ── Grid layout ── */
.learn__grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 28px;
  align-items: start;
}

/* ── Video area ── */
.learn__main { min-width: 0; }

.learn__player-wrap {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 20, 60, 0.12);
  background: #000;
}
.learn__player-wrap :deep(.edu-player) {
  aspect-ratio: 16/9;
  width: 100%;
}

/* ── Video info ── */
.learn__info {
  padding: 24px 0 20px;
}

.learn__info-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.learn__episode-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: var(--edu-accent-light);
  color: var(--edu-accent);
}

.learn__title {
  font-family: 'Manrope', sans-serif;
  font-size: 28px;
  font-weight: 800;
  line-height: 1.25;
  margin: 0 0 10px;
  color: var(--edu-text);
  letter-spacing: -0.02em;
}

.learn__desc {
  margin: 0;
  font-size: 16px;
  line-height: 1.6;
  color: var(--edu-text-secondary);
}

/* ── Prev / Next ── */
.learn__nav {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.learn__nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--edu-border);
  background: var(--edu-bg-card);
  color: var(--edu-text-secondary);
  transition: all 0.15s;
}
.learn__nav-btn:hover:not(:disabled) {
  border-color: var(--edu-accent);
  color: var(--edu-accent);
  background: var(--edu-accent-light);
}
.learn__nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.learn__nav-btn--next {
  background: var(--edu-accent);
  color: white;
  border-color: var(--edu-accent);
}
.learn__nav-btn--next:hover:not(:disabled) {
  background: var(--edu-accent-hover);
  color: white;
}
.learn__nav-btn .material-symbols-outlined { font-size: 20px; }

/* ── Content Tabs ── */
.learn__tabs-section {
  margin-top: 36px;
}

.learn__tabs {
  display: flex;
  gap: 6px;
  padding: 6px;
  background: var(--edu-bg);
  border-radius: 14px;
  border: 1px solid var(--edu-border);
}

.learn__tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  background: transparent;
  color: var(--edu-text-muted);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}
.learn__tab:hover {
  color: var(--edu-text);
  background: rgba(255,255,255,0.6);
}
.learn__tab--active {
  background: var(--edu-bg-card);
  color: var(--edu-accent);
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 27, 61, 0.08);
}

.learn__tab-icon { font-size: 20px; }

.learn__panel {
  margin-top: 24px;
  padding: 32px;
  background: var(--edu-bg-card);
  border: 1px solid var(--edu-border);
  border-radius: 16px;
  min-height: 320px;
  box-shadow: 0 1px 4px rgba(0, 20, 60, 0.04);
}

.learn__empty {
  text-align: center;
  padding: 56px 24px;
  color: var(--edu-text-muted);
}
.learn__empty .material-symbols-outlined {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.4;
}
.learn__empty p {
  font-size: 15px;
  margin: 0;
}

/* ── Sidebar ── */
.learn__sidebar {
  background: var(--edu-bg-card);
  border: 1px solid var(--edu-border);
  border-radius: 16px;
  overflow: hidden;
  position: sticky;
  top: 72px;
  max-height: calc(100vh - 90px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 4px rgba(0, 20, 60, 0.04);
}

.learn__sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--edu-border);
}
.learn__sidebar-header h3 {
  font-family: 'Manrope', sans-serif;
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--edu-text);
}
.learn__sidebar-count {
  font-size: 13px;
  color: var(--edu-text-muted);
  font-weight: 500;
}

.learn__lesson-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.learn__lesson {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}
.learn__lesson:hover {
  background: var(--edu-bg);
}

.learn__lesson--active {
  background: var(--edu-accent-light);
}

.learn__lesson-num {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--edu-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  color: var(--edu-text-muted);
  flex-shrink: 0;
  transition: all 0.15s;
}
.learn__lesson--active .learn__lesson-num {
  background: var(--edu-accent);
  color: white;
}
.learn__lesson--done .learn__lesson-num {
  background: #ecfdf5;
  color: var(--edu-success);
}

.learn__lesson-body {
  flex: 1;
  min-width: 0;
}
.learn__lesson-title {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--edu-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}
.learn__lesson--active .learn__lesson-title {
  color: var(--edu-accent);
  font-weight: 700;
}
.learn__lesson-dur {
  font-size: 12px;
  color: var(--edu-text-muted);
  margin-top: 2px;
  display: block;
}

.learn__lesson-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--edu-accent);
  flex-shrink: 0;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

/* ── Error state ── */
.learn__error {
  text-align: center;
  padding: 80px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.learn__error p {
  font-size: 17px;
  color: var(--edu-text-secondary);
  margin: 0;
}

/* ── Mobile ── */
@media (max-width: 1024px) {
  .learn__grid {
    grid-template-columns: 1fr;
  }
  .learn__sidebar {
    position: static;
    max-height: none;
  }
  .learn__title { font-size: 22px; }
}

@media (max-width: 600px) {
  .learn { padding: 12px 16px 32px; }
  .learn__title { font-size: 20px; }
  .learn__panel { padding: 20px 16px; }
  .learn__tab-label { display: none; }
  .learn__tab { padding: 10px; }
}
</style>
