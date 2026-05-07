<script setup>
const props = defineProps({
  columns: { type: Array, required: true }, // [{ key, label, align, type? }]
  rows: { type: Array, required: true },
  highlightRowIndex: { type: Array, default: () => [] },
  firstColumnBold: { type: Boolean, default: true },
})

const alignClass = { left: 'text-left', right: 'text-right', center: 'text-center' }

const cellAlign = (col) => alignClass[col.align || 'left']
const trendColor = (tone) => ({
  positive: 'text-green-600',
  negative: 'text-red-600',
  neutral: 'text-amber-600',
}[tone] || 'text-amber-600')
</script>

<template>
  <div class="bg-white border border-rs-border rounded-card shadow-rs-card overflow-hidden">
    <table class="w-full border-collapse">
      <thead>
        <tr class="bg-gray-100">
          <th
            v-for="col in columns" :key="col.key"
            class="font-semibold text-steel-500 uppercase text-[11px] tracking-[0.8px] py-[10px] px-3"
            :class="cellAlign(col)"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, i) in rows" :key="i"
          class="border-b border-[#F1F3F5] transition-colors duration-100 hover:bg-[#FAFBFC]"
          :class="{ 'bg-[#F8FAFC]': highlightRowIndex.includes(i) }"
        >
          <template v-for="(col, j) in columns" :key="col.key">
            <td
              v-if="col.type === 'trend'"
              class="py-[10px] px-3 font-mono text-[13px] font-semibold"
              :class="[cellAlign(col), trendColor(row[col.key]?.tone)]"
            >
              {{ row[col.key]?.value }}
            </td>
            <td
              v-else
              class="py-[10px] px-3 text-carbon text-[13px]"
              :class="[
                col.type === 'number' ? 'font-mono font-semibold' : 'font-medium',
                cellAlign(col),
                (highlightRowIndex.includes(i) || (j === 0 && firstColumnBold)) && 'font-semibold',
              ]"
            >
              {{ row[col.key] }}
            </td>
          </template>
        </tr>
      </tbody>
    </table>
  </div>
</template>
