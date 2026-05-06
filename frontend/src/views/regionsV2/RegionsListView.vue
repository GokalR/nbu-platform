<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import { cerrApi } from '@/services/cerrApi'

const { t } = useI18n()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const regions = ref([])
const search = ref('')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return regions.value
  return regions.value.filter((r) => (r.name || '').toLowerCase().includes(q))
})

const totals = computed(() => {
  let mahallas = 0
  let districts = 0
  for (const r of regions.value) {
    mahallas += r.mahalla_count || 0
    districts += r.districts_count || 0
  }
  return { mahallas, districts, regions: regions.value.length }
})

onMounted(async () => {
  const res = await cerrApi.listRegions()
  loading.value = false
  if (!res.ok) {
    error.value = res.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  regions.value = res.data || []
})

function openRegion(code) {
  router.push(`/regions-v2/regions/${code}`)
}
</script>

<template>
  <div class="px-6 lg:px-10 py-8 max-w-7xl mx-auto">
    <header class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-violet-600 flex items-center justify-center shadow-md">
          <AppIcon name="public" class="text-white !text-2xl" />
        </div>
        <div>
          <h1 class="text-3xl font-black text-slate-900 leading-tight">{{ t('regionsV2.title') }}</h1>
          <p class="text-sm text-slate-500 mt-0.5">{{ t('regionsV2.subtitle') }}</p>
        </div>
      </div>

      <div v-if="!loading && !error && regions.length" class="grid grid-cols-3 gap-3 mt-6 max-w-2xl">
        <div class="rounded-xl bg-white border border-slate-200/70 p-4">
          <div class="text-xs font-medium text-slate-500">{{ t('regionsV2.regionsHeading') }}</div>
          <div class="text-2xl font-black text-slate-900 mt-1">{{ totals.regions }}</div>
        </div>
        <div class="rounded-xl bg-white border border-slate-200/70 p-4">
          <div class="text-xs font-medium text-slate-500">{{ t('regionsV2.districtsCount') }}</div>
          <div class="text-2xl font-black text-slate-900 mt-1">{{ totals.districts }}</div>
        </div>
        <div class="rounded-xl bg-white border border-slate-200/70 p-4">
          <div class="text-xs font-medium text-slate-500">{{ t('regionsV2.mahallasCount') }}</div>
          <div class="text-2xl font-black text-slate-900 mt-1">{{ totals.mahallas.toLocaleString('ru-RU') }}</div>
        </div>
      </div>
    </header>

    <div v-if="loading" class="text-slate-500 py-20 text-center">{{ t('regionsV2.loading') }}</div>

    <div
      v-else-if="error"
      class="rounded-xl bg-amber-50 border border-amber-200 p-4 text-amber-900 text-sm"
    >
      {{ error }}
    </div>

    <template v-else>
      <div class="mb-5 max-w-md">
        <div class="relative">
          <AppIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="search"
            type="search"
            :placeholder="t('common.search')"
            class="w-full pl-10 pr-3 py-2.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
          />
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <button
          v-for="r in filtered"
          :key="r.code"
          class="group text-left rounded-2xl bg-white border border-slate-200/70 p-5 hover:shadow-lg hover:border-blue-300 transition-all duration-200"
          @click="openRegion(r.code)"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center group-hover:bg-blue-100 transition-colors">
              <AppIcon name="map" class="text-blue-700" />
            </div>
            <AppIcon
              name="arrow_forward"
              class="text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all"
            />
          </div>
          <div class="text-base font-bold text-slate-900 leading-tight mb-1">{{ r.name }}</div>
          <div class="text-xs text-slate-500">
            {{ r.districts_count }} · {{ t('regionsV2.districtsCount').toLowerCase() }}
            &middot;
            {{ (r.mahalla_count || 0).toLocaleString('ru-RU') }} {{ t('regionsV2.mahallasCount').toLowerCase() }}
          </div>
        </button>
      </div>

      <div v-if="!filtered.length" class="text-center text-slate-500 py-16">
        {{ t('regionsV2.noData') }}
      </div>
    </template>
  </div>
</template>
