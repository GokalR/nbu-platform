<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BACKEND_URL } from '@/services/api'
import { useEduAuthStore } from '@/stores/eduAuth'

const router = useRouter()

const { t } = useI18n()
const auth = useEduAuthStore()
const dashboard = ref(null)
const loading = ref(true)

onMounted(async () => {
  if (!auth.token) { router.push('/education/login'); return }
  try {
    const res = await fetch(`${BACKEND_URL}/api/me/dashboard`, {
      headers: { Authorization: `Bearer ${auth.token}` },
    })
    if (res.ok) dashboard.value = await res.json()
  } catch (e) {
    console.error('Failed to load dashboard:', e)
  }
  loading.value = false
})

function relativeTime(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return t('education.dash.justNow')
  if (mins < 60) return t('education.dash.minsAgo', { n: mins })
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return t('education.dash.hrsAgo', { n: hrs })
  const days = Math.floor(hrs / 24)
  return t('education.dash.daysAgo', { n: days })
}

function scoreColor(pct) {
  if (pct >= 70) return 'var(--edu-success)'
  if (pct >= 50) return 'var(--edu-warning)'
  return 'var(--edu-error)'
}
</script>

<template>
  <div class="edu-dash">
    <h1>{{ t('education.dash.myProgress') }}</h1>

    <div v-if="loading" style="display: flex; gap: 20px; flex-wrap: wrap;">
      <div v-for="i in 2" :key="i" class="edu-skeleton" style="height: 180px; flex: 1; min-width: 280px;" />
    </div>

    <template v-else-if="dashboard">
      <!-- Enrolled courses -->
      <section class="edu-dash__section">
        <h2>{{ t('education.dash.myCourses') }}</h2>
        <div v-if="!dashboard.enrolledCourses?.length" class="edu-card" style="padding: 32px; text-align: center; color: var(--edu-text-muted);">
          <span class="material-symbols-outlined" style="font-size: 40px;">school</span>
          <p style="margin: 12px 0 16px;">{{ t('education.dash.noEnrollments') }}</p>
          <button class="edu-btn edu-btn--primary" @click="router.push('/education')">{{ t('education.dash.findCourses') }}</button>
        </div>
        <div v-else class="edu-dash__courses">
          <div v-for="c in dashboard.enrolledCourses" :key="c.courseId" class="edu-card edu-dash__course" @click="router.push(`/education/courses/${c.courseId}`)">
            <div class="edu-dash__course-thumb">
              <img v-if="c.thumbnailUrl" :src="c.thumbnailUrl" :alt="c.title" />
            </div>
            <div class="edu-dash__course-info">
              <h4>{{ c.title }}</h4>
              <p>{{ c.educatorName }}</p>
              <div class="edu-progress-bar" style="margin-top: 8px;">
                <div class="edu-progress-bar__fill" :style="{ width: c.progressPercent + '%', background: 'var(--edu-accent)' }" />
              </div>
              <span style="font-size: 12px; color: var(--edu-text-muted); margin-top: 4px;">
                {{ t('education.dash.lessonsProgress', { done: c.completedVideos, total: c.totalVideos, pct: c.progressPercent }) }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent scores -->
      <section v-if="dashboard.recentScores?.length" class="edu-dash__section">
        <h2>{{ t('education.dash.recentScores') }}</h2>
        <div class="edu-card" style="overflow: hidden;">
          <div
            v-for="s in dashboard.recentScores"
            :key="s.id"
            style="display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--edu-border);"
          >
            <span
              class="edu-badge"
              :style="{ background: s.type === 'quiz' ? '#eceef0' : 'var(--edu-accent-light)', color: s.type === 'quiz' ? 'var(--edu-text-secondary)' : 'var(--edu-accent)' }"
            >
              {{ s.type === 'quiz' ? t('education.dash.quiz') : t('education.dash.test') }}
            </span>
            <span style="flex: 1; font-size: 14px; color: var(--edu-text);">
              {{ s.scorePercent != null ? s.scorePercent + '%' : '—' }}
            </span>
            <span v-if="s.type === 'test'" class="edu-badge" :style="{ background: s.passed ? 'rgba(5,150,105,0.1)' : 'rgba(220,38,38,0.1)', color: s.passed ? 'var(--edu-success)' : 'var(--edu-error)' }">
              {{ s.passed ? t('education.dash.passed') : t('education.dash.notPassed') }}
            </span>
            <span style="font-size: 12px; color: var(--edu-text-muted);">{{ relativeTime(s.createdAt) }}</span>
          </div>
        </div>
      </section>
    </template>

    <div v-else style="text-align: center; padding: 48px; color: var(--edu-text-muted);">
      {{ t('education.dash.loadError') }}
    </div>
  </div>
</template>

<style scoped>
.edu-dash { max-width: 900px; margin: 0 auto; padding: 24px; }
.edu-dash h1 { font-family: 'Manrope', sans-serif; font-size: 24px; font-weight: 700; margin: 0 0 24px; color: var(--edu-text); }
.edu-dash__section { margin-bottom: 32px; }
.edu-dash__section h2 { font-family: 'Manrope', sans-serif; font-size: 18px; font-weight: 600; margin: 0 0 16px; color: var(--edu-text); }

.edu-dash__courses { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.edu-dash__course { display: flex; gap: 16px; padding: 16px; cursor: pointer; }
.edu-dash__course-thumb { width: 100px; height: 70px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #eceef0; }
.edu-dash__course-thumb img { width: 100%; height: 100%; object-fit: cover; }
.edu-dash__course-info { flex: 1; display: flex; flex-direction: column; }
.edu-dash__course-info h4 { margin: 0; font-size: 14px; font-weight: 600; color: var(--edu-text); }
.edu-dash__course-info p { margin: 4px 0 0; font-size: 12px; color: var(--edu-text-muted); }
</style>
