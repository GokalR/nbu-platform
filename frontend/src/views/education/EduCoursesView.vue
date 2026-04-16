<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t, locale } = useI18n()
const courses = ref([])
const loading = ref(true)
const error = ref(null)

async function loadCourses() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`/api/courses?lang=${locale.value}`)
    if (res.ok) {
      const data = await res.json()
      courses.value = Array.isArray(data) ? data : data.courses || []
    } else {
      error.value = t('education.loadError')
    }
  } catch {
    error.value = t('education.backendUnavailable')
  } finally {
    loading.value = false
  }
}

onMounted(loadCourses)
watch(locale, loadCourses)

function goToCourse(id) {
  router.push(`/education/courses/${id}`)
}

function totalDuration(videoCount) {
  const hours = Math.round(videoCount * 15 / 60)
  return hours > 0
    ? `${t('education.approx')}${hours} ${t('education.hours')}`
    : `${t('education.approx')}${videoCount * 15} ${t('education.min')}`
}
</script>

<template>
  <div class="catalog">
    <!-- Hero -->
    <div class="catalog__hero">
      <div class="catalog__hero-content">
        <div class="catalog__hero-badge">NBU Education</div>
        <h1 class="catalog__hero-title" v-html="$t('education.heroTitle').replace('\n', '<br>')" />
        <p class="catalog__hero-subtitle">{{ $t('education.heroSubtitle') }}</p>
        <div class="catalog__hero-stats">
          <div class="catalog__stat">
            <span class="catalog__stat-num">{{ courses.reduce((s, c) => s + (c.videoCount || 0), 0) }}</span>
            <span class="catalog__stat-label">{{ $t('education.statLessons') }}</span>
          </div>
          <div class="catalog__stat-divider" />
          <div class="catalog__stat">
            <span class="catalog__stat-num">{{ courses.length }}</span>
            <span class="catalog__stat-label">{{ $t('education.statCourses') }}</span>
          </div>
          <div class="catalog__stat-divider" />
          <div class="catalog__stat">
            <span class="catalog__stat-num">4</span>
            <span class="catalog__stat-label">{{ $t('education.statTaskTypes') }}</span>
          </div>
        </div>
      </div>
      <div class="catalog__hero-visual">
        <div class="catalog__hero-icon">
          <span class="material-symbols-outlined">school</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="catalog__grid">
      <div v-for="i in 2" :key="i" class="edu-skeleton" style="height: 320px; border-radius: 20px;" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="catalog__empty">
      <span class="material-symbols-outlined" style="font-size: 56px; color: var(--edu-warning);">cloud_off</span>
      <p>{{ error }}</p>
    </div>

    <!-- Course grid -->
    <div v-else-if="courses.length" class="catalog__grid">
      <div
        v-for="course in courses"
        :key="course.id"
        class="catalog__card"
        @click="goToCourse(course.id)"
      >
        <div class="catalog__card-visual">
          <img v-if="course.thumbnailUrl" :src="course.thumbnailUrl" :alt="course.title" />
          <div v-else class="catalog__card-placeholder">
            <span class="material-symbols-outlined">play_circle</span>
          </div>
          <div class="catalog__card-overlay">
            <span class="catalog__card-category">{{ course.category }}</span>
          </div>
        </div>
        <div class="catalog__card-body">
          <h2 class="catalog__card-title">{{ course.title }}</h2>
          <p class="catalog__card-desc">{{ course.description }}</p>
          <div class="catalog__card-meta">
            <div class="catalog__card-info">
              <span class="material-symbols-outlined">play_circle</span>
              {{ course.videoCount }} {{ $t('education.lessonsCount') }}
            </div>
            <div class="catalog__card-info">
              <span class="material-symbols-outlined">schedule</span>
              {{ totalDuration(course.videoCount) }}
            </div>
            <div class="catalog__card-info">
              <span class="material-symbols-outlined">person</span>
              {{ course.educatorName }}
            </div>
          </div>
          <button class="catalog__card-btn">
            {{ $t('education.goToCourse') }}
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="catalog__empty">
      <span class="material-symbols-outlined" style="font-size: 56px; color: var(--edu-text-muted);">school</span>
      <p>{{ $t('education.noCoursesYet') }}</p>
    </div>
  </div>
</template>

<style scoped>
.catalog {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

/* ── Hero ── */
.catalog__hero {
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 48px;
  background: linear-gradient(135deg, #001f3f 0%, #003d7c 50%, #0054a6 100%);
  border-radius: 24px;
  color: white;
  margin-bottom: 40px;
  position: relative;
  overflow: hidden;
}
.catalog__hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 60%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
  pointer-events: none;
}
.catalog__hero-content { flex: 1; position: relative; z-index: 1; }
.catalog__hero-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}
.catalog__hero-title {
  font-family: 'Manrope', sans-serif;
  font-size: 40px;
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 16px;
  letter-spacing: -0.03em;
}
.catalog__hero-subtitle {
  font-size: 17px;
  line-height: 1.6;
  opacity: 0.8;
  margin: 0 0 28px;
  max-width: 520px;
}
.catalog__hero-stats { display: flex; align-items: center; gap: 24px; }
.catalog__stat { text-align: center; }
.catalog__stat-num {
  display: block;
  font-family: 'Manrope', sans-serif;
  font-size: 28px;
  font-weight: 800;
}
.catalog__stat-label { font-size: 13px; opacity: 0.7; margin-top: 2px; display: block; }
.catalog__stat-divider { width: 1px; height: 40px; background: rgba(255,255,255,0.2); }
.catalog__hero-visual { flex-shrink: 0; position: relative; z-index: 1; }
.catalog__hero-icon {
  width: 140px;
  height: 140px;
  border-radius: 32px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255,255,255,0.15);
}
.catalog__hero-icon .material-symbols-outlined { font-size: 72px; opacity: 0.9; }

/* ── Grid ── */
.catalog__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 24px;
}

/* ── Card ── */
.catalog__card {
  background: var(--edu-bg-card);
  border: 1px solid var(--edu-border);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s;
  display: flex;
  flex-direction: column;
}
.catalog__card:hover {
  box-shadow: 0 12px 40px rgba(0, 27, 61, 0.12);
  transform: translateY(-4px);
  border-color: rgba(0, 61, 124, 0.2);
}
.catalog__card-visual {
  position: relative;
  aspect-ratio: 2.2/1;
  background: linear-gradient(135deg, #e8edf5, #f0f4fa);
  overflow: hidden;
}
.catalog__card-visual img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}
.catalog__card:hover .catalog__card-visual img { transform: scale(1.05); }
.catalog__card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #001f3f, #003d7c);
}
.catalog__card-placeholder .material-symbols-outlined { font-size: 64px; color: rgba(255,255,255,0.3); }
.catalog__card-overlay { position: absolute; top: 16px; left: 16px; }
.catalog__card-category {
  padding: 5px 14px;
  border-radius: 20px;
  background: rgba(0, 61, 124, 0.9);
  color: white;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}
.catalog__card-body {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.catalog__card-title {
  font-family: 'Manrope', sans-serif;
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 10px;
  color: var(--edu-text);
  line-height: 1.3;
}
.catalog__card-desc {
  font-size: 15px;
  line-height: 1.6;
  color: var(--edu-text-secondary);
  margin: 0 0 20px;
  flex: 1;
}
.catalog__card-meta { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 20px; }
.catalog__card-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--edu-text-muted);
  font-weight: 500;
}
.catalog__card-info .material-symbols-outlined { font-size: 18px; }
.catalog__card-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  background: var(--edu-accent);
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
  width: fit-content;
}
.catalog__card-btn:hover { background: var(--edu-accent-hover); }
.catalog__card-btn .material-symbols-outlined { font-size: 20px; }

.catalog__empty { text-align: center; padding: 80px 24px; color: var(--edu-text-secondary); }
.catalog__empty p { margin-top: 12px; font-size: 16px; }

@media (max-width: 768px) {
  .catalog__hero { flex-direction: column; padding: 32px 24px; text-align: center; }
  .catalog__hero-title { font-size: 28px; }
  .catalog__hero-subtitle { max-width: none; }
  .catalog__hero-stats { justify-content: center; }
  .catalog__hero-visual { display: none; }
  .catalog__grid { grid-template-columns: 1fr; }
}
</style>
