<script setup>
import { computed } from 'vue'
import RsFieldLabel from './RsFieldLabel.vue'
import RsFieldHelper from './RsFieldHelper.vue'
import RsIcon from './RsIcon.vue'
import { useRsLang } from '@/composables/useRsLang'

const props = defineProps({
  label: { type: String, default: '' },
  options: { type: Array, required: true },
  helper: { type: String, default: '' },
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const { lang } = useRsLang()
const resolvedPlaceholder = computed(
  () => props.placeholder || (lang.value === 'uz' ? 'Танланг' : 'Выберите'),
)

const inputCls = computed(() => [
  'w-full h-12 px-4 bg-white border-[1.5px] border-rs-border rounded-[10px] text-[14px] font-medium text-carbon outline-none transition-[border-color,box-shadow] duration-150 focus:border-gold-500 focus:shadow-[0_0_0_3px_rgba(215,181,109,0.15)] appearance-none pr-10 cursor-pointer',
  props.disabled && 'bg-gray-100 cursor-not-allowed text-[#898989]',
  !props.modelValue && 'text-[#898989] font-normal',
])
</script>

<template>
  <div>
    <RsFieldLabel v-if="label">{{ label }}</RsFieldLabel>
    <div class="relative">
      <select
        :value="modelValue"
        :disabled="disabled"
        :class="inputCls"
        @change="$emit('update:modelValue', $event.target.value)"
      >
        <option value="" disabled>{{ resolvedPlaceholder }}</option>
        <option
          v-for="opt in options" :key="opt" :value="opt"
          class="text-carbon font-medium"
        >
          {{ opt }}
        </option>
      </select>
      <RsIcon
        name="chevron-down" :size="18"
        class="absolute right-4 top-1/2 -translate-y-1/2 text-steel-500 pointer-events-none"
      />
    </div>
    <RsFieldHelper v-if="helper">{{ helper }}</RsFieldHelper>
  </div>
</template>
