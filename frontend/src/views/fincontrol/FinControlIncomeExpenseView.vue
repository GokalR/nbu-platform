<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import FcSparkline from '@/components/fincontrol/FcSparkline.vue'
import AppIcon from '@/components/AppIcon.vue'
import { makeTransactions, makeExpenseStructure, makeExpenseCategories, makeIncomeCategories } from '@/data/fincontrol'

const { t, tm } = useI18n()

const transactions = computed(() => makeTransactions(t))
const expenseStructure = computed(() => makeExpenseStructure(t))
const expenseCategories = computed(() => makeExpenseCategories(t))
const incomeCategories = computed(() => makeIncomeCategories(t))

const compareMode = ref('both')
const txTab = ref('all')

const compareData = computed(() => ({
  labels: tm('fincontrol.incomeExpense.weeks'),
  datasets: [
    { label: t('fincontrol.incomeExpense.dsAprIncome'), data: [76, 84, 88, 72], backgroundColor: '#0054A6', stack: 'apr', borderRadius: 5, barThickness: 18 },
    { label: t('fincontrol.incomeExpense.dsAprExpense'), data: [-46, -52, -54, -46], backgroundColor: '#003D7C', stack: 'apr', borderRadius: 5, barThickness: 18 },
    { label: t('fincontrol.incomeExpense.dsMarIncome'), data: [68, 78, 80, 70], backgroundColor: '#CBD5E8', stack: 'mar', borderRadius: 5, barThickness: 18 },
    { label: t('fincontrol.incomeExpense.dsMarExpense'), data: [-50, -56, -58, -40], backgroundColor: '#94A3B8', stack: 'mar', borderRadius: 5, barThickness: 18 },
  ],
}))
const compareOptions = {
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
const donutOptions = { cutout: '68%', plugins: { legend: { display: false } } }

const pills = computed(() => [
  { key: 'week', label: t('fincontrol.common.week') },
  { key: 'month', label: t('fincontrol.common.month') },
  { key: 'quarter', label: t('fincontrol.common.quarter') },
  { key: 'year', label: t('fincontrol.common.year') },
])
const txTabs = computed(() => [
  { k: 'all', l: t('fincontrol.incomeExpense.tabAll') },
  { k: 'income', l: t('fincontrol.incomeExpense.tabIncome') },
  { k: 'expense', l: t('fincontrol.incomeExpense.tabExpense') },
])
</script>

<template>
  <FcHeader
    :title="t('fincontrol.incomeExpense.title')"
    :pills="pills"
    active-pill="month"
    :export-button="true"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.incomeExpense.eyebrow') }}</div>
      <h1>{{ t('fincontrol.incomeExpense.pageTitle') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.incomeExpense.subtitle') }}</p>
    </div>

    <!-- KPI strip -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px">
      <div class="fc-kpi" style="border-top:3px solid #00A651">
        <div class="fc-kpi-label">{{ t('fincontrol.incomeExpense.income') }}</div>
        <div class="fc-kpi-value green">320 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge green">▲ 8.2%</span><span class="fc-kpi-sub">{{ t('fincontrol.incomeExpense.vsPrev1') }}</span></div>
        <FcSparkline :data="[28,30,32,30,33,35,32,36,38,40,38,40]" color="#00A651" :height="34" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #E0384B">
        <div class="fc-kpi-label">{{ t('fincontrol.incomeExpense.expense') }}</div>
        <div class="fc-kpi-value red">198 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge red">▼ 3.1%</span><span class="fc-kpi-sub">{{ t('fincontrol.incomeExpense.vsPrev2') }}</span></div>
        <FcSparkline :data="[22,21,23,24,22,21,20,21,19,20,19,19.8]" color="#E0384B" :height="34" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #003D7C">
        <div class="fc-kpi-label">{{ t('fincontrol.incomeExpense.netResult') }}</div>
        <div class="fc-kpi-value navy">122 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge blue">▲ 15.0%</span><span class="fc-kpi-sub">{{ t('fincontrol.incomeExpense.vsPrev3') }}</span></div>
        <FcSparkline :data="[6,9,9,6,11,14,12,15,19,20,19,20.2]" color="#003D7C" :height="34" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #94A3B8">
        <div class="fc-kpi-label">{{ t('fincontrol.incomeExpense.avgExpDay') }}</div>
        <div class="fc-kpi-value" style="color:#475569">6 387 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge slate">{{ t('fincontrol.incomeExpense.stable') }}</span><span class="fc-kpi-sub">{{ t('fincontrol.incomeExpense.aprDays') }}</span></div>
        <FcSparkline :data="[6.4,6.3,6.5,6.4,6.4,6.3,6.4,6.5,6.4,6.4,6.3,6.4]" color="#94A3B8" :height="34" />
      </div>
    </div>

    <!-- Main grid -->
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:18px">
      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.incomeExpense.compareTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.incomeExpense.compareSub') }}</div>
          </div>
          <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
            <button class="fc-period-pill" :class="{active:compareMode==='both'}" @click="compareMode='both'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.incomeExpense.both') }}</button>
            <button class="fc-period-pill" :class="{active:compareMode==='income'}" @click="compareMode='income'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.incomeExpense.income') }}</button>
            <button class="fc-period-pill" :class="{active:compareMode==='expense'}" @click="compareMode='expense'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.incomeExpense.expense') }}</button>
          </div>
        </div>
        <div style="display:flex;gap:14px;margin-bottom:8px;font-size:12px;color:#6B7A99">
          <span><span style="display:inline-block;width:10px;height:10px;background:#003D7C;border-radius:2px;margin-right:6px"></span>{{ t('fincontrol.incomeExpense.april') }}</span>
          <span><span style="display:inline-block;width:10px;height:10px;background:#CBD5E8;border-radius:2px;margin-right:6px"></span>{{ t('fincontrol.incomeExpense.march') }}</span>
        </div>
        <FcChart type="bar" :data="compareData" :options="compareOptions" :height="280" />
      </div>

      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.incomeExpense.structureTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.incomeExpense.structureSub') }}</div>
          </div>
        </div>
        <div style="position:relative;height:200px;display:flex;align-items:center;justify-content:center">
          <FcChart type="doughnut" :data="donutData" :options="donutOptions" :height="200" />
          <div style="position:absolute;text-align:center;pointer-events:none">
            <div class="fc-num" style="font-size:18px;color:#003D7C">{{ t('fincontrol.incomeExpense.purchases') }}</div>
            <div style="font-size:12px;color:#6B7A99">{{ t('fincontrol.incomeExpense.purchasesShare') }}</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:5px;margin-top:14px">
          <div v-for="e in expenseStructure" :key="e.label" class="flex items-center gap-2" style="font-size:12px">
            <span :style="{ width:'10px', height:'10px', borderRadius:'2px', background:e.color }"></span>
            <span style="flex:1;color:#1A2B4A">{{ e.label }}</span>
            <span class="fc-num" style="color:#003D7C">{{ e.value }}%</span>
            <span class="fc-num" style="color:#6B7A99;font-weight:600">{{ e.amount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Expense categories -->
    <div class="flex items-center justify-between" style="margin-bottom:12px">
      <h3 class="fc-card-title" style="font-size:16px">{{ t('fincontrol.incomeExpense.expCatTitle') }}</h3>
      <button class="fc-link">{{ t('fincontrol.incomeExpense.manage') }}</button>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:24px">
      <div v-for="c in expenseCategories" :key="c.name" class="fc-card" style="padding:16px;position:relative">
        <div class="flex items-center justify-between" style="margin-bottom:8px">
          <div style="font-size:24px">{{ c.emoji }}</div>
          <span class="fc-badge" :class="c.trendTone">{{ c.trend }}</span>
        </div>
        <div style="font-weight:700;color:#1A2B4A;font-size:14px;margin-bottom:4px">{{ c.name }}</div>
        <div class="fc-num" style="color:#003D7C;font-size:18px">{{ c.amount }} <span style="font-size:11px;opacity:.55">UZS</span></div>
        <div style="font-size:11px;color:#6B7A99;margin:6px 0">{{ c.share }}{{ t('fincontrol.incomeExpense.shareOfExp') }}</div>
        <div class="fc-bar"><div class="fc-bar-fill" :class="c.overspend ? 'red' : 'blue'" :style="{ width: c.bar + '%' }"></div></div>
        <div v-if="c.overspend" class="fc-banner red" style="margin-top:8px;padding:6px 10px;font-size:11.5px">
          <AppIcon name="warning" /> {{ t('fincontrol.incomeExpense.overspend') }}
        </div>
      </div>
    </div>

    <!-- Income categories -->
    <div class="flex items-center justify-between" style="margin-bottom:12px">
      <h3 class="fc-card-title" style="font-size:16px">{{ t('fincontrol.incomeExpense.incCatTitle') }}</h3>
      <button class="fc-link">{{ t('fincontrol.incomeExpense.more') }}</button>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:24px">
      <div v-for="c in incomeCategories" :key="c.name" class="fc-card" style="padding:16px">
        <div style="font-size:24px;margin-bottom:8px">{{ c.emoji }}</div>
        <div style="font-weight:700;color:#1A2B4A;font-size:14px;margin-bottom:4px">{{ c.name }}</div>
        <div class="fc-num green" style="font-size:18px">{{ c.amount }} <span style="font-size:11px;opacity:.55;color:#6B7A99">UZS</span></div>
        <div style="font-size:11px;color:#6B7A99;margin:6px 0">{{ c.share }}{{ t('fincontrol.incomeExpense.shareOfInc') }}</div>
        <div class="fc-bar"><div class="fc-bar-fill green" :style="{ width: c.bar + '%' }"></div></div>
      </div>
    </div>

    <!-- Transactions -->
    <div class="fc-card" style="padding:0;overflow:hidden">
      <div class="fc-card-header" style="padding:18px 18px 14px">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.incomeExpense.txTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.incomeExpense.txSub') }}</div>
        </div>
        <div class="flex items-center gap-2">
          <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
            <button v-for="tt in txTabs" :key="tt.k"
              class="fc-period-pill" :class="{active:txTab===tt.k}" @click="txTab=tt.k" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ tt.l }}</button>
          </div>
          <select class="fc-select" style="width:auto;height:34px;font-size:12px;padding:0 10px"><option>{{ t('fincontrol.incomeExpense.allCategories') }}</option><option>{{ t('fincontrol.incomeExpense.catPurchases') }}</option><option>{{ t('fincontrol.incomeExpense.catSalary') }}</option><option>{{ t('fincontrol.incomeExpense.catTaxes') }}</option><option>{{ t('fincontrol.incomeExpense.catRent') }}</option><option>{{ t('fincontrol.incomeExpense.catMarketing') }}</option><option>{{ t('fincontrol.incomeExpense.catOther') }}</option></select>
          <input class="fc-input" :placeholder="t('fincontrol.incomeExpense.search')" style="height:34px;width:180px;font-size:12px" />
          <span style="font-size:12px;color:#6B7A99">{{ t('fincontrol.incomeExpense.shown') }}</span>
        </div>
      </div>
      <table class="fc-table">
        <thead>
          <tr><th>{{ t('fincontrol.incomeExpense.colDate') }}</th><th>{{ t('fincontrol.incomeExpense.colCounterparty') }}</th><th>{{ t('fincontrol.incomeExpense.colCategory') }}</th><th>{{ t('fincontrol.incomeExpense.colPurpose') }}</th><th style="text-align:right">{{ t('fincontrol.incomeExpense.colIncome') }}</th><th style="text-align:right">{{ t('fincontrol.incomeExpense.colExpense') }}</th><th>{{ t('fincontrol.incomeExpense.colAccount') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="(tx, i) in transactions.slice(0,7)" :key="i" class="clickable">
            <td><div style="font-size:12.5px">{{ tx.date }}</div><div style="font-size:11px;color:#6B7A99">{{ tx.time }}</div></td>
            <td><div class="flex items-center gap-2"><span class="fc-av" :class="tx.avTone" style="width:26px;height:26px;font-size:10px">{{ tx.av }}</span><span style="font-weight:600;font-size:13px">{{ tx.name }}</span></div></td>
            <td><span class="fc-badge" :class="tx.categoryTone">{{ tx.category }}</span></td>
            <td style="font-size:12px;color:#6B7A99">{{ tx.purpose }}</td>
            <td style="text-align:right"><span v-if="tx.income" class="fc-num green">{{ tx.income }}</span><span v-else style="color:#CBD5E8">—</span></td>
            <td style="text-align:right"><span v-if="tx.expense" class="fc-num red">{{ tx.expense }}</span><span v-else style="color:#CBD5E8">—</span></td>
            <td style="font-size:12px;color:#6B7A99">{{ tx.account }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
