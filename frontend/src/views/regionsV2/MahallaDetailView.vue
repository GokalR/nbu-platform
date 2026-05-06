<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import BreadcrumbNav from '@/components/regionsV2/BreadcrumbNav.vue'
import KpiCard from '@/components/regionsV2/KpiCard.vue'
import AiInsightsPanel from '@/components/regionsV2/AiInsightsPanel.vue'
import { cerrApi } from '@/services/cerrApi'
import '@/assets/regionsV2.css'

const { t } = useI18n()
const route = useRoute()

const stir = computed(() => String(route.params.stir))
const overview = ref(null)
const loading = ref(true)
const error = ref(null)

watchEffect(async () => {
  const s = stir.value
  if (!s) return
  loading.value = true
  error.value = null
  overview.value = null
  const res = await cerrApi.getMahalla(s)
  loading.value = false
  if (!res.ok) {
    error.value = res.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  overview.value = res.data
})

const header = computed(() => overview.value?.header || {})
const kpis = computed(() => overview.value?.kpis || [])
const aiInsights = computed(() => overview.value?.ai_insights || null)
const peerProfile = computed(() => overview.value?.peer_profile || null)
const detail = computed(() => overview.value?.detail || null)

const districtCode = computed(() => overview.value?.district_oktmo || overview.value?.district_code)
const regionCode = computed(() => overview.value?.region_oktmo || overview.value?.region_code)

const breadcrumb = computed(() => {
  const items = [{ label: t('regionsV2.title'), to: '/regions-v2' }]
  const crumbs = header.value?.breadcrumb
  if (Array.isArray(crumbs) && crumbs.length >= 3) {
    const regionLabel = crumbs[1]
    const districtLabel = crumbs[2]
    if (regionLabel) items.push({ label: regionLabel, to: regionCode.value ? `/regions-v2/regions/${regionCode.value}` : null })
    if (districtLabel) items.push({ label: districtLabel, to: districtCode.value ? `/regions-v2/districts/${districtCode.value}` : null })
  }
  items.push({ label: header.value?.title || stir.value })
  return items
})
</script>

<template>
  <div class="regions-v2">
    <div class="v2-shell">
      <div v-if="loading" class="empty">{{ t('regionsV2.loading') }}</div>

      <div v-else-if="error" class="alert">{{ error }}</div>

      <template v-else-if="overview">
        <!-- Hero -->
        <section class="hero">
          <div class="hero-left">
            <BreadcrumbNav :items="breadcrumb" />
            <h1 class="h-title">{{ header.title || $t('common.mahalla') }}</h1>
            <p v-if="header.subtitle" class="h-sub">{{ header.subtitle }}</p>
            <div class="h-meta">
              <span class="chip pale" style="font-family:'Geist Mono',monospace">
                STIR · {{ stir }}
              </span>
            </div>
          </div>
          <div class="hero-right">
            <div class="kpi-icon" style="width:64px;height:64px;border-radius:16px;font-size:28px">
              <AppIcon name="apartment" />
            </div>
            <div>
              <div class="kpi-label">{{ $t('common.mahalla') }}</div>
              <div class="kpi-value num">{{ header.title }}</div>
            </div>
          </div>
        </section>

        <!-- KPI strip -->
        <section v-if="kpis.length" class="kpi-grid">
          <KpiCard v-for="(k, i) in kpis" :key="i" :kpi="k" />
        </section>

        <!-- AI insights -->
        <AiInsightsPanel :insights="aiInsights" />

        <!-- Peer profile if present -->
        <section v-if="peerProfile && Array.isArray(peerProfile.rows) && peerProfile.rows.length" class="card">
          <header class="card-head">
            <h3>Сравнение с соседями</h3>
            <span v-if="peerProfile.scope" class="chip">{{ peerProfile.scope }}</span>
          </header>
          <div class="card-body" style="padding:0 20px 18px">
            <div style="display:flex;flex-direction:column;gap:0">
              <div
                v-for="(row, i) in peerProfile.rows"
                :key="i"
                style="
                  border-bottom: 1px dashed var(--border-subtle);
                  padding: 9px 0;
                  display: flex;
                  flex-direction: column;
                  gap: 3px;
                "
              >
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
                  <span style="font-size:12.5px;font-weight:600;color:var(--text-primary)">
                    {{ row.label }}
                  </span>
                  <span
                    class="chip pale num"
                    style="font-size:10.5px;padding:2px 8px"
                  >
                    {{ row.rank || '—' }}
                  </span>
                </div>
                <div
                  v-if="row.value !== undefined || row.peer_avg !== undefined"
                  style="font-size:11.5px;color:var(--text-muted);display:flex;gap:10px;flex-wrap:wrap"
                >
                  <span v-if="row.value !== undefined" class="num">{{ row.value }}</span>
                  <span v-if="row.peer_avg !== undefined">vs <span class="num">{{ row.peer_avg }}</span></span>
                  <span v-if="row.unit" style="color:var(--text-faint);font-style:italic">{{ row.unit }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>
