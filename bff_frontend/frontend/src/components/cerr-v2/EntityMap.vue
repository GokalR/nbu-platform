<script setup>
/* GeoJSON SVG choropleth — port of nbu_platform/geomap.jsx.
 * Equirectangular projection with cos(lat0) aspect correction. */
import { computed, ref } from 'vue'

const props = defineProps({
  geo: { type: Object, default: null },               // GeoJSON FeatureCollection
  width: { type: Number, default: 880 },
  height: { type: Number, default: 440 },
  getKey: { type: Function, required: true },         // f → string id
  getLabel: { type: Function, required: true },       // f → string label (rendered on the polygon)
  getTooltip: { type: Function, default: null },      // f → string for hover tip; falls back to getLabel
  title: { type: String, default: '' },               // optional area name shown inside the map (top-left)
  subtitle: { type: String, default: '' },            // optional secondary line under the title
  highlight: { type: [String, Array], default: null },
  selectable: { type: Function, default: null },      // (k) => bool
  colorize: { type: Function, default: null },        // (f) => fill | null
  showLabels: { type: Boolean, default: true },
  labelMin: { type: Number, default: 28 },
})
const emit = defineEmits(['select'])

const hover = ref(null)
const tip = ref(null)
const wrapRef = ref(null)

// Skip anything that isn't a non-empty Polygon/MultiPolygon. Source data
// occasionally ships districts with empty geometries (e.g. newly-split tumans
// not yet covered by the ADM2 shapefile) — without this guard one bad feature
// would crash bbox()/pathFor() and blank the whole region map.
function isDrawable(geom) {
  if (!geom) return false
  if (geom.type !== 'Polygon' && geom.type !== 'MultiPolygon') return false
  return Array.isArray(geom.coordinates) && geom.coordinates.length > 0
}

function bbox(geo) {
  let xmin = Infinity, ymin = Infinity, xmax = -Infinity, ymax = -Infinity
  function s(c) {
    if (typeof c[0] === 'number') {
      if (c[0] < xmin) xmin = c[0]; if (c[0] > xmax) xmax = c[0]
      if (c[1] < ymin) ymin = c[1]; if (c[1] > ymax) ymax = c[1]
      return
    }
    for (const x of c) s(x)
  }
  for (const f of geo.features) {
    if (!isDrawable(f.geometry)) continue
    s(f.geometry.coordinates)
  }
  return { xmin, ymin, xmax, ymax }
}

const project = computed(() => {
  if (!props.geo) return null
  const b = bbox(props.geo)
  if (!Number.isFinite(b.xmin) || !Number.isFinite(b.ymin)) return null
  // Detect coordinate system: WGS84 lon/lat have |x| ≤ 180; anything bigger is
  // already projected (Web Mercator EPSG:3857), use linear bbox scaling.
  const isProjected = Math.abs(b.xmax) > 360 || Math.abs(b.xmin) > 360
  const k = isProjected ? 1 : Math.cos(((b.ymin + b.ymax) / 2 * Math.PI) / 180)
  const dx = (b.xmax - b.xmin) * k
  const dy = b.ymax - b.ymin
  const pad = 12
  const sx = (props.width - pad * 2) / dx
  const sy = (props.height - pad * 2) / dy
  const s = Math.min(sx, sy)
  const ox = (props.width - dx * s) / 2
  const oy = (props.height - dy * s) / 2
  return ([x, y]) => [ox + (x - b.xmin) * k * s, oy + (b.ymax - y) * s]
})

function pathFor(geom) {
  const proj = project.value
  if (!proj || !isDrawable(geom)) return ''
  const rings = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates
  let d = ''
  for (const poly of rings) {
    for (const ring of poly) {
      ring.forEach(([lo, la], i) => {
        const [x, y] = proj([lo, la])
        d += (i === 0 ? 'M' : 'L') + x.toFixed(1) + ',' + y.toFixed(1)
      })
      d += 'Z'
    }
  }
  return d
}

function centroid(geom) {
  const proj = project.value
  if (!proj || !isDrawable(geom)) return [0, 0]
  const rings = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates
  let bigArea = 0, bigCx = 0, bigCy = 0
  for (const poly of rings) {
    const ring = poly[0]
    let A = 0, cx = 0, cy = 0
    for (let i = 0; i < ring.length - 1; i++) {
      const [x1, y1] = proj(ring[i])
      const [x2, y2] = proj(ring[i + 1])
      const f = x1 * y2 - x2 * y1
      A += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    }
    A /= 2
    if (Math.abs(A) > Math.abs(bigArea)) {
      bigArea = A; bigCx = cx / (6 * A); bigCy = cy / (6 * A)
    }
  }
  return [bigCx, bigCy]
}

const highlightSet = computed(() => {
  if (!props.highlight) return new Set()
  return new Set(Array.isArray(props.highlight) ? props.highlight : [props.highlight])
})

function isSelectable(k) { return props.selectable ? props.selectable(k) : false }

function fillFor(f, isHi) {
  if (isHi) return 'url(#cv2-hi)'
  if (props.colorize) {
    const c = props.colorize(f)
    if (c) return c
  }
  return isSelectable(props.getKey(f)) ? '#e8eef7' : '#f0f1f4'
}

function onEnter(e, f) {
  hover.value = props.getKey(f)
  updateTip(e, f)
}
function onMove(e, f) {
  if (hover.value === props.getKey(f)) updateTip(e, f)
}
function onLeave() { hover.value = null; tip.value = null }
function onClick(f) {
  const k = props.getKey(f)
  if (isSelectable(k)) emit('select', k, f)
}
function updateTip(e, f) {
  if (!wrapRef.value) return
  const r = wrapRef.value.getBoundingClientRect()
  const label = (props.getTooltip || props.getLabel)(f)
  tip.value = { x: e.clientX - r.left, y: e.clientY - r.top, label }
}

function labelFor(f) {
  if (!project.value) return null
  if (!isDrawable(f.geometry)) return null
  const [cx, cy] = centroid(f.geometry)
  const isHi = highlightSet.value.has(props.getKey(f))
  // Cheap "too small to label" heuristic: bbox of this single feature in screen px.
  const inner = { features: [f] }
  const b = bbox(inner)
  const w = (project.value([b.xmax, b.ymin])[0] - project.value([b.xmin, b.ymin])[0]) || 0
  if (w < props.labelMin && !isHi) return null
  return { cx, cy, isHi, label: props.getLabel(f) }
}
</script>

<template>
  <div class="geomap-wrap" ref="wrapRef">
    <div v-if="!geo || !project" class="geomap-placeholder" :style="{ height: `${height}px` }">
      <span>Загрузка карты…</span>
    </div>
    <svg
      v-else
      class="geomap"
      :viewBox="`0 0 ${width} ${height}`"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient id="cv2-hi" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#003D7C" />
          <stop offset="100%" stop-color="#0054A6" />
        </linearGradient>
        <filter id="cv2-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#001b3d" flood-opacity="0.32" />
        </filter>
      </defs>
      <template v-for="(f, i) in geo.features" :key="`p-${getKey(f)}-${i}`">
        <path
          v-if="isDrawable(f.geometry)"
          :d="pathFor(f.geometry)"
          :fill="fillFor(f, highlightSet.has(getKey(f)))"
          :stroke="highlightSet.has(getKey(f)) ? '#001b3d' : (hover === getKey(f) ? '#0054A6' : '#ffffff')"
          :stroke-width="highlightSet.has(getKey(f)) ? 1.5 : (hover === getKey(f) ? 2 : 1.5)"
          stroke-linejoin="round"
          :filter="highlightSet.has(getKey(f)) ? 'url(#cv2-shadow)' : null"
          :style="{
            cursor: isSelectable(getKey(f)) ? 'pointer' : 'default',
            opacity: !isSelectable(getKey(f)) && !highlightSet.has(getKey(f)) ? 0.55 : 1,
            transition: 'fill .15s, stroke .15s',
          }"
          @mouseenter="onEnter($event, f)"
          @mousemove="onMove($event, f)"
          @mouseleave="onLeave"
          @click="onClick(f)"
        />
      </template>
      <template v-if="showLabels">
        <template v-for="(f, i) in geo.features" :key="`l-${getKey(f)}-${i}`">
          <text
            v-if="labelFor(f)"
            :x="labelFor(f).cx"
            :y="labelFor(f).cy"
            text-anchor="middle"
            dominant-baseline="middle"
            :font-size="labelFor(f).isHi ? 10 : 8.5"
            :font-weight="labelFor(f).isHi ? 700 : 600"
            :fill="labelFor(f).isHi ? '#fff' : '#3f4654'"
            :style="{
              pointerEvents: 'none',
              textShadow: labelFor(f).isHi ? 'none' : '0 1px 0 #fff, 0 0 3px #fff',
            }"
          >{{ labelFor(f).label }}</text>
        </template>
      </template>
    </svg>
    <div v-if="title" class="geomap-title">
      <div class="geomap-title-name">{{ title }}</div>
      <div v-if="subtitle" class="geomap-title-sub">{{ subtitle }}</div>
    </div>
    <div
      v-if="tip"
      class="geomap-tip"
      :style="{ left: `${tip.x + 14}px`, top: `${tip.y - 18}px` }"
    >{{ tip.label }}</div>
  </div>
</template>

<style>
.cerr-v2-scope .geomap-wrap { position: relative; }
.cerr-v2-scope .geomap-title {
  position: absolute;
  top: 14px;
  left: 16px;
  pointer-events: none;
  z-index: 2;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(0, 27, 61, 0.08);
  border-radius: 10px;
  padding: 8px 14px;
  box-shadow: 0 4px 12px -4px rgba(0, 27, 61, 0.12);
}
.cerr-v2-scope .geomap-title-name {
  font-size: 16px;
  font-weight: 800;
  letter-spacing: -0.018em;
  color: var(--brand-navy-deep);
  line-height: 1.1;
}
.cerr-v2-scope .geomap-title-sub {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-soft);
  letter-spacing: 0.04em;
  margin-top: 2px;
}
</style>
