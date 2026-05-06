<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import { cerrApi } from '@/services/cerrApi'
import '@/assets/regionsV2.css'

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
  let mahallas = 0, districts = 0
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

function fmt(n) {
  return (n || 0).toLocaleString('ru-RU')
}
</script>

<template>
  <div class="regions-v2">
    <div class="v2-shell">
      <!-- Hero strip with breadcrumb + 3 KPIs on the right -->
      <section class="hero">
        <div class="hero-left">
          <nav class="crumb">
            <span class="here">{{ t('regionsV2.title') }}</span>
          </nav>
          <h1 class="h-title">{{ t('regionsV2.title') }}</h1>
          <p class="h-sub">{{ t('regionsV2.subtitle') }}</p>
          <div class="h-meta">
            <span class="chip pale"><AppIcon name="public" class="!text-base" />Ўзбекистон</span>
          </div>
        </div>

        <div class="hero-right" v-if="!loading && !error && regions.length">
          <div class="kpi-icon" style="width:64px;height:64px;border-radius:16px;font-size:28px">
            <AppIcon name="map" />
          </div>
          <div style="display:flex;flex-direction:column;gap:6px">
            <div style="display:flex;gap:24px">
              <div>
                <div class="kpi-label">{{ t('regionsV2.regionsHeading') }}</div>
                <div class="kpi-value num">{{ totals.regions }}</div>
              </div>
              <div>
                <div class="kpi-label">{{ t('regionsV2.districtsCount') }}</div>
                <div class="kpi-value num">{{ totals.districts }}</div>
              </div>
            </div>
            <div>
              <div class="kpi-label">{{ t('regionsV2.mahallasCount') }}</div>
              <div class="kpi-value num">{{ fmt(totals.mahallas) }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Search -->
      <div class="search-row" v-if="!loading && !error">
        <AppIcon name="search" />
        <input
          v-model="search"
          type="search"
          :placeholder="t('common.search')"
          autocomplete="off"
        />
      </div>

      <div v-if="loading" class="empty">{{ t('regionsV2.loading') }}</div>

      <div v-else-if="error" class="alert">{{ error }}</div>

      <template v-else>
        <!-- Region tile grid -->
        <div class="kpi-grid" v-if="filtered.length">
          <button
            v-for="r in filtered"
            :key="r.code"
            class="tile"
            @click="openRegion(r.code)"
          >
            <div class="tile-head">
              <div class="tile-mark">
                <AppIcon name="map" />
              </div>
              <div style="flex:1;min-width:0">
                <div class="tile-name">{{ r.name }}</div>
              </div>
              <AppIcon name="chevron_right" class="muted" />
            </div>
            <div class="tile-stats">
              <span><b>{{ r.districts_count }}</b> {{ t('regionsV2.districtsCount').toLowerCase() }}</span>
              <span><b>{{ fmt(r.mahalla_count) }}</b> {{ t('regionsV2.mahallasCount').toLowerCase() }}</span>
            </div>
          </button>
        </div>

        <div v-else class="empty">{{ t('regionsV2.noData') }}</div>
      </template>
    </div>
  </div>
</template>
