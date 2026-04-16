<script setup>
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'

const router = useRouter()
const { t } = useI18n()

const items = computed(() => [
  { to: '/tools/fincontrol/dashboard', icon: 'dashboard', label: t('fincontrol.dashboard.title') },
  { to: '/tools/fincontrol/accounts', icon: 'account_balance_wallet', label: t('fincontrol.accounts.title') },
  { to: '/tools/fincontrol/cashflow', icon: 'trending_up', label: t('fincontrol.cashflow.title') },
  { to: '/tools/fincontrol/income-expense', icon: 'bar_chart', label: t('fincontrol.incomeExpense.title') },
  { to: '/tools/fincontrol/pnl', icon: 'description', label: t('fincontrol.pnl.title') },
  { to: '/tools/fincontrol/counterparties', icon: 'group', label: t('fincontrol.counterparties.title') },
  { to: '/tools/fincontrol/planning', icon: 'event_note', label: t('fincontrol.planning.title') },
  { to: '/tools/fincontrol/import', icon: 'download', label: t('fincontrol.import.title') },
])
</script>

<template>
  <aside class="fc-sidebar">
    <button type="button" class="fc-sb-back" @click="router.push('/tools')">
      <AppIcon name="chevron_left" />
      <span>{{ $t('fincontrol.sidebar.home') }}</span>
    </button>

    <div class="fc-sb-brand">
      <div class="fc-sb-brand-icon">
        <AppIcon name="auto_awesome" filled />
      </div>
      <div>
        <div class="name">FinControl</div>
        <div class="sub">{{ $t('fincontrol.sidebar.assistant') }}</div>
      </div>
    </div>

    <nav class="fc-sb-nav">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="fc-sb-item"
        active-class="active"
      >
        <AppIcon class="nav-icon" :name="item.icon" />
        <span>{{ item.label }}</span>
      </RouterLink>

      <div class="fc-sb-divider"></div>

      <RouterLink
        to="/tools/fincontrol/ai"
        class="fc-sb-item ai"
        active-class="active"
      >
        <AppIcon class="nav-icon" name="auto_awesome" filled />
        <span>{{ $t('fincontrol.sidebar.aiHelper') }}</span>
      </RouterLink>
    </nav>

    <div class="fc-sb-footer">
      <button type="button" class="fc-sb-item">
        <AppIcon class="nav-icon" name="help" />
        <span>{{ $t('fincontrol.sidebar.support') }}</span>
      </button>
      <button type="button" class="fc-sb-item">
        <AppIcon class="nav-icon" name="settings" />
        <span>{{ $t('fincontrol.sidebar.settings') }}</span>
      </button>
    </div>
  </aside>
</template>
