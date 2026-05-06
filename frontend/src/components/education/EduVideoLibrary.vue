<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import EduVideoPlayer from '@/components/education/EduVideoPlayer.vue'

const { t, locale } = useI18n()

// category: ai_courses | banking | governance | entrepreneurs
// level:    beginner | intermediate | advanced
const VIDEOS = [
  // ── AI courses ──
  { id: 'XtizkYKT280', category: 'ai_courses', level: 'beginner',     title_uz: "Sun'iy intellekt nima? To'liq obzor",                     title_ru: 'Что такое искусственный интеллект? Полный обзор' },
  { id: 'N25wGvmun6g', category: 'ai_courses', level: 'beginner',     title_uz: "Sun'iy intellekt qanday yaratiladi?",                     title_ru: 'Как создаётся искусственный интеллект?' },
  { id: 'vlozVjE-IvE', category: 'ai_courses', level: 'intermediate', title_uz: "Sun'iy intellekt va dasturlashning kelajagi",              title_ru: 'Будущее ИИ и программирования' },
  { id: 'Nt5ee-3fyAc', category: 'ai_courses', level: 'beginner',     title_uz: "ChatGPT — sun'iy aql kelajakka eshik ochdi",                title_ru: 'ChatGPT — ИИ открывает дверь в будущее' },
  { id: '1hNxd2ldlRY', category: 'ai_courses', level: 'intermediate', title_uz: 'Machine Learning nima? Data Science kursi',                title_ru: 'Что такое Machine Learning? Курс Data Science' },
  { id: 'CHU6uI9ajBw', category: 'ai_courses', level: 'beginner',     title_uz: 'Machine Learning nima?',                                    title_ru: 'Что такое Machine Learning?' },
  { id: 'voImIdBNP9o', category: 'ai_courses', level: 'intermediate', title_uz: "ChatGPT eng yaxshi prompt — 1-qism",                       title_ru: 'ChatGPT — лучший промпт (часть 1)' },
  { id: 'eCkuazw-DNU', category: 'ai_courses', level: 'beginner',     title_uz: "Hamma sun'iy intellektlardan foydalanishni 1 videoda o'rgataman", title_ru: 'Все ИИ в одном видео — научу пользоваться' },
  { id: 'orVrV9p_mlg', category: 'ai_courses', level: 'beginner',     title_uz: "Sun'iy intellektda real rasm qilishni o'rganasiz",          title_ru: 'Реалистичные изображения с ИИ за 1 клик' },
  { id: 'gHu0r7lvMWU', category: 'ai_courses', level: 'beginner',     title_uz: "7 daqiqada ingliz tilini bilmasdan zo'r prompt yozishni o'rganasiz", title_ru: 'Промпты без знания английского — за 7 минут' },
  { id: 'OuQOSbxYrfs', category: 'ai_courses', level: 'beginner',     title_uz: "5 daqiqada har xil stildagi rasm qilishni o'rganasiz",      title_ru: 'Изображения в разных стилях за 5 минут' },
  { id: '44TZG0PWXVI', category: 'ai_courses', level: 'intermediate', title_uz: "Sun'iy intellekt bilan kino videolar tayyorlashni o'rganasiz", title_ru: 'Кино-видео с помощью ИИ' },
  { id: 'Ms3Lm49jnOc', category: 'ai_courses', level: 'beginner',     title_uz: "Sun'iy intellekt bilan multfilm tayyorlashni o'rganasiz",   title_ru: 'Мультфильмы с ИИ — легко' },
  { id: 'Sb4wNxCjSUs', category: 'ai_courses', level: 'intermediate', title_uz: "7 daqiqada qimmat ko'rinishli videolar tayyorlash",         title_ru: 'Дорогие на вид видео за 7 минут с ИИ' },
  { id: 'qFJWOPQD5QQ', category: 'ai_courses', level: 'intermediate', title_uz: "Veo 3'da o'zbekcha video tayyorlashni o'rganasiz",          title_ru: 'Узбекоязычные видео в Veo 3 (бесплатно)' },
  { id: '06uCOuCo9FU', category: 'ai_courses', level: 'beginner',     title_uz: "Do'stingizning sun'iy intellekt videosini tayyorlash",      title_ru: 'AI-видео твоего друга' },
  { id: 'OA9D4OVDFWM', category: 'ai_courses', level: 'beginner',     title_uz: "Tarixiy shaxslarni hayotga qaytarishni o'rganasiz (AI bilan)", title_ru: 'Возвращаем к жизни исторических личностей с ИИ' },
  { id: 'bcta17YeUvA', category: 'ai_courses', level: 'beginner',     title_uz: "Bu sun'iy intellekt bobomni hayotga qaytardi",              title_ru: 'ИИ вернул моего деда к жизни' },
  { id: 'f6HpXx3k2L4', category: 'ai_courses', level: 'beginner',     title_uz: "Sun'iy intellekt bilan reklamalar qanday tayyorlanadi?",    title_ru: 'Как делают рекламы с ИИ?' },

  // ── Banking ──
  { id: 'xuIUtuZihIE', category: 'banking', level: 'beginner',     title_uz: "Bank nima? Bank qanday vazifalarni bajaradi?",                  title_ru: 'Что такое банк? Какие функции он выполняет?' },
  { id: 'X0pJB0tYEDM', category: 'banking', level: 'beginner',     title_uz: "Markaziy bank qanday vazifalarni bajaradi?",                    title_ru: 'Какие функции выполняет Центральный банк?' },
  { id: '9UW04JB9RxA', category: 'banking', level: 'intermediate', title_uz: "Provodka nima? To'g'ri provodka berish, ikki yoqlama yozuv",      title_ru: 'Что такое проводка? Двойная запись' },

  // ── Governance ──
  { id: 'eg03HUS_L-I', category: 'governance', level: 'beginner', title_uz: "Davlat boshqaruv shakli",                          title_ru: 'Формы государственного управления' },
  { id: 'cm7Sl9L22jA', category: 'governance', level: 'beginner', title_uz: "Davlat va Huquq Nazariyasi",                       title_ru: 'Теория государства и права' },
  { id: 'YMW2ZlSVfm0', category: 'governance', level: 'beginner', title_uz: "Raqamli O'zbekiston-2030 — bu nima?",               title_ru: 'Цифровой Узбекистан-2030 — что это?' },
  { id: 'FOR1XUNy9NQ', category: 'governance', level: 'beginner', title_uz: 'Raqamli iqtisodiyotni rivojlantirish strategiyasi', title_ru: 'Стратегия развития цифровой экономики' },

  // ── Entrepreneurs ──
  { id: 'oOyVFHpmD7g', category: 'entrepreneurs', level: 'beginner', title_uz: "Tadbirkorlik faoliyatining qaysi turini tanlash kerak?", title_ru: 'Какой вид предпринимательства выбрать?' },
  { id: 'yXtdxDAVFIQ', category: 'entrepreneurs', level: 'beginner', title_uz: "2025-yilda hayotingizni o'zgartiradigan 7 ta kasb",        title_ru: '7 профессий, которые изменят вашу жизнь в 2025' },
  { id: 'h4QgWVwBc5w', category: 'entrepreneurs', level: 'beginner', title_uz: "UZUM Marketda biznes boshlash — bepul kurs",              title_ru: 'Старт бизнеса на UZUM Market — бесплатный курс' },
]

const activeCategory = ref('all')
const activeLevel = ref('all')
const activeVideo = ref(null)

const titleFor = (v) => locale.value === 'ru' ? v.title_ru : v.title_uz
const thumbFor = (id) => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`

const categories = computed(() => [
  { key: 'all',           label: t('education.videoLib.catAll') },
  { key: 'ai_courses',    label: t('education.videoLib.cat_ai_courses') },
  { key: 'banking',       label: t('education.videoLib.cat_banking') },
  { key: 'governance',    label: t('education.videoLib.cat_governance') },
  { key: 'entrepreneurs', label: t('education.videoLib.cat_entrepreneurs') },
])

const levels = computed(() => [
  { key: 'all',          label: t('education.videoLib.lvlAll') },
  { key: 'beginner',     label: t('education.videoLib.lvlBeginner') },
  { key: 'intermediate', label: t('education.videoLib.lvlIntermediate') },
  { key: 'advanced',     label: t('education.videoLib.lvlAdvanced') },
])

const filteredVideos = computed(() =>
  VIDEOS.filter((v) =>
    (activeCategory.value === 'all' || v.category === activeCategory.value) &&
    (activeLevel.value === 'all' || v.level === activeLevel.value)
  )
)

function openVideo(v) { activeVideo.value = v }
function closeVideo() { activeVideo.value = null }

function onKey(e) { if (e.key === 'Escape') closeVideo() }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
watch(activeVideo, (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
})
</script>

<template>
  <section class="vid-lib">
    <div class="vid-lib__header">
      <h2 class="vid-lib__title">{{ $t('education.videoLib.title') }}</h2>
      <p class="vid-lib__subtitle">{{ $t('education.videoLib.subtitle') }}</p>
    </div>

    <div class="vid-lib__filters">
      <div class="vid-lib__pills">
        <button
          v-for="c in categories"
          :key="c.key"
          class="vid-lib__pill"
          :class="{ 'is-active': activeCategory === c.key }"
          @click="activeCategory = c.key"
        >
          {{ c.label }}
        </button>
      </div>
      <div class="vid-lib__pills">
        <span class="vid-lib__pill-label">{{ $t('education.videoLib.levelLabel') }}</span>
        <button
          v-for="l in levels"
          :key="l.key"
          class="vid-lib__pill vid-lib__pill--sm"
          :class="{ 'is-active': activeLevel === l.key }"
          @click="activeLevel = l.key"
        >
          {{ l.label }}
        </button>
      </div>
      <div class="vid-lib__count">{{ $t('education.videoLib.countFound', { n: filteredVideos.length }) }}</div>
    </div>

    <div class="vid-lib__grid">
      <article
        v-for="v in filteredVideos"
        :key="v.id"
        class="vid-card"
        @click="openVideo(v)"
      >
        <div class="vid-card__thumb">
          <img :src="thumbFor(v.id)" :alt="titleFor(v)" loading="lazy" />
          <div class="vid-card__play">
            <span class="material-symbols-outlined">play_arrow</span>
          </div>
          <span class="vid-card__cat">{{ $t('education.videoLib.cat_' + v.category) }}</span>
        </div>
        <div class="vid-card__body">
          <h3 class="vid-card__title">{{ titleFor(v) }}</h3>
        </div>
      </article>
    </div>

    <div v-if="activeVideo" class="vid-modal" @click.self="closeVideo">
      <div class="vid-modal__inner">
        <button
          class="vid-modal__close"
          type="button"
          :aria-label="$t('education.videoLib.close')"
          @click="closeVideo"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
        <h3 class="vid-modal__title">{{ titleFor(activeVideo) }}</h3>
        <EduVideoPlayer
          :src="`https://www.youtube.com/watch?v=${activeVideo.id}`"
          :title="titleFor(activeVideo)"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.vid-lib { margin-top: 56px; }
.vid-lib__header { margin-bottom: 16px; }
.vid-lib__title {
  font-family: 'Manrope', sans-serif;
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 6px;
  color: var(--edu-text, #0f172a);
  letter-spacing: -0.02em;
}
.vid-lib__subtitle {
  font-size: 15px;
  color: var(--edu-text-secondary, #475569);
  margin: 0;
}

.vid-lib__filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}
.vid-lib__pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.vid-lib__pill {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.vid-lib__pill--sm {
  padding: 6px 14px;
  font-size: 12px;
}
.vid-lib__pill:hover { border-color: #0054a6; color: #0054a6; }
.vid-lib__pill.is-active {
  background: #0054a6;
  color: #fff;
  border-color: #0054a6;
}
.vid-lib__pill-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
  margin-right: 4px;
}
.vid-lib__count {
  font-size: 13px;
  color: #64748b;
  margin-top: 2px;
}

.vid-lib__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.vid-card {
  background: var(--edu-bg-card, #fff);
  border: 1px solid var(--edu-border, #e2e8f0);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}
.vid-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.1);
  border-color: rgba(0, 61, 124, 0.2);
}
.vid-card__thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: #0b1e3f;
  overflow: hidden;
}
.vid-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  display: block;
}
.vid-card:hover .vid-card__thumb img { transform: scale(1.04); }
.vid-card__play {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  opacity: 0;
  transition: opacity 0.2s ease;
}
.vid-card:hover .vid-card__play { opacity: 1; }
.vid-card__play .material-symbols-outlined {
  font-size: 40px;
  color: #fff;
  background: rgba(0, 84, 166, 0.92);
  border-radius: 50%;
  padding: 14px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.35));
}
.vid-card__cat {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(0, 61, 124, 0.9);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  backdrop-filter: blur(4px);
}
.vid-card__body { padding: 14px 16px 18px; }
.vid-card__title {
  font-size: 15px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--edu-text, #0f172a);
  margin: 0;
}

.vid-modal {
  position: fixed;
  inset: 0;
  background: rgba(8, 15, 30, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}
.vid-modal__inner {
  width: min(960px, 100%);
  background: #0b1220;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
}
.vid-modal__close {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
}
.vid-modal__close:hover { background: rgba(255, 255, 255, 0.28); }
.vid-modal__close .material-symbols-outlined { font-size: 22px; }
.vid-modal__title {
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  padding: 16px 56px 12px 20px;
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 600px) {
  .vid-lib__title { font-size: 22px; }
  .vid-modal { padding: 12px; }
}
</style>
