<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import AppIcon from '@/components/AppIcon.vue'
import {
  makeDashboardKpis,
  makeMonthly,
  makeExpenseStructure,
  makeTopCounterpartiesSuppliers,
  makeAiSignals,
  makeTransactions,
  makeAccounts,
} from '@/data/fincontrol'

const { t } = useI18n()

const activePeriod = ref('month')
const cpTab = ref('suppliers')
const chatInput = ref('')

const dashboardKpis = computed(() => makeDashboardKpis(t))
const monthly = computed(() => makeMonthly(t))
const expenseStructure = computed(() => makeExpenseStructure(t))
const topCounterpartiesSuppliers = computed(() => makeTopCounterpartiesSuppliers(t))
const aiSignals = computed(() => makeAiSignals(t))
const transactions = computed(() => makeTransactions(t))
const accounts = computed(() => makeAccounts(t))

const pills = computed(() => [
  { key: 'week', label: t('fincontrol.common.week') },
  { key: 'month', label: t('fincontrol.common.month') },
  { key: 'quarter', label: t('fincontrol.common.quarter') },
  { key: 'year', label: t('fincontrol.common.year') },
])

const incomeExpenseData = computed(() => ({
  labels: monthly.value.labels,
  datasets: [
    { type: 'bar', label: t('fincontrol.common.income'), data: monthly.value.income, backgroundColor: '#0054A6', borderRadius: 6, barThickness: 12 },
    { type: 'bar', label: t('fincontrol.common.expense'), data: monthly.value.expenses, backgroundColor: '#CBD5E8', borderRadius: 6, barThickness: 12 },
    {
      type: 'line', label: t('fincontrol.common.netCf'),
      data: monthly.value.income.map((v, i) => v - monthly.value.expenses[i]),
      borderColor: '#00A651', backgroundColor: 'rgba(0,166,81,.1)',
      borderWidth: 2.5, fill: true, tension: 0.4, pointRadius: 0, pointHoverRadius: 4,
    },
  ],
}))
const incomeExpenseOptions = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 11 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 11 }, callback: (v) => `${v}М` } },
  },
}

const donutData = computed(() => ({
  labels: expenseStructure.value.map((e) => e.label),
  datasets: [{
    data: expenseStructure.value.map((e) => e.value),
    backgroundColor: expenseStructure.value.map((e) => e.color),
    borderWidth: 0,
  }],
}))
const donutOptions = {
  cutout: '68%',
  plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${c.label}: ${c.parsed}%` } } },
}
</script>

<template>
  <FcHeader
    :title="$t('fincontrol.dashboard.title')"
    :search="$t('fincontrol.dashboard.search')"
    :pills="pills"
    active-pill="month"
    :export-button="true"
    @period="activePeriod = $event"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">NBU Institutional / FinControl</div>
      <h1>{{ $t('fincontrol.dashboard.pageTitle') }} / <span style="background:linear-gradient(90deg,#003D7C,#0054A6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">FinControl</span></h1>
      <p class="subtitle">
        <span class="fc-green-line"></span>
        {{ $t('fincontrol.dashboard.subtitle') }}
      </p>
    </div>

    <!-- KPI strip -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin-bottom:20px">
      <div v-for="kpi in dashboardKpis" :key="kpi.key" class="fc-kpi">
        <div class="fc-kpi-top">
          <div class="fc-kpi-icon" :style="{ background: kpi.iconBg, color: kpi.iconColor }">
            <AppIcon :name="kpi.icon" />
          </div>
          <span class="fc-badge" :class="kpi.deltaTone">{{ kpi.delta }}</span>
        </div>
        <div class="fc-kpi-label">{{ kpi.label }}</div>
        <div class="fc-kpi-value" :class="kpi.valueTone || ''">
          {{ kpi.value }}<span v-if="kpi.unit" style="font-size:13px;opacity:.55;margin-left:3px">{{ kpi.unit }}</span>
        </div>
        <div class="fc-kpi-sub">{{ kpi.sub }}</div>
      </div>
    </div>

    <!-- Bento row 1 -->
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px">
      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ $t('fincontrol.dashboard.incExpTitle') }}</div>
            <div class="fc-card-sub">{{ $t('fincontrol.dashboard.incExpSub') }}</div>
          </div>
          <div style="display:flex;gap:14px;font-size:12px;font-weight:600;color:#6B7A99">
            <span><span style="display:inline-block;width:10px;height:10px;background:#0054A6;border-radius:2px;margin-right:6px"></span>{{ $t('fincontrol.common.income') }}</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#CBD5E8;border-radius:2px;margin-right:6px"></span>{{ $t('fincontrol.common.expense') }}</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#00A651;border-radius:2px;margin-right:6px"></span>{{ $t('fincontrol.common.netCf') }}</span>
          </div>
        </div>
        <FcChart type="bar" :data="incomeExpenseData" :options="incomeExpenseOptions" :height="280" />
      </div>

      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ $t('fincontrol.dashboard.structureTitle') }}</div>
            <div class="fc-card-sub">{{ $t('fincontrol.dashboard.structureSub') }}</div>
          </div>
        </div>
        <div style="position:relative;height:240px;display:flex;align-items:center;justify-content:center">
          <FcChart type="doughnut" :data="donutData" :options="donutOptions" :height="240" />
          <div style="position:absolute;text-align:center;pointer-events:none">
            <div class="fc-num" style="font-size:24px;color:#003D7C">198М</div>
            <div style="font-size:11px;color:#6B7A99">{{ $t('fincontrol.dashboard.uzsExpenses') }}</div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;margin-top:14px">
          <div v-for="e in expenseStructure" :key="e.label" style="display:flex;align-items:center;gap:6px;font-size:11.5px">
            <span :style="{ width:'8px',height:'8px',background: e.color, borderRadius:'2px', flexShrink:0 }"></span>
            <span style="flex:1;color:#1A2B4A">{{ e.label }}</span>
            <span class="fc-num" style="color:#003D7C">{{ e.value }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bento row 2 -->
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px">
      <!-- Accounts -->
      <div class="fc-card">
        <div class="fc-card-header">
          <div class="fc-card-title">{{ $t('fincontrol.accounts.title') }}</div>
          <RouterLink to="/tools/fincontrol/accounts" class="fc-link">{{ $t('fincontrol.dashboard.allAccounts') }}</RouterLink>
        </div>
        <div style="display:flex;flex-direction:column;gap:14px">
          <div v-for="a in accounts" :key="a.key">
            <div class="flex items-center justify-between" style="margin-bottom:6px">
              <div>
                <div style="font-weight:700;font-size:13px;color:#1A2B4A">{{ a.bank }}</div>
                <div style="font-size:11px;color:#6B7A99;font-family:'Manrope';font-variant-numeric:tabular-nums">{{ a.number }}</div>
              </div>
              <div class="fc-num" style="color:#003D7C;font-size:14px">{{ a.balance }}</div>
            </div>
            <div class="fc-bar"><div class="fc-bar-fill blue" :style="{ width: a.share + '%' }"></div></div>
            <div class="flex items-center justify-between" style="margin-top:4px;font-size:11px;color:#6B7A99">
              <span>{{ $t('fincontrol.dashboard.shareOfTotal', { n: a.share }) }}</span>
              <span :style="{ color: a.trend.tone === 'up' ? '#00A651' : '#E0384B', fontWeight:700 }">
                {{ a.trend.tone === 'up' ? '↑' : '↓' }} {{ a.trend.value }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Top counterparties -->
      <div class="fc-card">
        <div class="fc-card-header">
          <div class="fc-card-title">{{ $t('fincontrol.dashboard.topCp') }}</div>
          <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
            <button class="fc-period-pill" :class="{active: cpTab==='suppliers'}" @click="cpTab='suppliers'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ $t('fincontrol.dashboard.suppliers') }}</button>
            <button class="fc-period-pill" :class="{active: cpTab==='buyers'}" @click="cpTab='buyers'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ $t('fincontrol.dashboard.buyers') }}</button>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px">
          <div v-for="cp in topCounterpartiesSuppliers" :key="cp.name" class="flex items-center gap-3">
            <span class="fc-av" :class="cp.tone">{{ cp.initials }}</span>
            <div style="flex:1;min-width:0">
              <div style="font-weight:700;font-size:13px;color:#1A2B4A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ cp.name }}</div>
              <div style="font-size:11px;color:#6B7A99">{{ cp.sub }}</div>
            </div>
            <div class="fc-num red" style="font-size:13px">{{ cp.amount }}</div>
          </div>
        </div>
      </div>

      <!-- AI Signals -->
      <div class="fc-card">
        <div class="fc-card-header">
          <div class="fc-card-title flex items-center gap-2">
            <AppIcon name="auto_awesome" filled style="color:#F59E0B" /> {{ $t('fincontrol.dashboard.aiSignals') }}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px">
          <div v-for="s in aiSignals" :key="s.title" class="fc-banner" :class="s.tone">
            <AppIcon :name="s.icon" />
            <div>
              <div style="font-weight:700;margin-bottom:3px">{{ s.title }}</div>
              <div style="font-weight:500;opacity:.9">{{ s.text }}</div>
              <div style="font-size:10.5px;opacity:.6;margin-top:4px">{{ s.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bento row 3: transactions + AI chat -->
    <div style="display:grid;grid-template-columns:1.7fr 1fr;gap:16px">
      <div class="fc-card" style="padding:0;overflow:hidden">
        <div class="fc-card-header" style="padding:18px 18px 0">
          <div>
            <div class="fc-card-title">{{ $t('fincontrol.dashboard.recentTx') }}</div>
            <div class="fc-card-sub">{{ $t('fincontrol.dashboard.recentTxSub') }}</div>
          </div>
          <div class="flex items-center gap-3">
            <select class="fc-select" style="width:auto;height:32px;font-size:12px;padding:0 10px">
              <option>{{ $t('fincontrol.dashboard.filterAll') }}</option>
              <option>{{ $t('fincontrol.dashboard.filterIncoming') }}</option>
              <option>{{ $t('fincontrol.dashboard.filterOutgoing') }}</option>
            </select>
            <RouterLink to="/tools/fincontrol/income-expense" class="fc-link">{{ $t('fincontrol.dashboard.allTx') }}</RouterLink>
          </div>
        </div>
        <table class="fc-table" style="margin-top:12px">
          <thead>
            <tr>
              <th>{{ $t('fincontrol.dashboard.colDate') }}</th>
              <th>{{ $t('fincontrol.dashboard.colCp') }}</th>
              <th>{{ $t('fincontrol.dashboard.colCategory') }}</th>
              <th style="text-align:right">{{ $t('fincontrol.dashboard.colAmount') }}</th>
              <th>{{ $t('fincontrol.dashboard.colAccount') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(tx, i) in transactions.slice(0,6)" :key="i" class="clickable">
              <td style="font-size:12px;color:#6B7A99">{{ tx.date }}</td>
              <td>
                <div class="flex items-center gap-2">
                  <span class="fc-av" :class="tx.avTone" style="width:26px;height:26px;font-size:10px">{{ tx.av }}</span>
                  <span style="font-weight:600">{{ tx.name }}</span>
                </div>
              </td>
              <td><span class="fc-badge" :class="tx.categoryTone">{{ tx.category }}</span></td>
              <td style="text-align:right">
                <span class="fc-num" :class="tx.income ? 'green' : 'red'">{{ tx.income || tx.expense }}</span>
              </td>
              <td style="font-size:12px;color:#6B7A99">{{ tx.account }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="fc-aichat">
        <div class="flex items-center justify-between">
          <div>
            <div style="font-family:'Manrope';font-weight:800;font-size:15px">{{ $t('fincontrol.dashboard.aiAssistant') }}</div>
            <div style="font-size:11px;opacity:.7">{{ $t('fincontrol.dashboard.aiAssistantSub') }}</div>
          </div>
          <span class="fc-badge amber" style="background:rgba(245,158,11,.2);color:#F59E0B">FinControl AI</span>
        </div>
        <div class="fc-aichat-msg bot">
          <span v-html="$t('fincontrol.dashboard.aiMsg1')"></span>
          <span class="time">09:12</span>
        </div>
        <div class="fc-aichat-msg bot">
          {{ $t('fincontrol.dashboard.aiMsg2') }}
          <span class="time">09:13</span>
        </div>
        <div class="fc-aichat-msg user">
          {{ $t('fincontrol.dashboard.aiMsg3') }}
          <span class="time">09:18</span>
        </div>
        <div class="fc-aichat-msg bot">
          <span v-html="$t('fincontrol.dashboard.aiMsg4')"></span>
          <span class="time">09:18</span>
        </div>
        <div style="font-size:11px;opacity:.6;font-style:italic">{{ $t('fincontrol.dashboard.aiTyping') }}</div>
        <div class="fc-aichat-input">
          <input v-model="chatInput" type="text" :placeholder="$t('fincontrol.dashboard.aiInput')" />
          <button type="button"><AppIcon name="send" /></button>
        </div>
      </div>
    </div>
  </div>
</template>
