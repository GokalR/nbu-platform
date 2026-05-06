<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
  mahallas: { type: Array, required: true },
  highlightedStir: { type: String, default: null },
})
const emit = defineEmits(['hover'])

const router = useRouter()
const sortDesc = ref(false)

const sorted = computed(() => {
  const copy = [...props.mahallas]
  copy.sort((a, b) => {
    const av = a.rating_score
    const bv = b.rating_score
    if (av == null && bv == null) return 0
    if (av == null) return 1
    if (bv == null) return -1
    return sortDesc.value ? bv - av : av - bv
  })
  return copy
})

function open(stir) {
  router.push(`/regions-v2/mahallas/${stir}`)
}
</script>

<template>
  <div class="rounded-xl bg-white border border-slate-200/70 overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wide">
        <tr>
          <th class="px-4 py-3 text-left w-12">#</th>
          <th class="px-4 py-3 text-left">{{ $t('common.mahalla') }}</th>
          <th
            class="px-4 py-3 text-right cursor-pointer hover:text-slate-900"
            @click="sortDesc = !sortDesc"
          >
            <span class="inline-flex items-center gap-1">
              {{ $t('regionsV2.ratingScore') }}
              <AppIcon :name="sortDesc ? 'arrow_downward' : 'arrow_upward'" class="!text-base" />
            </span>
          </th>
          <th class="px-4 py-3 w-12"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(m, i) in sorted"
          :key="m.stir"
          class="border-t border-slate-100 cursor-pointer transition-colors"
          :class="m.stir === highlightedStir ? 'bg-blue-50' : 'hover:bg-slate-50'"
          @click="open(m.stir)"
          @mouseenter="emit('hover', m.stir)"
          @mouseleave="emit('hover', null)"
        >
          <td class="px-4 py-2.5 text-slate-400 font-mono text-xs">{{ i + 1 }}</td>
          <td class="px-4 py-2.5 font-medium text-slate-900">{{ m.name || '—' }}</td>
          <td class="px-4 py-2.5 text-right tabular-nums">
            <span v-if="m.rating_score != null" class="font-semibold text-slate-700">
              {{ m.rating_score.toLocaleString('ru-RU') }}
            </span>
            <span v-else class="text-slate-400">—</span>
          </td>
          <td class="px-4 py-2.5 text-right">
            <AppIcon name="chevron_right" class="text-slate-400" />
          </td>
        </tr>
        <tr v-if="!sorted.length">
          <td colspan="4" class="px-4 py-8 text-center text-slate-500 text-sm">
            {{ $t('regionsV2.noData') }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
