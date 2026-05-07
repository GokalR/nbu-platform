<script setup>
import { ref } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
  title: { type: String, required: true },
  search: { type: String, default: '' },
  pills: { type: Array, default: () => [] }, // [{key, label}]
  activePill: { type: String, default: '' },
  primaryAction: { type: Object, default: null }, // {label, icon}
  secondaryAction: { type: Object, default: null }, // {label, icon}
  exportButton: { type: [Boolean, Object], default: false }, // true | {label, color}
  pdfExcel: { type: Boolean, default: false },
})
const emit = defineEmits(['period', 'primary', 'secondary'])
const searchValue = ref('')
</script>

<template>
  <header class="fc-header">
    <span class="fc-header-title">{{ title }}</span>

    <div v-if="search" class="fc-header-search">
      <AppIcon class="fc-header-search-icon" name="search" />
      <input v-model="searchValue" type="search" :placeholder="search" />
    </div>
    <div v-else class="flex-1"></div>

    <div v-if="pills.length" class="fc-period-pills">
      <button
        v-for="p in pills"
        :key="p.key"
        type="button"
        class="fc-period-pill"
        :class="{ active: activePill === p.key }"
        @click="emit('period', p.key)"
      >
        {{ p.label }}
      </button>
    </div>

    <div class="fc-header-actions">
      <button
        v-if="exportButton === true"
        type="button"
        class="fc-export-btn"
      >
        <AppIcon name="file_download" />
        <span>{{ $t('fincontrol.dashboard.export') }}</span>
      </button>
      <template v-if="pdfExcel">
        <button type="button" class="fc-export-btn">
          <AppIcon name="picture_as_pdf" />
          <span>PDF</span>
        </button>
        <button type="button" class="fc-export-btn green">
          <AppIcon name="grid_on" />
          <span>Excel</span>
        </button>
        <button type="button" class="fc-icon-btn">
          <AppIcon name="share" />
        </button>
      </template>
      <button
        v-if="secondaryAction"
        type="button"
        class="fc-cta-ghost"
        style="height:34px;padding:0 14px;display:inline-flex;align-items:center;gap:6px"
        @click="emit('secondary')"
      >
        <AppIcon :name="secondaryAction.icon || 'edit'" />
        <span>{{ secondaryAction.label }}</span>
      </button>
      <button v-if="primaryAction" type="button" class="fc-primary-btn" @click="emit('primary')">
        <AppIcon :name="primaryAction.icon || 'add'" />
        <span>{{ primaryAction.label }}</span>
      </button>
      <button type="button" class="fc-icon-btn">
        <AppIcon name="notifications" />
        <span class="fc-notif-dot"></span>
      </button>
      <div class="fc-avatar">АБ</div>
    </div>
  </header>
</template>
