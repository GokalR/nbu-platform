<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import FcSparkline from '@/components/fincontrol/FcSparkline.vue'
import AppIcon from '@/components/AppIcon.vue'
import { makeAccounts, makeTransactions } from '@/data/fincontrol'

const { t } = useI18n()

const accounts = computed(() => makeAccounts(t))
const transactions = computed(() => makeTransactions(t))

const days = computed(() => Array.from({ length: 30 }, (_, i) => t('fincontrol.accounts.dayApr', { n: i + 1 })))

const stackedData = computed(() => ({
  labels: days.value,
  datasets: accounts.value.map((a) => ({
    label: a.bank,
    data: a.spark,
    backgroundColor: a.color + '33',
    borderColor: a.color,
    borderWidth: 2,
    fill: true,
    pointRadius: 0,
    tension: 0.35,
  })),
}))
const stackedOptions = {
  plugins: { legend: { display: false } },
  interaction: { mode: 'index', intersect: false },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 10 }, maxTicksLimit: 8 } },
    y: { grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 11 } } },
  },
}

const filters = ref({ nbu: true, hbk: true, cash: true })

const pills = computed(() => [
  { key: 'week', label: t('fincontrol.common.week') },
  { key: 'month', label: t('fincontrol.common.month') },
  { key: 'quarter', label: t('fincontrol.common.quarter') },
  { key: 'year', label: t('fincontrol.common.year') },
])
const primaryAction = computed(() => ({ label: t('fincontrol.accounts.addAcc'), icon: 'add' }))
</script>

<template>
  <FcHeader
    :title="t('fincontrol.accounts.title')"
    :pills="pills"
    active-pill="month"
    :primary-action="primaryAction"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.accounts.eyebrow') }}</div>
      <h1>{{ t('fincontrol.accounts.pageTitle') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.accounts.subtitle') }}</p>
    </div>

    <!-- Hero summary -->
    <div style="background:linear-gradient(135deg,#003D7C,#0054A6);color:white;border-radius:14px;padding:22px 24px;margin-bottom:18px;display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:center;box-shadow:0 8px 24px rgba(0,61,124,.25)">
      <div>
        <div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:1.3px;opacity:.7;margin-bottom:6px">{{ t('fincontrol.accounts.totalLabel') }}</div>
        <div class="fc-num" style="font-size:36px;color:white;line-height:1">842 500 000 <span style="font-size:18px;opacity:.7">UZS</span></div>
        <div style="margin-top:8px;font-size:12.5px;color:#86EFAC;font-weight:700">{{ t('fincontrol.accounts.vsLastMonth') }}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px">
          <span class="fc-badge" style="background:rgba(255,255,255,.15);color:white">{{ t('fincontrol.accounts.accountsCount') }}</span>
          <span class="fc-badge" style="background:rgba(255,255,255,.15);color:white">{{ t('fincontrol.accounts.updated') }}</span>
          <span class="fc-badge" style="background:rgba(255,255,255,.15);color:white">{{ t('fincontrol.accounts.currency') }}</span>
          <span class="fc-badge" style="background:rgba(0,166,81,.25);color:#86EFAC">{{ t('fincontrol.accounts.cfMonth') }}</span>
        </div>
      </div>
      <div>
        <div style="font-size:11px;opacity:.7;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">{{ t('fincontrol.accounts.dynamic30') }}</div>
        <FcSparkline :data="accounts[0].spark" color="#86EFAC" :height="60" />
      </div>
    </div>

    <!-- Account cards -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin-bottom:18px">
      <div v-for="a in accounts" :key="a.key" class="fc-card" :style="`border-top:3px solid ${a.color}`">
        <div class="flex items-center justify-between" style="margin-bottom:10px">
          <div>
            <div style="font-weight:700;font-size:14px;color:#1A2B4A">{{ a.bank }}</div>
            <div style="font-size:11.5px;color:#6B7A99;font-family:'Manrope';font-variant-numeric:tabular-nums">{{ a.number }}</div>
          </div>
          <div style="display:flex;flex-direction:column;gap:3px;align-items:flex-end">
            <span v-for="b in a.badges" :key="b.label" class="fc-badge" :class="b.tone">{{ b.label }}</span>
          </div>
        </div>
        <div class="fc-num" style="font-size:24px;color:#003D7C;margin-bottom:6px">{{ a.balance }} <span style="font-size:13px;opacity:.55">UZS</span></div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0;padding:10px;background:#F8FAFC;border-radius:9px">
          <div><div style="font-size:10px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px">{{ t('fincontrol.accounts.min') }}</div><div class="fc-num" style="font-size:13px;color:#1A2B4A">{{ a.stats.min }}</div></div>
          <div><div style="font-size:10px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px">{{ t('fincontrol.accounts.max') }}</div><div class="fc-num" style="font-size:13px;color:#1A2B4A">{{ a.stats.max }}</div></div>
          <div><div style="font-size:10px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px">{{ t('fincontrol.accounts.avg') }}</div><div class="fc-num" style="font-size:13px;color:#1A2B4A">{{ a.stats.avg }}</div></div>
        </div>
        <FcSparkline :data="a.spark" :color="a.color" :height="42" />
        <div style="margin:10px 0">
          <div style="font-size:11px;color:#6B7A99;margin-bottom:4px">{{ t('fincontrol.accounts.shareTotal') }}</div>
          <div class="fc-bar"><div class="fc-bar-fill blue" :style="{ width: a.share + '%', background: a.color }"></div></div>
        </div>
        <div class="flex items-center justify-between" style="margin-top:8px">
          <button class="fc-link">{{ t('fincontrol.accounts.txLink') }}</button>
          <span style="font-size:12px;font-weight:700" :style="{ color: a.trend.tone === 'up' ? '#00A651' : '#E0384B' }">
            {{ a.trend.tone === 'up' ? '↑' : '↓' }} {{ a.trend.value }}
          </span>
        </div>
      </div>
    </div>

    <div style="text-align:center;margin-bottom:18px">
      <button class="fc-link"><AppIcon name="add" /> {{ t('fincontrol.accounts.addOther') }}</button>
    </div>

    <!-- Stacked area -->
    <div class="fc-card" style="margin-bottom:16px">
      <div class="fc-card-header">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.accounts.balanceDynTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.accounts.balanceDynSub') }}</div>
        </div>
        <div style="display:flex;gap:14px">
          <label v-for="a in accounts" :key="a.key" class="flex items-center gap-2" style="font-size:12px;font-weight:600;color:#1A2B4A;cursor:pointer">
            <input type="checkbox" v-model="filters[a.key]" :style="{ accentColor: a.color }" />
            <span :style="{ display:'inline-block', width:'10px', height:'10px', borderRadius:'2px', background: a.color }"></span>
            {{ a.bank }}
          </label>
        </div>
      </div>
      <FcChart type="line" :data="stackedData" :options="stackedOptions" :height="280" />
    </div>

    <!-- Transactions table -->
    <div class="fc-card" style="padding:0;overflow:hidden">
      <div class="fc-card-header" style="padding:18px 18px 14px">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.accounts.txTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.accounts.txSub') }}</div>
        </div>
        <div class="flex items-center gap-2">
          <select class="fc-select" style="width:auto;height:34px;font-size:12px;padding:0 10px"><option>{{ t('fincontrol.accounts.filterAll') }}</option><option>NBU •4402</option><option>HBK •1192</option></select>
          <select class="fc-select" style="width:auto;height:34px;font-size:12px;padding:0 10px"><option>{{ t('fincontrol.accounts.filterAllOps') }}</option><option>{{ t('fincontrol.accounts.income') }}</option><option>{{ t('fincontrol.accounts.expense') }}</option></select>
          <input class="fc-input" :placeholder="t('fincontrol.accounts.search')" style="height:34px;width:220px;font-size:12px" />
          <span style="font-size:12px;color:#6B7A99">{{ t('fincontrol.accounts.shown') }}</span>
        </div>
      </div>
      <table class="fc-table">
        <thead>
          <tr>
            <th>{{ t('fincontrol.accounts.colDate') }}</th><th>{{ t('fincontrol.accounts.colAccount') }}</th><th>{{ t('fincontrol.accounts.colCounterparty') }}</th><th>{{ t('fincontrol.accounts.colPurpose') }}</th><th>{{ t('fincontrol.accounts.colCategory') }}</th>
            <th style="text-align:right">{{ t('fincontrol.accounts.colIncome') }}</th><th style="text-align:right">{{ t('fincontrol.accounts.colExpense') }}</th><th style="text-align:right">{{ t('fincontrol.accounts.colBalance') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(tx, i) in transactions" :key="i" class="clickable">
            <td><div style="font-size:12.5px;color:#1A2B4A">{{ tx.date }}</div><div style="font-size:11px;color:#6B7A99">{{ tx.time }}</div></td>
            <td style="font-size:12px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#0054A6;margin-right:6px"></span>{{ tx.account }}</td>
            <td><div class="flex items-center gap-2"><span class="fc-av" :class="tx.avTone" style="width:26px;height:26px;font-size:10px">{{ tx.av }}</span><span style="font-weight:600;font-size:13px">{{ tx.name }}</span></div></td>
            <td style="font-size:12px;color:#6B7A99">{{ tx.purpose }}</td>
            <td><span class="fc-badge" :class="tx.categoryTone">{{ tx.category }}</span></td>
            <td style="text-align:right"><span v-if="tx.income" class="fc-num green">{{ tx.income }}</span><span v-else style="color:#CBD5E8">—</span></td>
            <td style="text-align:right"><span v-if="tx.expense" class="fc-num red">{{ tx.expense }}</span><span v-else style="color:#CBD5E8">—</span></td>
            <td style="text-align:right"><span class="fc-num" style="color:#003D7C">{{ ['524 000 000','439 000 000','215 000 000','491 400 000','512 600 000','449 100 000','242 720 000','103 500 000'][i] }}</span></td>
          </tr>
        </tbody>
      </table>
      <div style="display:flex;justify-content:space-between;padding:14px 18px;border-top:1px solid #DDE3EE">
        <button class="fc-cta-ghost" style="padding:6px 12px;font-size:12px"><AppIcon name="expand_more" /> {{ t('fincontrol.accounts.loadMore') }}</button>
        <div class="flex items-center gap-1">
          <button class="fc-period-pill active" style="padding:4px 10px">1</button>
          <button class="fc-period-pill" style="padding:4px 10px">2</button>
          <button class="fc-period-pill" style="padding:4px 10px">3</button>
          <span style="color:#6B7A99">…</span>
          <button class="fc-icon-btn" style="width:30px;height:30px"><AppIcon name="chevron_right" /></button>
        </div>
      </div>
    </div>
  </div>
</template>
