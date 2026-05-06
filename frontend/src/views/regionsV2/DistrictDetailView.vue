<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import BreadcrumbNav from '@/components/regionsV2/BreadcrumbNav.vue'
import KpiCard from '@/components/regionsV2/KpiCard.vue'
import CerrMap from '@/components/regionsV2/CerrMap.vue'
import MahallaTable from '@/components/regionsV2/MahallaTable.vue'
import { cerrApi } from '@/services/cerrApi'
import '@/assets/regionsV2.css'

const { t } = useI18n()
const route = useRoute()

const districtCode = computed(() => Number(route.params.districtCode))
const district = ref(null)
const overview = ref(null)
const mahallas = ref([])
const geo = ref(null)
const loading = ref(true)
const error = ref(null)
const hoveredStir = ref(null)

watchEffect(async () => {
  const code = districtCode.value
  if (!code) return
  loading.value = true
  error.value = null
  district.value = null
  overview.value = null
  mahallas.value = []
  geo.value = null

  const [d, ov, ml, g] = await Promise.all([
    cerrApi.getDistrict(code),
    cerrApi.getDistrictOverview(code),
    cerrApi.listDistrictMahallas(code),
    cerrApi.getDistrictGeo(code),
  ])
  loading.value = false
  if (!d.ok) {
    error.value = d.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  district.value = d.data
  overview.value = ov.ok ? ov.data : null
  mahallas.value = ml.ok ? ml.data : []
  geo.value = g.ok ? g.data : null
})

const kpis = computed(() => overview.value?.kpis || [])

const breadcrumb = computed(() => {
  if (!district.value) return [{ label: t('regionsV2.title'), to: '/regions-v2' }]
  return [
    { label: t('regionsV2.title'), to: '/regions-v2' },
    { label: district.value.region_name, to: `/regions-v2/regions/${district.value.region_code}` },
    { label: district.value.name },
  ]
})

function fmt(n) { return (n || 0).toLocaleString('ru-RU') }
</script>

<template>
  <div class="regions-v2">
    <div class="v2-shell">
      <div v-if="loading" class="empty">{{ t('regionsV2.loading') }}</div>

      <div v-else-if="error" class="alert">{{ error }}</div>

      <template v-else-if="district">
        <!-- Hero -->
        <section class="hero">
          <div class="hero-left">
            <BreadcrumbNav :items="breadcrumb" />
            <h1 class="h-title">{{ district.name }}</h1>
            <p class="h-sub">
              {{ district.region_name }} ·
              <b class="num">{{ fmt(district.mahalla_count) }}</b> {{ t('regionsV2.mahallasCount').toLowerCase() }}
            </p>
          </div>
          <div class="hero-right">
            <div class="kpi-icon" style="width:64px;height:64px;border-radius:16px;font-size:28px">
              <AppIcon name="location_city" />
            </div>
            <div>
              <div class="kpi-label">{{ district.region_name }}</div>
              <div class="kpi-value num">{{ district.name }}</div>
            </div>
          </div>
        </section>

        <!-- KPI strip -->
        <section v-if="kpis.length" class="kpi-grid">
          <KpiCard v-for="(k, i) in kpis" :key="i" :kpi="k" />
        </section>

        <!-- Map + table side by side -->
        <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:14px" class="map-table-row">
          <section class="card map-wrap" style="padding:0;min-height:540px">
            <CerrMap
              :geo="geo"
              :mahallas="mahallas"
              :highlighted-stir="hoveredStir"
              style="height:100%"
              @hover="(s) => (hoveredStir = s)"
              @select="(s) => $router.push(`/regions-v2/mahallas/${s}`)"
            />
          </section>
          <section class="card" style="display:flex;flex-direction:column;min-height:540px">
            <header class="card-head">
              <h3>{{ t('regionsV2.mahallasHeading') }}</h3>
              <span class="chip">{{ mahallas.length }}</span>
            </header>
            <div style="flex:1;overflow-y:auto;padding:0 0 12px">
              <MahallaTable
                :mahallas="mahallas"
                :highlighted-stir="hoveredStir"
                @hover="(s) => (hoveredStir = s)"
              />
            </div>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 1024px) {
  .map-table-row {
    grid-template-columns: 1fr !important;
  }
}
</style>
