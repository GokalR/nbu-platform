<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEduAuthStore } from '@/stores/eduAuth'
import { rsApi } from '@/services/rsApi'
import RsHeader from '@/components/regionalStrategist/RsHeader.vue'
import { useRsLang } from '@/composables/useRsLang'

const { lang } = useRsLang()
const router = useRouter()
const auth = useEduAuthStore()

const submissions = ref([])
const loading = ref(true)
const error = ref(null)

const T = {
  ru: {
    title: 'Мои результаты',
    subtitle: 'История ваших AI-анализов',
    empty: 'У вас пока нет анализов. Пройдите анкету, чтобы получить первый результат.',
    startNew: 'Новый анализ',
    loginRequired: 'Войдите в аккаунт, чтобы увидеть ваши результаты',
    loginBtn: 'Войти',
    verdict: { good: 'Хороший', fair: 'Средний', weak: 'Слабый' },
    business: 'Бизнес',
    city: 'Город',
    date: 'Дата',
    viewDetails: 'Подробнее',
    error: 'Не удалось загрузить результаты',
  },
  uz: {
    title: 'Mening natijalarim',
    subtitle: 'AI tahlillar tarixi',
    empty: 'Sizda hali tahlillar yoʻq. Anketani toʻldiring va birinchi natijani oling.',
    startNew: 'Yangi tahlil',
    loginRequired: 'Natijalarni koʻrish uchun tizimga kiring',
    loginBtn: 'Kirish',
    verdict: { good: 'Yaxshi', fair: 'Oʻrtacha', weak: 'Past' },
    business: 'Biznes',
    city: 'Shahar',
    date: 'Sana',
    viewDetails: 'Batafsil',
    error: 'Natijalarni yuklab boʻlmadi',
  },
}

const t = computed(() => T[lang.value] || T.ru)

const verdictColor = (v) => {
  if (v === 'good') return 'bg-emerald-100 text-emerald-800 border-emerald-300'
  if (v === 'fair') return 'bg-amber-100 text-amber-800 border-amber-300'
  return 'bg-red-100 text-red-800 border-red-300'
}

function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString(lang.value === 'uz' ? 'uz-UZ' : 'ru-RU', {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

onMounted(async () => {
  if (!auth.isAuthenticated) {
    loading.value = false
    return
  }
  try {
    const res = await rsApi.mySubmissions()
    if (res.ok) {
      submissions.value = res.data
    } else {
      error.value = res.error || t.value.error
    }
  } catch (e) {
    error.value = t.value.error
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <RsHeader />

    <div class="max-w-4xl mx-auto px-4 py-10">
      <h1 class="text-3xl font-bold text-slate-800 mb-1">{{ t.title }}</h1>
      <p class="text-slate-500 mb-8">{{ t.subtitle }}</p>

      <!-- Not logged in -->
      <div v-if="!auth.isAuthenticated && !loading"
           class="text-center py-16 bg-white rounded-2xl shadow-sm border border-slate-200">
        <div class="text-5xl mb-4">🔐</div>
        <p class="text-slate-600 mb-6">{{ t.loginRequired }}</p>
        <button @click="router.push('/education')"
                class="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition">
          {{ t.loginBtn }}
        </button>
      </div>

      <!-- Loading -->
      <div v-else-if="loading" class="text-center py-16">
        <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-16 text-red-500">{{ error }}</div>

      <!-- Empty -->
      <div v-else-if="submissions.length === 0"
           class="text-center py-16 bg-white rounded-2xl shadow-sm border border-slate-200">
        <div class="text-5xl mb-4">📋</div>
        <p class="text-slate-600 mb-6">{{ t.empty }}</p>
        <button @click="router.push('/tools/regional-strategist/test')"
                class="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition">
          {{ t.startNew }}
        </button>
      </div>

      <!-- Submissions list -->
      <div v-else class="space-y-4">
        <div v-for="sub in submissions" :key="sub.id"
             class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition cursor-pointer"
             @click="router.push(`/tools/regional-strategist/test?submission=${sub.id}`)">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <!-- Business name -->
              <h3 class="text-lg font-semibold text-slate-800 truncate">
                {{ sub.profile?.name || sub.finance?.businessDirection || t.business }}
              </h3>

              <!-- City + date -->
              <div class="flex items-center gap-3 mt-1 text-sm text-slate-500">
                <span v-if="sub.city_id" class="flex items-center gap-1">
                  📍 {{ sub.city_id }}
                </span>
                <span>{{ formatDate(sub.created_at) }}</span>
              </div>

              <!-- Summary -->
              <p v-if="sub.latest_analysis?.summary" class="mt-3 text-sm text-slate-600 line-clamp-2">
                {{ sub.latest_analysis.summary }}
              </p>
            </div>

            <!-- Verdict badge -->
            <div v-if="sub.latest_analysis?.verdict"
                 class="shrink-0 px-3 py-1 rounded-full text-sm font-medium border"
                 :class="verdictColor(sub.latest_analysis.verdict)">
              {{ t.verdict[sub.latest_analysis.verdict] || sub.latest_analysis.verdict }}
            </div>

            <!-- No analysis yet -->
            <div v-else-if="sub.latest_analysis?.error"
                 class="shrink-0 px-3 py-1 rounded-full text-sm font-medium bg-red-50 text-red-600 border border-red-200">
              Error
            </div>

            <div v-else
                 class="shrink-0 px-3 py-1 rounded-full text-sm font-medium bg-slate-100 text-slate-500 border border-slate-200">
              —
            </div>
          </div>
        </div>

        <!-- New analysis button -->
        <div class="text-center pt-4">
          <button @click="router.push('/tools/regional-strategist/test')"
                  class="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition">
            {{ t.startNew }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
