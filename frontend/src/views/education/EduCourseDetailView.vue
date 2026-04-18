<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BACKEND_URL } from '@/services/api'
import { formatDuration } from '@/utils/formatDuration'

const route = useRoute()
const router = useRouter()

const { locale } = useI18n()
const courseId = computed(() => route.params.id)

const course = ref(null)
const videos = ref([])
const loading = ref(true)

async function loadData() {
  loading.value = true
  try {
    const [courseRes, videosRes] = await Promise.all([
      fetch(`${BACKEND_URL}/api/courses/${courseId.value}?lang=${locale.value}`),
      fetch(`${BACKEND_URL}/api/courses/${courseId.value}/videos?lang=${locale.value}`),
    ])
    if (courseRes.ok) course.value = await courseRes.json()
    if (videosRes.ok) videos.value = await videosRes.json()
  } catch (e) {
    console.error('Failed to load course data:', e)
  }
  loading.value = false
}

onMounted(loadData)
watch(locale, loadData)

function startLesson(videoId) {
  router.push(`/education/courses/${courseId.value}/learn/${videoId}`)
}

const totalMinutes = computed(() => {
  return Math.round(videos.value.reduce((sum, v) => sum + (v.durationSec || 0), 0) / 60)
})
</script>

<template>
  <div class="detail">
    <div v-if="loading" style="padding: 48px; text-align: center;">
      <div class="edu-skeleton" style="height: 260px; max-width: 800px; margin: 0 auto; border-radius: 24px;" />
    </div>

    <template v-else-if="course">
      <!-- Back -->
      <button class="detail__back" @click="router.push('/education')">
        <span class="material-symbols-outlined">arrow_back</span>
        {{ $t('education.allCourses') }}
      </button>

      <!-- Hero -->
      <div class="detail__hero">
        <div class="detail__hero-content">
          <span v-if="course.category" class="detail__category">{{ course.category }}</span>
          <h1 class="detail__title">{{ course.title }}</h1>
          <p v-if="course.description" class="detail__desc">{{ course.description }}</p>

          <div class="detail__stats">
            <div class="detail__stat">
              <span class="material-symbols-outlined">play_circle</span>
              {{ videos.length }} {{ $t('education.lessonsCount') }}
            </div>
            <div class="detail__stat">
              <span class="material-symbols-outlined">schedule</span>
              {{ totalMinutes }} {{ $t('education.min') }}
            </div>
            <div v-if="course.educatorName" class="detail__stat">
              <span class="material-symbols-outlined">person</span>
              {{ course.educatorName }}
            </div>
            <div class="detail__stat">
              <span class="material-symbols-outlined">quiz</span>
              {{ $t('education.quizzesAndTests') }}
            </div>
          </div>

          <button class="detail__start-btn" @click="videos.length && startLesson(videos[0].id)">
            <span class="material-symbols-outlined">play_arrow</span>
            {{ $t('education.startLearningBtn') }}
          </button>
        </div>
      </div>

      <!-- Lessons -->
      <div class="detail__lessons">
        <div class="detail__lessons-header">
          <h2>{{ $t('education.courseProgram') }}</h2>
          <span class="detail__lessons-count">{{ videos.length }} {{ $t('education.videoLessons') }}</span>
        </div>

        <div class="detail__lesson-grid">
          <div
            v-for="(video, idx) in videos"
            :key="video.id"
            class="detail__lesson"
            @click="startLesson(video.id)"
          >
            <div class="detail__lesson-left">
              <div class="detail__lesson-num">{{ idx + 1 }}</div>
              <div class="detail__lesson-info">
                <h4>{{ video.title }}</h4>
                <p v-if="video.description">{{ video.description }}</p>
              </div>
            </div>
            <div class="detail__lesson-right">
              <span class="detail__lesson-dur">
                <span class="material-symbols-outlined" style="font-size: 16px;">schedule</span>
                {{ formatDuration(video.durationSec) }}
              </span>
              <span class="material-symbols-outlined detail__lesson-play">play_circle</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="detail__not-found">
      <span class="material-symbols-outlined" style="font-size: 56px;">error_outline</span>
      <p>{{ $t('education.courseNotFound') }}</p>
      <button class="edu-btn edu-btn--primary" @click="router.push('/education')">{{ $t('education.backBtn') }}</button>
    </div>
  </div>
</template>

<style scoped>
.detail {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 24px 64px;
}

.detail__back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--edu-accent);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  margin-bottom: 20px;
  transition: opacity 0.15s;
}
.detail__back:hover { opacity: 0.7; }
.detail__back .material-symbols-outlined { font-size: 20px; }

/* ── Hero ── */
.detail__hero {
  padding: 44px 40px;
  background: linear-gradient(135deg, #001f3f 0%, #003d7c 50%, #0054a6 100%);
  border-radius: 24px;
  color: white;
  position: relative;
  overflow: hidden;
}
.detail__hero::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -15%;
  width: 50%;
  height: 180%;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.detail__hero-content { position: relative; z-index: 1; }

.detail__category {
  display: inline-block;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  margin-bottom: 16px;
  letter-spacing: 0.3px;
}

.detail__title {
  font-family: 'Manrope', sans-serif;
  font-size: 34px;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 14px;
  letter-spacing: -0.02em;
}

.detail__desc {
  font-size: 17px;
  line-height: 1.6;
  opacity: 0.8;
  margin: 0 0 24px;
  max-width: 600px;
}

.detail__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 28px;
}
.detail__stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  opacity: 0.85;
}
.detail__stat .material-symbols-outlined { font-size: 20px; }

.detail__start-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  background: white;
  color: var(--edu-accent);
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.detail__start-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}
.detail__start-btn .material-symbols-outlined { font-size: 22px; }

/* ── Lessons ── */
.detail__lessons { margin-top: 40px; }

.detail__lessons-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 20px;
}
.detail__lessons-header h2 {
  font-family: 'Manrope', sans-serif;
  font-size: 24px;
  font-weight: 800;
  margin: 0;
  color: var(--edu-text);
  letter-spacing: -0.01em;
}
.detail__lessons-count {
  font-size: 14px;
  color: var(--edu-text-muted);
  font-weight: 500;
}

.detail__lesson-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail__lesson {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  background: var(--edu-bg-card);
  border: 1px solid var(--edu-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.detail__lesson:hover {
  border-color: rgba(0, 61, 124, 0.25);
  box-shadow: 0 4px 16px rgba(0, 27, 61, 0.08);
  transform: translateX(4px);
}

.detail__lesson-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.detail__lesson-num {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--edu-accent-light);
  color: var(--edu-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 15px;
  flex-shrink: 0;
}

.detail__lesson-info { min-width: 0; }
.detail__lesson-info h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--edu-text);
  line-height: 1.3;
}
.detail__lesson-info p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--edu-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail__lesson-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}
.detail__lesson-dur {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--edu-text-muted);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
.detail__lesson-play {
  font-size: 32px;
  color: var(--edu-accent);
  opacity: 0;
  transition: opacity 0.15s;
}
.detail__lesson:hover .detail__lesson-play { opacity: 1; }

.detail__not-found {
  text-align: center;
  padding: 80px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--edu-text-secondary);
}
.detail__not-found p { font-size: 17px; margin: 0; }

@media (max-width: 768px) {
  .detail__hero { padding: 32px 24px; }
  .detail__title { font-size: 24px; }
  .detail__lesson-info p { display: none; }
  .detail__lesson-play { display: none; }
}
</style>
