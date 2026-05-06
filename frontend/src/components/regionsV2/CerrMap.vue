<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const props = defineProps({
  // GeoJSON FeatureCollection (WGS84 lon/lat) returned by /api/cerr/districts/:code/geo
  geo: { type: Object, default: null },
  // Mahalla summary list, used to color polygons by rating_score.
  // Match by feature.properties.stir (or id).
  mahallas: { type: Array, default: () => [] },
  // Stir of the polygon to outline (driven by hover or selection in the table).
  highlightedStir: { type: String, default: null },
})
const emit = defineEmits(['select', 'hover'])

const containerRef = ref(null)
let map = null
let popup = null

// Free, no-key OSM raster style. Good enough for an internal dashboard.
const STYLE = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [{ id: 'osm', type: 'raster', source: 'osm', minzoom: 0, maxzoom: 19 }],
}

// Build a stir -> rating lookup so we can attach rating to each feature
// before MapLibre paints. This drives the data-driven fill colour.
const stirRatings = computed(() => {
  const m = new Map()
  for (const it of props.mahallas) {
    if (it.stir != null) m.set(String(it.stir), it.rating_score)
  }
  return m
})

// Decorate each feature with rating + a normalised score in [0,1] (low=better).
function decorate(fc) {
  if (!fc || !Array.isArray(fc.features)) return null
  const ratings = stirRatings.value
  const vals = []
  const features = fc.features.map((f) => {
    const stir = String(f?.properties?.stir ?? f?.properties?.id ?? f?.id ?? '')
    const rating = ratings.get(stir) ?? null
    if (rating != null) vals.push(rating)
    return {
      ...f,
      id: stir || undefined, // enables feature-state for hover/highlight
      properties: { ...(f.properties || {}), stir, rating_score: rating },
    }
  })
  let min = Math.min(...vals)
  let max = Math.max(...vals)
  if (!isFinite(min) || !isFinite(max) || min === max) {
    min = 0
    max = 1
  }
  for (const f of features) {
    const r = f.properties.rating_score
    f.properties.rating_norm = r == null ? null : (r - min) / (max - min)
  }
  return { type: 'FeatureCollection', features }
}

const decorated = computed(() => decorate(props.geo))

function fitToFeatures(fc) {
  if (!map || !fc?.features?.length) return
  const b = new maplibregl.LngLatBounds()
  let touched = false
  const visit = (coords) => {
    if (typeof coords[0] === 'number') {
      b.extend(coords)
      touched = true
      return
    }
    coords.forEach(visit)
  }
  for (const f of fc.features) {
    const c = f?.geometry?.coordinates
    if (c) visit(c)
  }
  if (touched) map.fitBounds(b, { padding: 30, duration: 600 })
}

function setData(fc) {
  if (!map) return
  const src = map.getSource('mahallas')
  if (src) src.setData(fc || { type: 'FeatureCollection', features: [] })
}

function attachLayers() {
  if (!map) return
  if (map.getLayer('mahallas-fill')) return // idempotent

  map.addSource('mahallas', {
    type: 'geojson',
    data: decorated.value || { type: 'FeatureCollection', features: [] },
    promoteId: 'stir',
  })

  // Fill — green when rating_norm is low (better), red when high.
  // null ratings get neutral grey.
  map.addLayer({
    id: 'mahallas-fill',
    type: 'fill',
    source: 'mahallas',
    paint: {
      'fill-color': [
        'case',
        ['==', ['get', 'rating_norm'], null], '#cbd5e1',
        [
          'interpolate', ['linear'], ['get', 'rating_norm'],
          0.0, '#10b981',
          0.5, '#f59e0b',
          1.0, '#ef4444',
        ],
      ],
      'fill-opacity': [
        'case',
        ['boolean', ['feature-state', 'hover'], false], 0.85,
        0.55,
      ],
    },
  })

  map.addLayer({
    id: 'mahallas-outline',
    type: 'line',
    source: 'mahallas',
    paint: {
      'line-color': [
        'case',
        ['boolean', ['feature-state', 'highlight'], false], '#1d4ed8',
        '#475569',
      ],
      'line-width': [
        'case',
        ['boolean', ['feature-state', 'highlight'], false], 3,
        ['boolean', ['feature-state', 'hover'], false], 2,
        0.6,
      ],
    },
  })

  let hoveredId = null
  map.on('mousemove', 'mahallas-fill', (e) => {
    if (!e.features?.length) return
    const id = e.features[0].id
    if (hoveredId === id) return
    if (hoveredId != null) map.setFeatureState({ source: 'mahallas', id: hoveredId }, { hover: false })
    hoveredId = id
    map.setFeatureState({ source: 'mahallas', id }, { hover: true })
    map.getCanvas().style.cursor = 'pointer'
    emit('hover', String(id))

    // Tooltip
    const f = e.features[0]
    const name = f.properties?.name || f.properties?.NAME || `STIR ${id}`
    const rating = f.properties?.rating_score
    const html = `
      <div class="text-xs">
        <div class="font-bold text-slate-900">${escapeHtml(name)}</div>
        ${rating != null ? `<div class="text-slate-600 mt-0.5">Рейтинг: ${rating}</div>` : ''}
      </div>`
    if (!popup) popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 6, className: 'cerr-popup' })
    popup.setLngLat(e.lngLat).setHTML(html).addTo(map)
  })

  map.on('mouseleave', 'mahallas-fill', () => {
    if (hoveredId != null) map.setFeatureState({ source: 'mahallas', id: hoveredId }, { hover: false })
    hoveredId = null
    map.getCanvas().style.cursor = ''
    if (popup) popup.remove()
    emit('hover', null)
  })

  map.on('click', 'mahallas-fill', (e) => {
    if (!e.features?.length) return
    const stir = String(e.features[0].id ?? e.features[0].properties?.stir ?? '')
    if (stir) emit('select', stir)
  })
}

let prevHighlight = null
function applyHighlight(stir) {
  if (!map) return
  if (prevHighlight != null) {
    try { map.setFeatureState({ source: 'mahallas', id: prevHighlight }, { highlight: false }) } catch {}
  }
  if (stir != null) {
    try { map.setFeatureState({ source: 'mahallas', id: stir }, { highlight: true }) } catch {}
  }
  prevHighlight = stir
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  )
}

onMounted(() => {
  map = new maplibregl.Map({
    container: containerRef.value,
    style: STYLE,
    center: [64.5, 41.5], // Uzbekistan-ish centre — fitBounds replaces this once data loads
    zoom: 5.5,
    attributionControl: { compact: true },
  })
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
  map.on('load', () => {
    attachLayers()
    if (decorated.value) {
      setData(decorated.value)
      fitToFeatures(decorated.value)
    }
  })
})

onBeforeUnmount(() => {
  if (popup) { popup.remove(); popup = null }
  if (map) { map.remove(); map = null }
})

// React to data changes after mount.
watch(decorated, (fc) => {
  if (!map) return
  if (!map.isStyleLoaded()) {
    map.once('load', () => { setData(fc); fitToFeatures(fc) })
    return
  }
  setData(fc)
  if (fc?.features?.length) fitToFeatures(fc)
})

watch(() => props.highlightedStir, (s) => applyHighlight(s))
</script>

<template>
  <div class="relative rounded-xl overflow-hidden border border-slate-200/70 bg-slate-100">
    <div ref="containerRef" class="w-full h-full min-h-[420px]" />
  </div>
</template>

<style>
.cerr-popup .maplibregl-popup-content {
  border-radius: 10px;
  padding: 8px 10px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.4);
}
</style>
