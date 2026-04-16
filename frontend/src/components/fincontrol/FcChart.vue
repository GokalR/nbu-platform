<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import {
  Chart,
  LineController,
  BarController,
  DoughnutController,
  PieController,
  LineElement,
  BarElement,
  PointElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

Chart.register(
  LineController,
  BarController,
  DoughnutController,
  PieController,
  LineElement,
  BarElement,
  PointElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Filler,
)

const props = defineProps({
  type: { type: String, required: true },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
  height: { type: [Number, String], default: 240 },
})

const canvas = ref(null)
let chart = null

function build() {
  if (!canvas.value) return
  if (chart) {
    chart.destroy()
    chart = null
  }
  chart = new Chart(canvas.value, {
    type: props.type,
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...props.options,
    },
  })
}

onMounted(build)
watch(() => [props.data, props.options, props.type], build, { deep: true })
onBeforeUnmount(() => {
  if (chart) chart.destroy()
})
</script>

<template>
  <div class="fc-chart-wrap" :style="{ height: typeof height === 'number' ? `${height}px` : height }">
    <canvas ref="canvas"></canvas>
  </div>
</template>
