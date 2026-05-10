<script setup>
/* Wraps every cerr-v2 view inside `.cerr-v2-scope` so the ported design tokens
 * apply only here. Renders the breadcrumb topbar above the active route view. */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import '@/styles/cerr-v2-theme.css'

const route = useRoute()
const router = useRouter()
const store = useCerrV2Store()
const { t: tFn } = useI18n()

const crumbs = computed(() => {
  const out = [{ label: tFn('cerrV2.country.title'), target: { name: 'cerr-v2-country' } }]
  const rc = Number(route.params.regionCode || 0)
  const dc = Number(route.params.districtCode || 0)
  const stir = route.params.stir ? String(route.params.stir) : null

  // Resolve owning region/district for mahalla page from cached summary records.
  let mahallaSummary = null
  if (stir) {
    for (const list of Object.values(store.districtMahallas)) {
      const m = (list || []).find((mm) => String(mm.stir) === stir)
      if (m) { mahallaSummary = m; break }
    }
  }

  const effectiveRc = rc || mahallaSummary?.region_oktmo
  const effectiveDc = dc || mahallaSummary?.district_oktmo

  if (effectiveRc) {
    const r = store.regionByCode(effectiveRc)
    out.push({
      label: r?.name || tFn('cerrV2.topbar.regionFallback', { code: effectiveRc }),
      target: { name: 'cerr-v2-region', params: { regionCode: effectiveRc } },
    })
  }
  if (effectiveDc) {
    const d = store.districtByCode(effectiveDc)
    out.push({
      label: d?.name || tFn('cerrV2.topbar.districtFallback', { code: effectiveDc }),
      target: stir ? { name: 'cerr-v2-district', params: { districtCode: effectiveDc } } : null,
    })
  }
  if (stir) {
    const ov = store.mahallaOverview[stir]
    out.push({
      label: ov?.header?.title || mahallaSummary?.name || tFn('cerrV2.topbar.mahallaFallback', { stir }),
      target: null,
    })
  }
  return out
})

function go(target) { if (target) router.push(target) }
</script>

<template>
  <div class="cerr-v2-scope cerr-v2-root">
    <header class="topbar">
      <h1>{{ $t('cerrV2.topbar.title') }}</h1>
      <span class="crumb-sep">/</span>
      <div class="crumbs">
        <template v-for="(c, i) in crumbs" :key="i">
          <span v-if="i > 0" class="crumb-sep">›</span>
          <button
            :class="['crumb', i === crumbs.length - 1 ? 'current' : '']"
            @click="i < crumbs.length - 1 && go(c.target)"
          >{{ c.label }}</button>
        </template>
      </div>
    </header>
    <router-view />
  </div>
</template>

<style>
/* Ensure the wrapper stretches to fill the platform's main content area. */
.cerr-v2-scope.cerr-v2-root {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: var(--bg, #f3f4f7);
}
</style>
