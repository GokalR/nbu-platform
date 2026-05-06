<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import EduVideoPlayer from '@/components/education/EduVideoPlayer.vue'

const { t, locale } = useI18n()

const VIDEOS = [
  { id: 'XtizkYKT280', category: 'ai',   title_uz: "Sun'iy intellekt nima? To'liq obzor",                title_ru: 'Что такое искусственный интеллект? Полный обзор' },
  { id: 'N25wGvmun6g', category: 'ai',   title_uz: "Sun'iy intellekt qanday yaratiladi?",                 title_ru: 'Как создаётся искусственный интеллект?' },
  { id: 'vlozVjE-IvE', category: 'ai',   title_uz: "Sun'iy intellekt va dasturlashning kelajagi",          title_ru: 'Будущее ИИ и программирования' },
  { id: 'Nt5ee-3fyAc', category: 'ai',   title_uz: "ChatGPT — sun'iy aql kelajakka eshik ochdi",           title_ru: 'ChatGPT — ИИ открывает дверь в будущее' },
  { id: '1hNxd2ldlRY', category: 'data', title_uz: 'Machine Learning nima? Data Science kursi',           title_ru: 'Что такое Machine Learning? Курс Data Science' },
  { id: 'CHU6uI9ajBw', category: 'data', title_uz: 'Machine Learning nima?',                               title_ru: 'Что такое Machine Learning?' },
  { id: 'YMW2ZlSVfm0', category: 'sme',  title_uz: "Raqamli O'zbekiston-2030 — bu nima?",                   title_ru: 'Цифровой Узбекистан-2030 — что это?' },
  { id: 'FOR1XUNy9NQ', category: 'sme',  title_uz: 'Raqamli iqtisodiyotni rivojlantirish strategiyasi',     title_ru: 'Стратегия развития цифровой экономики' },
]

const activeCategory = ref('all')
const activeVideo = ref(null)

const titleFor = (v) => locale.value === 'ru' ? v.title_ru : v.title_uz
const thumbFor = (id) => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`

const categories = computed(() => [
  { key: 'all',  label: t('education.videoLib.all') },
  { key: 'ai',   label: t('education.videoLib.ai') },
  { key: 'data', label: t('education.videoLib.data') },
  { key: 'sme',  label: t('education.videoLib.sme') },
])

const filteredVideos = computed(() => {
  if (activeCategory.value === 'all') return VIDEOS
  return VIDEOS.filter((v) => v.category === activeCategory.value)
})

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
          <span class="vid-card__cat">{{ $t('education.videoLib.' + v.category) }}</span>
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

.vid-lib__pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
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
.vid-lib__pill:hover { border-color: #0054a6; color: #0054a6; }
.vid-lib__pill.is-active {
  background: #0054a6;
  color: #fff;
  border-color: #0054a6;
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
