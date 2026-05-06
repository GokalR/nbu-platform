<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import BreadcrumbNav from '@/components/regionsV2/BreadcrumbNav.vue'
import KpiCard from '@/components/regionsV2/KpiCard.vue'
import { cerrApi } from '@/services/cerrApi'
import '@/assets/regionsV2.css'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const regionCode = computed(() => Number(route.params.regionCode))
const region = ref(null)
const overview = ref(null)
const districts = ref([])
const loading = ref(true)
const error = ref(null)

watchEffect(async () => {
  const code = regionCode.value
  if (!code) return
  loading.value = true
  error.value = null
  region.value = null
  overview.value = null
  districts.value = []

  const [r, ov, dl] = await Promise.all([
    cerrApi.getRegion(code),
    cerrApi.getRegionOverview(code),
    cerrApi.listRegionDistricts(code),
  ])
  loading.value = false
  if (!r.ok) {
    error.value = r.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  region.value = r.data
  overview.value = ov.ok ? ov.data : null
  districts.value = dl.ok ? dl.data : []
})

const kpis = computed(() => overview.value?.kpis || [])

const breadcrumb = computed(() => [
  { label: t('regionsV2.title'), to: '/regions-v2' },
  { label: region.value?.name || '…' },
])

function openDistrict(code) {
  router.push(`/regions-v2/districts/${code}`)
}

function fmt(n) { return (n || 0).toLocaleString('ru-RU') }
</script>

<template>
  <div class="regions-v2">
    <div class="v2-shell">
      <div v-if="loading" class="empty">{{ t('regionsV2.loading') }}</div>

      <div v-else-if="error" class="alert">{{ error }}</div>

      <template v-else-if="region">
        <!-- Hero -->
        <section class="hero">
          <div class="hero-left">
            <BreadcrumbNav :items="breadcrumb" />
            <h1 class="h-title">{{ region.name }}</h1>
            <p class="h-sub">
              {{ region.districts_count }} {{ t('regionsV2.districtsCount').toLowerCase() }}
              ·
              {{ fmt(region.mahalla_count) }} {{ t('regionsV2.mahallasCount').toLowerCase() }}
            </p>
          </div>
          <div class="hero-right">
            <div class="kpi-icon" style="width:64px;height:64px;border-radius:16px;font-size:28px">
              <AppIcon name="map" />
            </div>
            <div>
              <div class="kpi-label">{{ t('regionsV2.regionsHeading') }}</div>
              <div class="kpi-value num">{{ region.name }}</div>
              <div style="display:flex;gap:6px;margin-top:6px">
                <span class="chip pale">{{ region.districts_count }} {{ t('regionsV2.districtsCount').toLowerCase() }}</span>
                <span class="chip">{{ fmt(region.mahalla_count) }} {{ t('regionsV2.mahallasCount').toLowerCase() }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- KPI strip -->
        <section v-if="kpis.length" class="kpi-grid">
          <KpiCard v-for="(k, i) in kpis" :key="i" :kpi="k" />
        </section>

        <!-- Districts panel -->
        <section class="card">
          <header class="card-head">
            <h3>{{ t('regionsV2.districtsHeading') }}</h3>
            <span class="chip">{{ districts.length }}</span>
          </header>
          <div class="card-body">
            <div class="kpi-grid">
              <button
                v-for="d in districts"
                :key="d.code"
                class="tile"
                @click="openDistrict(d.code)"
              >
                <div class="tile-head">
                  <div class="tile-mark"><AppIcon name="location_city" /></div>
                  <div style="flex:1;min-width:0">
                    <div class="tile-name">{{ d.name }}</div>
                  </div>
                  <AppIcon name="chevron_right" class="muted" />
                </div>
                <div class="tile-stats">
                  <span><b>{{ fmt(d.mahalla_count) }}</b> {{ t('regionsV2.mahallasCount').toLowerCase() }}</span>
                  <span v-if="d.has_geo" class="chip green" style="font-size:10px;padding:2px 6px">
                    <AppIcon name="map" class="!text-xs" /> Карта
                  </span>
                </div>
              </button>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>
