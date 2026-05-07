<script setup>
import RsFieldLabel from './RsFieldLabel.vue'
import RsFieldHelper from './RsFieldHelper.vue'

defineProps({
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  helper: { type: String, default: '' },
  modelValue: { type: String, default: '' },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <div>
    <RsFieldLabel v-if="label">{{ label }}</RsFieldLabel>
    <input
      type="text"
      :value="modelValue"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', $event.target.value)"
      class="w-full h-12 px-4 bg-white border-[1.5px] border-rs-border rounded-[10px] text-[14px] font-medium text-carbon placeholder:text-[#898989] placeholder:font-normal outline-none transition-[border-color,box-shadow] duration-150 focus:border-gold-500 focus:shadow-[0_0_0_3px_rgba(215,181,109,0.15)]"
    />
    <RsFieldHelper v-if="helper">{{ helper }}</RsFieldHelper>
  </div>
</template>
