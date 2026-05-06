<script setup>
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  categories: { type: Array, required: true },
  sphereIdx: { type: Number, required: true },
  sphereCount: { type: Number, required: true },
  selectedId: { type: String, default: '' },
})
const emit = defineEmits(['next', 'back'])

const { t, locale } = useI18n()

function pick(cat) {
  emit('next', { id: cat.id, nameRu: cat.name.ru, nameUz: cat.name.uz })
}
</script>

<template>
  <div class="space-y-6">
    <div class="text-center space-y-2">
      <p class="inline-block text-xs font-semibold text-primary bg-primary/10 px-3 py-1 rounded-full">
        {{ t('smeProfile.category.sphere', { n: sphereIdx + 1, total: sphereCount }) }}
      </p>
      <h2 class="text-2xl font-bold text-on-surface">{{ t('smeProfile.category.title') }}</h2>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="group flex flex-col items-center gap-3 p-5 rounded-card border-2 transition-all duration-200 text-center"
        :class="
          cat.id === selectedId
            ? 'border-primary bg-primary/10 shadow-md'
            : 'border-outline-variant bg-white hover:border-primary/50 hover:bg-primary/5'
        "
        @click="pick(cat)"
      >
        <div
          class="w-12 h-12 rounded-2xl flex items-center justify-center transition-colors"
          :class="cat.id === selectedId ? 'bg-primary' : 'bg-primary/10 group-hover:bg-primary/20'"
        >
          <AppIcon
            :name="cat.icon || 'business_center'"
            class="text-2xl"
            :class="cat.id === selectedId ? 'text-white' : 'text-primary'"
          />
        </div>
        <span
          class="text-sm font-semibold leading-tight"
          :class="cat.id === selectedId ? 'text-primary' : 'text-on-surface'"
        >
          {{ locale === 'ru' ? cat.name.ru : cat.name.uz }}
        </span>
      </button>
    </div>

    <button
      class="inline-flex items-center justify-center gap-2 w-full px-5 py-3 bg-surface-container text-on-surface border border-outline-variant rounded-btn text-sm font-semibold hover:bg-surface-container-high transition-all"
      @click="emit('back')"
    >
      <AppIcon name="arrow_back" />
      {{ t('smeProfile.back') }}
    </button>
  </div>
</template>
