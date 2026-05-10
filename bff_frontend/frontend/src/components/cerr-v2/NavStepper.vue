<script setup>
/** Compact 4-level navigation pill at the top of the rail.
 *  Узбекистан → Регион → Район → Махалля. Each level is clickable when
 *  context exists; "—" for levels you haven't drilled into yet. */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import CerrIcon from './CerrIcon.vue'

const route = useRoute()
const router = useRouter()
const store = useCerrV2Store()
const { t: tFn } = useI18n()

const props = defineProps({
  /** Optional: { stir, name } override for the active mahalla. Falls back to
   *  the route's :stir param when present. */
  mahalla: { type: Object, default: null },
})

const regionCode = computed(() => Number(route.params.regionCode || 0) || null)
const districtCode = computed(() => Number(route.params.districtCode || 0) || null)
const routeStir = computed(() => route.params.stir ? String(route.params.stir) : null)

const region = computed(() => regionCode.value ? store.regionByCode(regionCode.value) : null)
const district = computed(() => districtCode.value ? store.districtByCode(districtCode.value) : null)
const districtRegionCode = computed(() => district.value?.region_code || null)

/** When on /mahalla/:stir, look up the mahalla's owning district + region from
 *  cached summary records (DistrictView preloads them when you click a mahalla). */
const mahallaSummary = computed(() => {
  if (!routeStir.value) return null
  for (const list of Object.values(store.districtMahallas)) {
    const m = (list || []).find((mm) => String(mm.stir) === routeStir.value)
    if (m) return m
  }
  return null
})
const activeMahalla = computed(() => {
  if (props.mahalla) return props.mahalla
  if (routeStir.value) {
    const overview = store.mahallaOverview[routeStir.value]
    return {
      stir: routeStir.value,
      name: overview?.header?.title || mahallaSummary.value?.name || `STIR ${routeStir.value}`,
    }
  }
  return null
})
const effectiveDistrictCode = computed(() => districtCode.value || mahallaSummary.value?.district_oktmo || null)
const effectiveRegionCode = computed(() => regionCode.value || districtRegionCode.value || mahallaSummary.value?.region_oktmo || null)
const effectiveDistrict = computed(() => effectiveDistrictCode.value ? store.districtByCode(effectiveDistrictCode.value) : null)
const effectiveRegion = computed(() => effectiveRegionCode.value ? store.regionByCode(effectiveRegionCode.value) : null)

const levels = computed(() => [
  {
    key: 'country',
    icon: 'globe',
    label: tFn('cerrV2.stepper.uzbekistan'),
    sub: tFn('cerrV2.stepper.uzSub'),
    active: !regionCode.value && !districtCode.value && !routeStir.value,
    target: { name: 'cerr-v2-country' },
  },
  {
    key: 'region',
    icon: 'map',
    label: effectiveRegion.value?.name
      || (effectiveRegionCode.value
        ? tFn('cerrV2.stepper.regionFmt', { code: effectiveRegionCode.value })
        : tFn('cerrV2.stepper.region')),
    sub: effectiveRegion.value
      ? tFn('cerrV2.stepper.regionDistrictsShort', { n: effectiveRegion.value.districts_count })
      : '—',
    active: !!regionCode.value && !districtCode.value && !routeStir.value,
    target: effectiveRegionCode.value
      ? { name: 'cerr-v2-region', params: { regionCode: effectiveRegionCode.value } }
      : null,
    disabled: !effectiveRegionCode.value,
  },
  {
    key: 'district',
    icon: 'pin',
    label: effectiveDistrict.value?.name
      || (effectiveDistrictCode.value
        ? tFn('cerrV2.stepper.districtFmt', { code: effectiveDistrictCode.value })
        : tFn('cerrV2.stepper.districtCity')),
    sub: effectiveDistrict.value
      ? tFn('cerrV2.stepper.mahallaCount', { n: effectiveDistrict.value.mahalla_count })
      : '—',
    active: !!districtCode.value && !routeStir.value,
    target: effectiveDistrictCode.value
      ? { name: 'cerr-v2-district', params: { districtCode: effectiveDistrictCode.value } }
      : null,
    disabled: !effectiveDistrictCode.value,
  },
  {
    key: 'mahalla',
    icon: 'grid',
    label: activeMahalla.value?.name || tFn('cerrV2.stepper.mahalla'),
    sub: activeMahalla.value?.stir ? `STIR ${activeMahalla.value.stir}` : '—',
    active: !!routeStir.value || !!props.mahalla,
    target: activeMahalla.value?.stir && !routeStir.value
      ? { name: 'cerr-v2-mahalla', params: { stir: String(activeMahalla.value.stir) } }
      : null,
    disabled: !activeMahalla.value,
  },
])

function go(target) {
  if (target) router.push(target)
}
</script>

<template>
  <div class="nav-stepper">
    <button
      v-for="(l, i) in levels"
      :key="l.key"
      :class="['nav-step', l.active ? 'is-active' : '', l.disabled ? 'is-disabled' : '']"
      :disabled="l.disabled || !l.target"
      @click="go(l.target)"
    >
      <span class="ico"><CerrIcon :name="l.icon" :size="14" /></span>
      <span class="lbl">
        <span class="nm">{{ l.label }}</span>
        <span class="sub">{{ l.sub }}</span>
      </span>
    </button>
  </div>
</template>

<style>
.cerr-v2-scope .nav-stepper {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px 12px;
  margin: 0 0 10px;
  background: linear-gradient(135deg, rgba(0,84,166,.04), rgba(0,84,166,.01));
  border: 1px solid var(--brand-blue-100);
  border-radius: var(--radius-md);
}
.cerr-v2-scope .nav-step {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 9px;
  border-radius: 8px;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  width: 100%;
  position: relative;
  transition: background .14s, color .14s;
  color: var(--text-muted);
}
.cerr-v2-scope .nav-step:hover:not(.is-disabled):not(:disabled) {
  background: rgba(0,84,166,.08);
  color: var(--brand-navy);
}
.cerr-v2-scope .nav-step.is-active {
  background: linear-gradient(135deg, var(--brand-navy), var(--brand-navy-bright));
  color: #fff;
  font-weight: 700;
}
.cerr-v2-scope .nav-step.is-active .sub { color: rgba(255,255,255,.72); }
.cerr-v2-scope .nav-step.is-disabled,
.cerr-v2-scope .nav-step:disabled {
  opacity: 0.45;
  cursor: default;
}
.cerr-v2-scope .nav-step .ico {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: rgba(0,84,166,.08);
  flex-shrink: 0;
}
.cerr-v2-scope .nav-step.is-active .ico { background: rgba(255,255,255,.18); }
.cerr-v2-scope .nav-step .lbl { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.cerr-v2-scope .nav-step .nm {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cerr-v2-scope .nav-step .sub {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-faint);
  letter-spacing: 0.02em;
  margin-top: 1px;
}
</style>
