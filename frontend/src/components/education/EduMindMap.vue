<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  root: { type: Object, required: true },
})

const selectedNode = ref(null)
const nodes = ref([])
const edges = ref([])
const canvasWidth = ref(900)
const canvasHeight = ref(600)

const X_GAP = 260
const Y_GAP_BRANCH = 120
const Y_GAP_LEAF = 48
const NODE_H = 40

function countLeaves(node) {
  if (!node.children?.length) return 1
  return node.children.reduce((sum, c) => sum + countLeaves(c), 0)
}

function buildLayout(node, depth, yStart, yEnd) {
  const x = 40 + depth * X_GAP
  const y = (yStart + yEnd) / 2
  const id = `${depth}-${x}-${y}`
  const isRoot = depth === 0
  const isBranch = depth === 1

  nodes.value.push({ id, label: node.label, x, y, isRoot, isBranch, children: node.children })

  if (node.children?.length) {
    const totalLeaves = countLeaves(node)
    let currentY = yStart
    for (const child of node.children) {
      const childLeaves = countLeaves(child)
      const share = (childLeaves / totalLeaves) * (yEnd - yStart)
      const childResult = buildLayout(child, depth + 1, currentY, currentY + share)
      edges.value.push({ from: { x: x + 80, y }, to: { x: childResult.x, y: childResult.y } })
      currentY += share
    }
  }

  return { x, y }
}

onMounted(() => {
  nodes.value = []
  edges.value = []
  const totalLeaves = countLeaves(props.root)
  const height = Math.max(500, totalLeaves * Y_GAP_LEAF + 100)
  canvasHeight.value = height

  // Determine max depth
  function maxDepth(n, d = 0) {
    if (!n.children?.length) return d
    return Math.max(...n.children.map(c => maxDepth(c, d + 1)))
  }
  const depth = maxDepth(props.root)
  canvasWidth.value = Math.max(900, (depth + 1) * X_GAP + 200)

  buildLayout(props.root, 0, 50, height - 50)
})

function selectNode(node) {
  selectedNode.value = selectedNode.value?.id === node.id ? null : node
}

function edgePath(edge) {
  const midX = (edge.from.x + edge.to.x) / 2
  return `M ${edge.from.x} ${edge.from.y} C ${midX} ${edge.from.y}, ${midX} ${edge.to.y}, ${edge.to.x} ${edge.to.y}`
}
</script>

<template>
  <div class="edu-mindmap" style="position: relative;">
    <div class="edu-mindmap__canvas" :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px', position: 'relative' }">
      <!-- Edges (SVG) -->
      <svg :width="canvasWidth" :height="canvasHeight" style="position: absolute; top: 0; left: 0; pointer-events: none;">
        <path
          v-for="(edge, idx) in edges"
          :key="idx"
          :d="edgePath(edge)"
          class="edu-mindmap__edge"
        />
      </svg>

      <!-- Nodes -->
      <button
        v-for="node in nodes"
        :key="node.id"
        class="edu-mindmap__node"
        :class="{
          'edu-mindmap__node--root': node.isRoot,
          'edu-mindmap__node--branch': node.isBranch,
          'edu-mindmap__node--selected': selectedNode?.id === node.id,
        }"
        :style="{ left: node.x + 'px', top: (node.y - NODE_H/2) + 'px' }"
        @click="selectNode(node)"
      >
        {{ node.label }}
      </button>
    </div>

    <!-- Detail panel -->
    <transition name="slide">
      <div v-if="selectedNode" class="edu-mindmap__detail">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
          <h4 style="margin: 0; font-size: 15px; font-weight: 600; color: var(--edu-text);">{{ selectedNode.label }}</h4>
          <button style="background: none; border: none; cursor: pointer; color: var(--edu-text-muted); padding: 0;" @click="selectedNode = null">
            <span class="material-symbols-outlined" style="font-size: 20px;">close</span>
          </button>
        </div>
        <div v-if="selectedNode.children?.length" style="font-size: 13px; color: var(--edu-text-secondary);">
          <div v-for="(child, i) in selectedNode.children" :key="i" style="padding: 6px 0; border-bottom: 1px solid var(--edu-border);">
            {{ child.label }}
          </div>
        </div>
        <p v-else style="font-size: 13px; color: var(--edu-text-muted);">{{ t('education.mindmap.leafHint') }}</p>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: transform 0.2s, opacity 0.2s; }
.slide-enter-from, .slide-leave-to { transform: translateX(20px); opacity: 0; }
</style>
