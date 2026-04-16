<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'

const { t } = useI18n()
const activeTrack = ref('all')

const tracks = computed(() => [
  { key: 'all', label: t('education.trackAll') },
  { key: 'finance', label: t('education.trackFinance') },
  { key: 'business', label: t('education.trackBusiness') },
  { key: 'digital', label: t('education.trackDigital') },
  { key: 'ai', label: t('education.trackAi') },
])

const stats = computed(() => [
  { icon: 'menu_book', label: t('education.statCourses'), value: '48', tone: 'blue' },
  { icon: 'groups', label: t('education.statStudents'), value: '12 400', tone: 'green' },
  { icon: 'workspace_premium', label: t('education.statCertificates'), value: '3 250', tone: 'amber' },
  { icon: 'school', label: t('education.statInstructors'), value: '26', tone: 'purple' },
])

const courses = computed(() => [
  {
    track: 'finance',
    title: t('education.courseCorpFinance'),
    level: t('education.levelBeginner'),
    duration: t('education.duration', { n: 6 }),
    lessons: 24,
    students: 1840,
    rating: 4.8,
    progress: 0,
    color: '#0054A6',
    emoji: '💼',
    tag: t('education.tagPopular'),
    tagTone: 'blue',
  },
  {
    track: 'finance',
    title: t('education.courseSmbAnalysis'),
    level: t('education.levelIntermediate'),
    duration: t('education.duration', { n: 8 }),
    lessons: 32,
    students: 920,
    rating: 4.7,
    progress: 35,
    color: '#00A651',
    emoji: '📊',
    tag: t('education.tagInProgress'),
    tagTone: 'green',
  },
  {
    track: 'business',
    title: t('education.courseStartup'),
    level: t('education.levelBeginner'),
    duration: t('education.duration', { n: 4 }),
    lessons: 18,
    students: 2750,
    rating: 4.9,
    progress: 0,
    color: '#F59E0B',
    emoji: '🚀',
    tag: t('education.tagNew'),
    tagTone: 'amber',
  },
  {
    track: 'ai',
    title: t('education.courseAiBusiness'),
    level: t('education.levelIntermediate'),
    duration: t('education.duration', { n: 10 }),
    lessons: 40,
    students: 680,
    rating: 4.9,
    progress: 72,
    color: '#8B5CF6',
    emoji: '🤖',
    tag: t('education.tagInProgress'),
    tagTone: 'purple',
  },
  {
    track: 'digital',
    title: t('education.courseDigMarketing'),
    level: t('education.levelBeginner'),
    duration: t('education.duration', { n: 5 }),
    lessons: 22,
    students: 3120,
    rating: 4.6,
    progress: 100,
    color: '#E0384B',
    emoji: '📣',
    tag: t('education.tagCompleted'),
    tagTone: 'green',
  },
  {
    track: 'digital',
    title: t('education.courseExcel'),
    level: t('education.levelBeginner'),
    duration: t('education.duration', { n: 3 }),
    lessons: 14,
    students: 4200,
    rating: 4.7,
    progress: 0,
    color: '#0891B2',
    emoji: '📈',
    tag: t('education.tagBestseller'),
    tagTone: 'teal',
  },
  {
    track: 'business',
    title: t('education.courseProjectMgmt'),
    level: t('education.levelIntermediate'),
    duration: t('education.duration', { n: 7 }),
    lessons: 28,
    students: 1540,
    rating: 4.8,
    progress: 15,
    color: '#0054A6',
    emoji: '🗂',
    tag: t('education.tagInProgress'),
    tagTone: 'blue',
  },
  {
    track: 'ai',
    title: t('education.courseMlFinance'),
    level: t('education.levelAdvanced'),
    duration: t('education.duration', { n: 12 }),
    lessons: 48,
    students: 420,
    rating: 5.0,
    progress: 0,
    color: '#8B5CF6',
    emoji: '🧠',
    tag: t('education.tagPro'),
    tagTone: 'purple',
  },
])

const filteredCourses = computed(() => {
  if (activeTrack.value === 'all') return courses.value
  return courses.value.filter((c) => c.track === activeTrack.value)
})

const learningPath = computed(() => [
  { step: 1, title: t('education.pathFinLiteracy'), status: 'done', sub: t('education.pathFinLiteracySub') },
  { step: 2, title: t('education.pathReporting'), status: 'done', sub: t('education.pathReportingSub') },
  { step: 3, title: t('education.pathBizPlan'), status: 'active', sub: t('education.pathBizPlanSub') },
  { step: 4, title: t('education.pathInvest'), status: 'pending', sub: t('education.pathInvestSub') },
  { step: 5, title: t('education.pathStrategy'), status: 'pending', sub: t('education.pathStrategySub') },
])

const upcoming = computed(() => [
  { date: t('education.event1Date'), time: '14:00', title: t('education.event1Title'), speaker: t('education.event1Speaker'), tone: 'purple' },
  { date: t('education.event2Date'), time: '10:00', title: t('education.event2Title'), speaker: t('education.event2Speaker'), tone: 'blue' },
  { date: t('education.event3Date'), time: '16:00', title: t('education.event3Title'), speaker: t('education.event3Speaker'), tone: 'green' },
])
</script>

<template>
  <div class="edu-root">
    <!-- Hero -->
    <section class="edu-hero">
      <div class="edu-hero-text">
        <div class="edu-eyebrow">{{ $t('education.eyebrow') }}</div>
        <h1 class="edu-title">
          NBU
          <span class="edu-title-grad">Education</span>
        </h1>
        <p class="edu-subtitle">
          {{ $t('education.subtitle') }}
        </p>
        <div class="edu-hero-actions">
          <button class="edu-btn edu-btn-primary">
            <AppIcon name="play_arrow" />
            <span>{{ $t('education.startLearning') }}</span>
          </button>
          <button class="edu-btn edu-btn-ghost">
            <AppIcon name="explore" />
            <span>{{ $t('education.courseCatalog') }}</span>
          </button>
        </div>
      </div>
      <div class="edu-hero-card">
        <div class="edu-hero-card-top">
          <span class="edu-hero-pill">{{ $t('education.monthProgram') }}</span>
          <AppIcon name="auto_awesome" />
        </div>
        <div class="edu-hero-card-title">{{ $t('education.heroCardTitle') }}</div>
        <div class="edu-hero-card-sub">{{ $t('education.heroCardSub') }}</div>
        <div class="edu-hero-card-progress">
          <div class="edu-progress-bar"><span style="width:72%"></span></div>
          <div class="edu-progress-label">{{ $t('education.heroProgress') }}</div>
        </div>
        <div class="edu-hero-card-bottom">
          <div class="edu-avatars">
            <span class="edu-avatar" style="background:#0054A6">АР</span>
            <span class="edu-avatar" style="background:#00A651">ДХ</span>
            <span class="edu-avatar" style="background:#F59E0B">БЮ</span>
            <span class="edu-avatar edu-avatar-more">+12</span>
          </div>
          <button class="edu-btn edu-btn-primary edu-btn-sm">{{ $t('education.continue') }}</button>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <section class="edu-stats">
      <div v-for="s in stats" :key="s.label" class="edu-stat" :class="`tone-${s.tone}`">
        <div class="edu-stat-icon"><AppIcon :name="s.icon" /></div>
        <div>
          <div class="edu-stat-value">{{ s.value }}</div>
          <div class="edu-stat-label">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- Tracks -->
    <section class="edu-tracks">
      <div class="edu-section-title">
        <h2>{{ $t('education.directions') }}</h2>
        <span class="edu-muted">{{ $t('education.coursesCount', { n: filteredCourses.length }) }}</span>
      </div>
      <div class="edu-pills">
        <button
          v-for="tr in tracks"
          :key="tr.key"
          class="edu-pill"
          :class="{ 'is-active': activeTrack === tr.key }"
          @click="activeTrack = tr.key"
        >
          {{ tr.label }}
        </button>
      </div>
    </section>

    <!-- Courses grid -->
    <section class="edu-courses">
      <article
        v-for="c in filteredCourses"
        :key="c.title"
        class="edu-course"
      >
        <div class="edu-course-head" :style="{ background: `linear-gradient(135deg, ${c.color}22, ${c.color}08)` }">
          <div class="edu-course-emoji" :style="{ background: c.color }">{{ c.emoji }}</div>
          <span class="edu-badge" :class="`tone-${c.tagTone}`">{{ c.tag }}</span>
        </div>
        <div class="edu-course-body">
          <div class="edu-course-meta">{{ c.level }} · {{ c.duration }}</div>
          <h3 class="edu-course-title">{{ c.title }}</h3>
          <div class="edu-course-info">
            <span><AppIcon name="menu_book" /> {{ $t('education.lessons', { n: c.lessons }) }}</span>
            <span><AppIcon name="groups" /> {{ c.students.toLocaleString() }}</span>
            <span><AppIcon name="star" /> {{ c.rating }}</span>
          </div>
          <div v-if="c.progress > 0" class="edu-course-progress">
            <div class="edu-progress-bar"><span :style="{ width: c.progress + '%', background: c.color }"></span></div>
            <div class="edu-progress-label">{{ c.progress }}% {{ $t('education.completed') }}</div>
          </div>
          <button class="edu-btn edu-btn-outline edu-btn-block">
            {{ c.progress > 0 && c.progress < 100 ? $t('education.btnContinue') : c.progress === 100 ? $t('education.btnCertificate') : $t('education.btnEnroll') }}
          </button>
        </div>
      </article>
    </section>

    <!-- Learning path + Upcoming -->
    <section class="edu-split">
      <div class="edu-card">
        <div class="edu-section-title">
          <h2>{{ $t('education.myTrack') }}</h2>
          <span class="edu-muted">{{ $t('education.financialAnalyst') }}</span>
        </div>
        <ol class="edu-path">
          <li
            v-for="p in learningPath"
            :key="p.step"
            class="edu-path-item"
            :class="`status-${p.status}`"
          >
            <div class="edu-path-dot">
              <AppIcon v-if="p.status === 'done'" name="check" />
              <span v-else>{{ p.step }}</span>
            </div>
            <div class="edu-path-body">
              <div class="edu-path-title">{{ p.title }}</div>
              <div class="edu-path-sub">{{ p.sub }}</div>
            </div>
            <span v-if="p.status === 'active'" class="edu-badge tone-blue">{{ $t('education.now') }}</span>
          </li>
        </ol>
      </div>

      <div class="edu-card">
        <div class="edu-section-title">
          <h2>{{ $t('education.upcomingEvents') }}</h2>
          <a href="#" class="edu-link">{{ $t('education.allEvents') }}</a>
        </div>
        <ul class="edu-events">
          <li v-for="e in upcoming" :key="e.title" class="edu-event" :class="`tone-${e.tone}`">
            <div class="edu-event-date">
              <div class="edu-event-day">{{ e.date }}</div>
              <div class="edu-event-time">{{ e.time }}</div>
            </div>
            <div class="edu-event-body">
              <div class="edu-event-title">{{ e.title }}</div>
              <div class="edu-event-speaker">
                <AppIcon name="person" /> {{ e.speaker }}
              </div>
            </div>
            <AppIcon name="chevron_right" class="edu-event-chev" />
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<style scoped>
.edu-root {
  padding: 24px 28px 48px;
  color: #1E293B;
  max-width: 1400px;
  margin: 0 auto;
}

.edu-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6B7A99;
  margin-bottom: 8px;
}

.edu-hero {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.edu-hero-text { align-self: center; }
.edu-title {
  font-size: 44px;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #0F172A;
  margin: 0 0 12px;
}
.edu-title-grad {
  background: linear-gradient(90deg, #003D7C, #0054A6 45%, #00A651);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.edu-subtitle {
  font-size: 15px;
  line-height: 1.55;
  color: #475569;
  max-width: 520px;
  margin: 0 0 20px;
}
.edu-hero-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.edu-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all .15s ease;
}
.edu-btn-sm { padding: 7px 14px; font-size: 13px; }
.edu-btn-block { width: 100%; justify-content: center; margin-top: 4px; }
.edu-btn-primary { background: #0054A6; color: #fff; }
.edu-btn-primary:hover { background: #003D7C; transform: translateY(-1px); }
.edu-btn-ghost { background: #fff; color: #0F172A; border-color: #E2E8F0; }
.edu-btn-ghost:hover { border-color: #0054A6; color: #0054A6; }
.edu-btn-outline { background: #F8FAFC; color: #0F172A; border-color: #E2E8F0; }
.edu-btn-outline:hover { border-color: #0054A6; color: #0054A6; background: #fff; }

.edu-hero-card {
  background: linear-gradient(145deg, #0B1E3F 0%, #0054A6 100%);
  color: #fff;
  border-radius: 18px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 12px 40px rgba(0, 84, 166, 0.25);
  position: relative;
  overflow: hidden;
}
.edu-hero-card::after {
  content: '';
  position: absolute;
  top: -30%; right: -20%;
  width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(0,166,81,.3), transparent 60%);
  pointer-events: none;
}
.edu-hero-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}
.edu-hero-pill {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  background: rgba(255,255,255,.14);
  padding: 5px 10px;
  border-radius: 999px;
}
.edu-hero-card-title { font-size: 22px; font-weight: 800; line-height: 1.2; position: relative; z-index: 1; }
.edu-hero-card-sub { font-size: 13px; opacity: .8; position: relative; z-index: 1; }
.edu-hero-card-progress { position: relative; z-index: 1; }
.edu-hero-card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  position: relative;
  z-index: 1;
}

.edu-progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255,255,255,.15);
  border-radius: 999px;
  overflow: hidden;
}
.edu-course .edu-progress-bar { background: #F1F5F9; }
.edu-progress-bar span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #00A651, #22D37F);
  border-radius: 999px;
  transition: width .3s ease;
}
.edu-progress-label { font-size: 11px; opacity: .85; margin-top: 6px; }
.edu-course .edu-progress-label { color: #64748B; opacity: 1; }

.edu-avatars { display: flex; }
.edu-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  border: 2px solid #0B1E3F;
  margin-left: -8px;
}
.edu-avatar:first-child { margin-left: 0; }
.edu-avatar-more { background: rgba(255,255,255,.18); }

.edu-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 28px;
}
.edu-stat {
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 16px;
  display: flex;
  gap: 14px;
  align-items: center;
  transition: all .15s ease;
}
.edu-stat:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(15,23,42,.06); }
.edu-stat-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}
.edu-stat.tone-blue   .edu-stat-icon { background: #EEF4FF; color: #0054A6; }
.edu-stat.tone-green  .edu-stat-icon { background: #E6F7EE; color: #00A651; }
.edu-stat.tone-amber  .edu-stat-icon { background: #FEF3C7; color: #F59E0B; }
.edu-stat.tone-purple .edu-stat-icon { background: #F3E8FF; color: #8B5CF6; }
.edu-stat-value { font-size: 22px; font-weight: 800; color: #0F172A; }
.edu-stat-label { font-size: 12px; color: #64748B; }

.edu-section-title {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 14px;
}
.edu-section-title h2 { font-size: 18px; font-weight: 800; color: #0F172A; margin: 0; }
.edu-muted { font-size: 12px; color: #64748B; }
.edu-link { font-size: 13px; font-weight: 600; color: #0054A6; text-decoration: none; }
.edu-link:hover { text-decoration: underline; }

.edu-tracks { margin-bottom: 16px; }
.edu-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-bottom: 4px;
}
.edu-pill {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #E2E8F0;
  background: #fff;
  color: #64748B;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all .15s ease;
}
.edu-pill:hover { border-color: #0054A6; color: #0054A6; }
.edu-pill.is-active {
  background: #0054A6;
  color: #fff;
  border-color: #0054A6;
}

.edu-courses {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}
.edu-course {
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all .18s ease;
}
.edu-course:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(15,23,42,.08); border-color: #CBD5E1; }
.edu-course-head {
  padding: 22px 18px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.edu-course-emoji {
  width: 54px; height: 54px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 8px 20px rgba(0,0,0,.1);
}
.edu-course-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.edu-course-meta {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #64748B;
}
.edu-course-title {
  font-size: 15px;
  font-weight: 700;
  color: #0F172A;
  line-height: 1.35;
  margin: 0;
  min-height: 42px;
}
.edu-course-info {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #64748B;
  flex-wrap: wrap;
}
.edu-course-info span { display: inline-flex; align-items: center; gap: 4px; }
.edu-course-info .material-symbols-outlined { font-size: 14px; }
.edu-course-progress { margin-top: 2px; }

.edu-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
  padding: 4px 9px;
  border-radius: 999px;
}
.edu-badge.tone-blue   { background: #EEF4FF; color: #0054A6; }
.edu-badge.tone-green  { background: #E6F7EE; color: #00A651; }
.edu-badge.tone-amber  { background: #FEF3C7; color: #B45309; }
.edu-badge.tone-purple { background: #F3E8FF; color: #7C3AED; }
.edu-badge.tone-teal   { background: #CCFBF1; color: #0F766E; }
.edu-badge.tone-red    { background: #FEE2E5; color: #B91C1C; }

.edu-split {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}
.edu-card {
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 22px;
}

.edu-path { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.edu-path-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 4px;
  position: relative;
}
.edu-path-item + .edu-path-item::before {
  content: '';
  position: absolute;
  top: -14px;
  left: 17px;
  width: 2px;
  height: 24px;
  background: #E2E8F0;
}
.edu-path-item.status-done + .edu-path-item::before,
.edu-path-item.status-active + .edu-path-item::before { background: #00A651; }
.edu-path-dot {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  flex-shrink: 0;
  border: 2px solid #E2E8F0;
  background: #fff;
  color: #94A3B8;
}
.edu-path-item.status-done .edu-path-dot { background: #00A651; color: #fff; border-color: #00A651; }
.edu-path-item.status-active .edu-path-dot { background: #0054A6; color: #fff; border-color: #0054A6; box-shadow: 0 0 0 4px rgba(0,84,166,.15); }
.edu-path-body { flex: 1; }
.edu-path-title { font-size: 14px; font-weight: 700; color: #0F172A; }
.edu-path-sub { font-size: 12px; color: #64748B; margin-top: 2px; }

.edu-events { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.edu-event {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #F8FAFC;
  border-left: 3px solid #E2E8F0;
  transition: all .15s ease;
  cursor: pointer;
}
.edu-event:hover { background: #fff; border-left-color: #0054A6; box-shadow: 0 4px 14px rgba(15,23,42,.05); }
.edu-event.tone-blue   { border-left-color: #0054A6; }
.edu-event.tone-green  { border-left-color: #00A651; }
.edu-event.tone-purple { border-left-color: #8B5CF6; }
.edu-event-date {
  text-align: center;
  min-width: 52px;
  padding: 6px 8px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
}
.edu-event-day { font-size: 12px; font-weight: 700; color: #0F172A; }
.edu-event-time { font-size: 10px; color: #64748B; margin-top: 2px; }
.edu-event-body { flex: 1; }
.edu-event-title { font-size: 14px; font-weight: 700; color: #0F172A; }
.edu-event-speaker {
  font-size: 12px;
  color: #64748B;
  margin-top: 3px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.edu-event-chev { color: #94A3B8; }

@media (max-width: 960px) {
  .edu-hero,
  .edu-split { grid-template-columns: 1fr; }
  .edu-stats { grid-template-columns: repeat(2, 1fr); }
  .edu-title { font-size: 32px; }
}
</style>
