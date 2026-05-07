<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { regionColors } from '@/data/regionColors'

const props = defineProps({
  modelValue: { type: String, default: null },
  colored: { type: Boolean, default: true }, // toggle distinct colors
})
const emit = defineEmits(['update:modelValue', 'select'])
const { t } = useI18n()

const features = ref([])
const hovered = ref(null)
const error = ref(null)

const VIEW_W = 1000
const VIEW_H = 500
const LON_MIN = 55.5
const LON_MAX = 73.5
const LAT_MIN = 36.5
const LAT_MAX = 45.7

function projX(lon) {
  return ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * VIEW_W
}
function projY(lat) {
  return ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * VIEW_H
}
function ringToPath(ring) {
  return (
    ring
      .map(
        ([lon, lat], i) =>
          `${i === 0 ? 'M' : 'L'} ${projX(lon).toFixed(2)} ${projY(lat).toFixed(2)}`,
      )
      .join(' ') + ' Z'
  )
}
function geomToPath(geom) {
  if (geom.type === 'Polygon') return geom.coordinates.map(ringToPath).join(' ')
  if (geom.type === 'MultiPolygon')
    return geom.coordinates.flat().map(ringToPath).join(' ')
  return ''
}
// Project a polygon (array of rings of [lon, lat]) to SVG coords.
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
      const xi = ring[i][0]
      const yi = ring[i][1]
      const xj = ring[j][0]
      const yj = ring[j][1]
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
      const ax = ring[j][0]
      const ay = ring[j][1]
      const bx = ring[i][0]
      const by = ring[i][1]
      const dx = bx - ax
      const dy = by - ay
      let x = ax
      let y = ay
      if (dx !== 0 || dy !== 0) {
        const t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        if (t > 1) {
          x = bx
          y = by
        } else if (t > 0) {
          x = ax + dx * t
          y = ay + dy * t
        }
      }
      const ex = px - x
      const ey = py - y
      const sq = ex * ex + ey * ey
      if (sq < minSq) minSq = sq
    }
  }
  return Math.sqrt(minSq)
}

// Pole of inaccessibility: grid sample, pick interior point farthest from any edge,
// then refine locally. Good for concave/irregular shapes where centroid lands outside.
function visualCenter(rings) {
  const outer = rings[0]
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const [x, y] of outer) {
    if (x < minX) minX = x
    if (y < minY) minY = y
    if (x > maxX) maxX = x
    if (y > maxY) maxY = y
  }
  const N = 48
  const cellW = (maxX - minX) / N
  const cellH = (maxY - minY) / N
  let best = { x: (minX + maxX) / 2, y: (minY + maxY) / 2, d: -Infinity }
  for (let i = 0; i <= N; i++) {
    for (let j = 0; j <= N; j++) {
      const x = minX + i * cellW
      const y = minY + j * cellH
      if (!pointInPolygon(x, y, rings)) continue
      const d = distToEdges(x, y, rings)
      if (d > best.d) best = { x, y, d }
    }
  }
  // Refine with a finer local grid around the best point.
  const rX = cellW
  const rY = cellH
  const M = 10
  for (let i = -M; i <= M; i++) {
    for (let j = -M; j <= M; j++) {
      const x = best.x + (i / M) * rX
      const y = best.y + (j / M) * rY
      if (!pointInPolygon(x, y, rings)) continue
      const d = distToEdges(x, y, rings)
      if (d > best.d) best = { x, y, d }
    }
  }
  return { x: best.x, y: best.y }
}

function centroid(geom) {
  const polygons = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates
  // Project each polygon, pick the one with the largest outer-ring area.
  let bestRings = null
  let bestArea = -1
  for (const poly of polygons) {
    const rings = projectRings(poly)
    const a = ringArea(rings[0])
    if (a > bestArea) {
      bestArea = a
      bestRings = rings
    }
  }
  return visualCenter(bestRings)
}

const paths = computed(() =>
  features.value.map((f) => ({
    key: f.properties.key,
    d: geomToPath(f.geometry),
    centroid: centroid(f.geometry),
  })),
)

function fillFor(key) {
  const palette = regionColors[key] || { base: '#e6e8ea', hover: '#d8dadc', selected: '#003d7c' }
  if (props.modelValue === key) return palette.selected
  if (hovered.value === key) return palette.hover
  return props.colored ? palette.base : '#e6e8ea'
}

function fillOpacityFor(key) {
  if (props.modelValue === key) return 1
  if (hovered.value === key) return 0.85
  // Dim non-selected regions; stronger dim when a different region is active.
  return props.modelValue ? 0.35 : 0.55
}

function strokeFor(key) {
  if (props.modelValue === key) return '#ffffff'
  return '#ffffff'
}

// Manual nudges for labels that don't sit nicely at the polygon centroid
// (very small regions, irregular shapes). Values are SVG units to add.
const LABEL_OFFSETS = {
  tashkent_city: { dx: 0, dy: -14 },
  sirdaryo: { dx: 0, dy: 4 },
}
function labelPos(region) {
  const off = LABEL_OFFSETS[region.key] || { dx: 0, dy: 0 }
  return { x: region.centroid.x + off.dx, y: region.centroid.y + off.dy }
}

function strokeWidthFor(key) {
  return props.modelValue === key ? 2.5 : 1
}

function onClick(key) {
  emit('update:modelValue', props.modelValue === key ? null : key)
  emit('select', key)
}

onMounted(async () => {
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}uzbekistan-regions.geojson`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()
    features.value = json.features
  } catch (e) {
    error.value = e.message
    console.error('Failed to load regions geojson', e)
  }
})

const tooltipPos = computed(() => {
  if (!hovered.value) return null
  const p = paths.value.find((x) => x.key === hovered.value)
  return p?.centroid
})
</script>

<template>
  <figure
    class="bg-surface-container-low rounded-xl p-4 lg:p-6 relative shadow-sm"
    :aria-label="t('home.map.aria')"
  >
    <div v-if="error" class="text-error text-sm p-4">{{ error }}</div>

    <svg
      :viewBox="`0 0 ${VIEW_W} ${VIEW_H}`"
      class="w-full h-auto select-none"
      role="img"
      :aria-label="t('home.map.aria')"
    >
      <defs>
        <filter id="region-shadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.3" />
        </filter>
      </defs>

      <g>
        <path
          v-for="region in paths"
          :key="region.key"
          :d="region.d"
          class="transition-[fill,stroke-width] duration-200 cursor-pointer focus:outline-none"
          :fill="fillFor(region.key)"
          :fill-opacity="fillOpacityFor(region.key)"
          :stroke="strokeFor(region.key)"
          :stroke-width="strokeWidthFor(region.key)"
          stroke-linejoin="round"
          :style="modelValue === region.key ? 'filter: url(#region-shadow)' : ''"
          @mouseenter="hovered = region.key"
          @mouseleave="hovered = null"
          @click="onClick(region.key)"
          @keyup.enter="onClick(region.key)"
          tabindex="0"
          :aria-label="t(`regions.${region.key}`)"
          :aria-pressed="modelValue === region.key"
          role="button"
        />
      </g>

      <!-- Tashkent city marker (polygon is tiny) -->
      <g v-for="region in paths" :key="`mark-${region.key}`">
        <circle
          v-if="region.key === 'tashkent_city'"
          :cx="region.centroid.x"
          :cy="region.centroid.y"
          r="5"
          :fill="modelValue === 'tashkent_city' ? '#ffffff' : '#c62828'"
          stroke="#c62828"
          stroke-width="2"
          pointer-events="none"
        />
      </g>

      <!-- Region name labels -->
      <g class="map-labels" pointer-events="none">
        <text
          v-for="region in paths"
          :key="`label-${region.key}`"
          :x="labelPos(region).x"
          :y="labelPos(region).y"
          :font-size="region.key === 'tashkent_city' || region.key === 'sirdaryo' ? 11 : 13"
          :font-weight="modelValue === region.key ? 800 : 600"
          text-anchor="middle"
          dominant-baseline="middle"
          :fill="modelValue === region.key ? '#ffffff' : '#1f2937'"
          stroke="#ffffff"
          stroke-width="3"
          stroke-linejoin="round"
          paint-order="stroke fill"
          :style="modelValue === region.key ? 'stroke: #003d7c' : ''"
        >
          {{ t(`regionsShort.${region.key}`) }}
        </text>
      </g>
    </svg>

    <!-- Hover tooltip -->
    <transition name="fade">
      <div
        v-if="hovered && tooltipPos"
        class="pointer-events-none absolute bg-white/95 backdrop-blur-md px-3 py-2 rounded-lg shadow-lg border-l-4 border-primary text-xs font-bold text-on-surface"
        :style="{
          left: `calc(${(tooltipPos.x / VIEW_W) * 100}% + 8px)`,
          top: `calc(${(tooltipPos.y / VIEW_H) * 100}% + 8px)`,
        }"
      >
        {{ t(`regions.${hovered}`) }}
      </div>
    </transition>

    <!-- Overlay slot (e.g., selected region info shown in empty map area) -->
    <slot name="overlay" />

    <figcaption class="mt-3 text-xs text-on-surface-variant text-center">
      {{ t('home.map.hint') }}
    </figcaption>
  </figure>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
