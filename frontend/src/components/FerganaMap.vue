<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { districtByKey } from '@/data/districts'

const props = defineProps({
  modelValue: { type: String, default: null },
})
const emit = defineEmits(['update:modelValue', 'select'])
const { t } = useI18n()

const features = ref([])
const hovered = ref(null)
const error = ref(null)

// Fergana valley bounds (with padding) — from geoBoundaries ADM2 extract.
const VIEW_W = 1000
const VIEW_H = 650
const LON_MIN = 70.2
const LON_MAX = 72.3
const LAT_MIN = 39.80
const LAT_MAX = 40.85

function projX(lon) {
  return ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * VIEW_W
}
function projY(lat) {
  return ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * VIEW_H
}
function ringToPath(ring) {
  return (
    ring
      .map(([lon, lat], i) => `${i === 0 ? 'M' : 'L'} ${projX(lon).toFixed(2)} ${projY(lat).toFixed(2)}`)
      .join(' ') + ' Z'
  )
}
function geomToPath(geom) {
  if (geom.type === 'Polygon') return geom.coordinates.map(ringToPath).join(' ')
  if (geom.type === 'MultiPolygon') return geom.coordinates.flat().map(ringToPath).join(' ')
  return ''
}
function projectRings(rings) {
  return rings.map((ring) => ring.map(([lon, lat]) => [projX(lon), projY(lat)]))
}
function ringArea(ring) {
  let a = 0
  for (let i = 0, n = ring.length, j = n - 1; i < n; j = i++) {
    a += ring[j][0] * ring[i][1] - ring[i][0] * ring[j][1]
  }
  return Math.abs(a) * 0.5
}
function pointInPolygon(px, py, rings) {
  let inside = false
  for (const ring of rings) {
    for (let i = 0, n = ring.length, j = n - 1; i < n; j = i++) {
      const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1]
      if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) {
        inside = !inside
      }
    }
  }
  return inside
}
function distToEdges(px, py, rings) {
  let minSq = Infinity
  for (const ring of rings) {
    for (let i = 0, n = ring.length, j = n - 1; i < n; j = i++) {
      const ax = ring[j][0], ay = ring[j][1], bx = ring[i][0], by = ring[i][1]
      const dx = bx - ax, dy = by - ay
      let x = ax, y = ay
      if (dx !== 0 || dy !== 0) {
        const tt = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        if (tt > 1) { x = bx; y = by }
        else if (tt > 0) { x = ax + dx * tt; y = ay + dy * tt }
      }
      const ex = px - x, ey = py - y
      const sq = ex * ex + ey * ey
      if (sq < minSq) minSq = sq
    }
  }
  return Math.sqrt(minSq)
}
function visualCenter(rings) {
  const outer = rings[0]
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  for (const [x, y] of outer) {
    if (x < minX) minX = x; if (y < minY) minY = y
    if (x > maxX) maxX = x; if (y > maxY) maxY = y
  }
  const N = 48
  const cellW = (maxX - minX) / N, cellH = (maxY - minY) / N
  let best = { x: (minX + maxX) / 2, y: (minY + maxY) / 2, d: -Infinity }
  for (let i = 0; i <= N; i++) {
    for (let j = 0; j <= N; j++) {
      const x = minX + i * cellW, y = minY + j * cellH
      if (!pointInPolygon(x, y, rings)) continue
      const d = distToEdges(x, y, rings)
      if (d > best.d) best = { x, y, d }
    }
  }
  const M = 10
  for (let i = -M; i <= M; i++) {
    for (let j = -M; j <= M; j++) {
      const x = best.x + (i / M) * cellW, y = best.y + (j / M) * cellH
      if (!pointInPolygon(x, y, rings)) continue
      const d = distToEdges(x, y, rings)
      if (d > best.d) best = { x, y, d }
    }
  }
  return { x: best.x, y: best.y }
}
function centroid(geom) {
  const polygons = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates
  let bestRings = null, bestArea = -1
  for (const poly of polygons) {
    const rings = projectRings(poly)
    const a = ringArea(rings[0])
    if (a > bestArea) { bestArea = a; bestRings = rings }
  }
  return visualCenter(bestRings)
}

const paths = computed(() =>
  features.value.map((f) => ({
    key: f.properties.key,
    kind: f.properties.kind,
    d: geomToPath(f.geometry),
    centroid: centroid(f.geometry),
  })),
)

// Color palette — cities (4) stand out; districts share a tonal scale.
const CITY_FILL = '#003D7C'
const CITY_FILL_SEL = '#001B3D'
const DIST_FILL = '#7FB5E6'
const DIST_FILL_SEL = '#0054A6'

function fillFor(p) {
  const isCity = p.kind === 'city'
  const base = isCity ? CITY_FILL : DIST_FILL
  const selected = isCity ? CITY_FILL_SEL : DIST_FILL_SEL
  if (props.modelValue === p.key) return selected
  if (hovered.value === p.key) return isCity ? CITY_FILL_SEL : DIST_FILL_SEL
  return base
}
function fillOpacityFor(key) {
  if (props.modelValue === key) return 1
  if (hovered.value === key) return 0.95
  return props.modelValue ? 0.4 : 0.8
}
function strokeWidthFor(key) {
  return props.modelValue === key ? 2.5 : 1.2
}
function labelFor(key) {
  return t(`districtsShort.${key}`, key)
}
function onClick(key) {
  emit('update:modelValue', props.modelValue === key ? null : key)
  emit('select', key)
}

onMounted(async () => {
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}fergana-districts.geojson`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()
    features.value = json.features
  } catch (e) {
    error.value = e.message
    console.error('Failed to load fergana geojson', e)
  }
})

const tooltipPos = computed(() => {
  if (!hovered.value) return null
  const p = paths.value.find((x) => x.key === hovered.value)
  return p?.centroid
})
const tooltipDistrict = computed(() => (hovered.value ? districtByKey[hovered.value] : null))
</script>

<template>
  <figure
    class="bg-surface-container-lowest rounded-xl p-4 lg:p-6 relative shadow-sm border border-outline-variant/20"
    :aria-label="t('district.mapTitle')"
  >
    <div v-if="error" class="text-error text-sm p-4">{{ error }}</div>

    <svg
      :viewBox="`0 0 ${VIEW_W} ${VIEW_H}`"
      class="w-full h-auto select-none mx-auto max-w-5xl"
      role="img"
      :aria-label="t('district.mapTitle')"
    >
      <defs>
        <filter id="fergana-shadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.3" />
        </filter>
      </defs>

      <g>
        <path
          v-for="p in paths"
          :key="p.key"
          :d="p.d"
          class="transition-[fill,stroke-width] duration-200 cursor-pointer focus:outline-none"
          :fill="fillFor(p)"
          :fill-opacity="fillOpacityFor(p.key)"
          stroke="#ffffff"
          :stroke-width="strokeWidthFor(p.key)"
          stroke-linejoin="round"
          :style="modelValue === p.key ? 'filter: url(#fergana-shadow)' : ''"
          @mouseenter="hovered = p.key"
          @mouseleave="hovered = null"
          @click="onClick(p.key)"
          @keyup.enter="onClick(p.key)"
          tabindex="0"
          :aria-label="t(`districtsList.${p.key}`)"
          :aria-pressed="modelValue === p.key"
          role="button"
        />
      </g>

      <g class="map-labels" pointer-events="none">
        <text
          v-for="p in paths"
          :key="`lab-${p.key}`"
          :x="p.centroid.x"
          :y="p.centroid.y"
          :font-size="p.kind === 'city' ? 15 : 12"
          :font-weight="modelValue === p.key ? 900 : p.kind === 'city' ? 800 : 600"
          text-anchor="middle"
          dominant-baseline="middle"
          :fill="p.kind === 'city' ? '#ffffff' : '#0b1a33'"
          stroke="#ffffff"
          :stroke-width="p.kind === 'city' ? 0 : 3"
          stroke-linejoin="round"
          paint-order="stroke fill"
        >
          {{ labelFor(p.key) }}
        </text>
      </g>
    </svg>

    <transition name="fade">
      <div
        v-if="hovered && tooltipPos && tooltipDistrict"
        class="pointer-events-none absolute bg-white/95 backdrop-blur-md px-3 py-2 rounded-lg shadow-lg border-l-4 border-primary text-xs text-on-surface"
        :style="{
          left: `calc(${(tooltipPos.x / VIEW_W) * 100}% + 8px)`,
          top: `calc(${(tooltipPos.y / VIEW_H) * 100}% + 8px)`,
        }"
      >
        <div class="font-bold">{{ t(`districtsList.${hovered}`) }}</div>
        <div class="text-[10px] text-on-surface-variant mt-0.5">
          {{ tooltipDistrict.population }} тыс · {{ tooltipDistrict.area }} км²
        </div>
      </div>
    </transition>

    <figcaption class="mt-3 text-xs text-on-surface-variant text-center flex items-center justify-center gap-4 flex-wrap">
      <span class="inline-flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-sm" :style="{ background: CITY_FILL }"></span>
        {{ t('district.listCities') }}
      </span>
      <span class="inline-flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-sm" :style="{ background: DIST_FILL }"></span>
        {{ t('district.listDistricts') }}
      </span>
      <span>· {{ t('district.mapHint') }}</span>
    </figcaption>
  </figure>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
