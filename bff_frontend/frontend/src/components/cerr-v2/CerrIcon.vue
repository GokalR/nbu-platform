<script setup>
/* Inline SVG icon set ported from nbu_platform/components.jsx (subset).
 * Stroke-based, color via currentColor. */
const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 18 },
  strokeWidth: { type: [Number, String], default: 1.8 },
})

const PATHS = {
  home2: 'M3 12L12 4l9 8 M5 10v10h14V10 M9 20v-6h6v6',
  chart: 'M4 20V8 M10 20V4 M16 20v-8 M22 20H2',
  globe: 'M3 12h18 M12 3a14 14 0 010 18 M12 3a14 14 0 000 18',
  map: 'M9 2L3 4v18l6-2 6 2 6-2V2l-6 2-6-2z M9 2v18 M15 4v18',
  brain: 'M12 4a3 3 0 00-3 3v0a3 3 0 00-3 3v2a3 3 0 003 3v0a3 3 0 003 3 3 3 0 003-3 3 3 0 003-3v-2a3 3 0 00-3-3 3 3 0 00-3-3z',
  bot: 'M12 2v4 M8 12v.01 M16 12v.01 M9 17h6',
  book: 'M4 4v16a2 2 0 002 2h12V2H6a2 2 0 00-2 2z M8 6h8 M8 10h8 M8 14h6',
  shield: 'M12 2l8 3v7c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z',
  file: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M9 13h6 M9 17h4',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  arrowD: 'M12 5v14 M6 13l6 6 6-6',
  arrowU: 'M12 19V5 M6 11l6-6 6 6',
  search: 'M21 21l-4.3-4.3',
  close: 'M18 6L6 18 M6 6l12 12',
  pin: 'M12 2a7 7 0 00-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 00-7-7z',
  factory: 'M2 20h20V10l-6 4V8l-6 4V4H4v16z M6 20v-4 M10 20v-4 M14 20v-4 M18 20v-4',
  tractor: 'M8 14h8l2-7h-5l-2 4H8a2 2 0 00-2 2v3',
  coin: 'M9 12h6 M12 9v6',
  users: 'M3 20c0-3 3-5 6-5s6 2 6 5 M15 20c0-2 2-4 4-4s2.5 1 2.5 3',
  truck: 'M3 17V6h11v11 M14 9h5l3 4v4h-8',
  bus: 'M4 12h16 M8 5v3 M16 5v3',
  tools: 'M14 6l4 4-9 9-4 1 1-4 9-9z M14 6l-3-3 3-3 3 3-3 3z',
  store: 'M3 8h18l-1 4H4L3 8z M5 8V6h14v2 M5 12v8h14v-8',
  spark: 'M12 2l2 7h7l-5.5 4 2 7L12 16l-5.5 4 2-7L3 9h7z',
  leaf: 'M11 20A8 8 0 003 12c0-5 4-9 11-9 0 5-1 13-3 17z',
  award: 'M9 14l-2 7 5-3 5 3-2-7',
  check: 'M5 12l5 5 9-9',
  warn: 'M12 3l10 18H2L12 3z M12 9v5 M12 17v.01',
  bolt: 'M13 2L3 14h7l-1 8 10-12h-7l1-8z',
  target: '',
  layers: 'M12 2L2 7l10 5 10-5-10-5z M2 12l10 5 10-5 M2 17l10 5 10-5',
  pulse: 'M3 12h4l2-8 4 16 2-8h6',
  info: 'M12 8v.01 M12 11v5',
  help: 'M9.5 9a2.5 2.5 0 015 0c0 1.5-2.5 2-2.5 4 M12 17v.01',
  grid: '',
  road: 'M5 21l3-18 M19 21l-3-18 M12 4v3 M12 11v3 M12 18v3',
  drop: 'M12 3l5 7a6 6 0 11-10 0l5-7z',
  school: 'M2 9l10-5 10 5-10 5L2 9z M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5 M22 9v5',
  hospital: 'M12 10v6 M9 13h6 M9 2h6v4H9z',
  docs: 'M9 4h9v16H6V7l3-3z M9 4v3H6 M11 11h6 M11 15h6',
  apple: 'M12 7s2-4 5-4 M12 7c0-2-2-4-2-4',
  cow: '',
  mosque: 'M3 21V10h18v11 M12 4v6 M9 7h6 M3 13h18',
}

const CIRCLES_RECTS = {
  globe: [{ tag: 'circle', attrs: { cx: 12, cy: 12, r: 9 } }],
  bot: [{ tag: 'rect', attrs: { x: 4, y: 6, width: 16, height: 14, rx: 3 } }],
  search: [{ tag: 'circle', attrs: { cx: 11, cy: 11, r: 7 } }],
  pin: [{ tag: 'circle', attrs: { cx: 12, cy: 9, r: 2.5 } }],
  tractor: [{ tag: 'circle', attrs: { cx: 6, cy: 17, r: 3 } }, { tag: 'circle', attrs: { cx: 18, cy: 18, r: 2 } }],
  coin: [{ tag: 'circle', attrs: { cx: 12, cy: 12, r: 9 } }],
  users: [{ tag: 'circle', attrs: { cx: 9, cy: 8, r: 3 } }, { tag: 'circle', attrs: { cx: 17, cy: 8, r: 2.5 } }],
  truck: [{ tag: 'circle', attrs: { cx: 7, cy: 18, r: 2 } }, { tag: 'circle', attrs: { cx: 17, cy: 18, r: 2 } }],
  bus: [{ tag: 'rect', attrs: { x: 4, y: 5, width: 16, height: 13, rx: 2 } }, { tag: 'circle', attrs: { cx: 8, cy: 18, r: 1.5 } }, { tag: 'circle', attrs: { cx: 16, cy: 18, r: 1.5 } }],
  award: [{ tag: 'circle', attrs: { cx: 12, cy: 9, r: 6 } }],
  target: [{ tag: 'circle', attrs: { cx: 12, cy: 12, r: 9 } }, { tag: 'circle', attrs: { cx: 12, cy: 12, r: 5 } }, { tag: 'circle', attrs: { cx: 12, cy: 12, r: 1.5 } }],
  grid: [{ tag: 'rect', attrs: { x: 3, y: 3, width: 7, height: 7 } }, { tag: 'rect', attrs: { x: 14, y: 3, width: 7, height: 7 } }, { tag: 'rect', attrs: { x: 3, y: 14, width: 7, height: 7 } }, { tag: 'rect', attrs: { x: 14, y: 14, width: 7, height: 7 } }],
  info: [{ tag: 'circle', attrs: { cx: 12, cy: 12, r: 9 } }],
  help: [{ tag: 'circle', attrs: { cx: 12, cy: 12, r: 9 } }],
  hospital: [{ tag: 'rect', attrs: { x: 4, y: 6, width: 16, height: 14, rx: 2 } }],
  apple: [{ tag: 'circle', attrs: { cx: 12, cy: 14, r: 7 } }],
  cow: [{ tag: 'circle', attrs: { cx: 12, cy: 12, r: 8 } }, { tag: 'circle', attrs: { cx: 9, cy: 11, r: 1.2 } }, { tag: 'circle', attrs: { cx: 15, cy: 11, r: 1.2 } }],
}
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <component
      v-for="(shape, i) in CIRCLES_RECTS[name] || []"
      :key="`s-${i}`"
      :is="shape.tag"
      v-bind="shape.attrs"
    />
    <path v-if="PATHS[name]" :d="PATHS[name]" />
  </svg>
</template>
