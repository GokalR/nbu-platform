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
  <table class="m-table">
    <thead>
      <tr>
        <th style="width:48px">#</th>
        <th>{{ $t('common.mahalla') }}</th>
        <th
          class="num-col"
          style="cursor:pointer"
          @click="sortDesc = !sortDesc"
        >
          <span style="display:inline-flex;align-items:center;gap:4px">
            {{ $t('regionsV2.ratingScore') }}
            <AppIcon :name="sortDesc ? 'arrow_downward' : 'arrow_upward'" class="!text-base" />
          </span>
        </th>
        <th style="width:32px"></th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(m, i) in sorted"
        :key="m.stir"
        :class="{ 'is-active': m.stir === highlightedStir }"
        @click="open(m.stir)"
        @mouseenter="emit('hover', m.stir)"
        @mouseleave="emit('hover', null)"
      >
        <td><span class="rank">{{ i + 1 }}</span></td>
        <td class="name">{{ m.name || '—' }}</td>
        <td class="num-col">
          <span v-if="m.rating_score != null">
            {{ m.rating_score.toLocaleString('ru-RU') }}
          </span>
          <span v-else class="faint">—</span>
        </td>
        <td><AppIcon name="chevron_right" class="muted" /></td>
      </tr>
      <tr v-if="!sorted.length">
        <td colspan="4" style="text-align:center;padding:32px 14px;color:var(--text-muted)">
          {{ $t('regionsV2.noData') }}
        </td>
      </tr>
    </tbody>
  </table>
</template>
