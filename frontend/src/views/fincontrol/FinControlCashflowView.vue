<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import FcSparkline from '@/components/fincontrol/FcSparkline.vue'
import AppIcon from '@/components/AppIcon.vue'
import { makeRecurring } from '@/data/fincontrol'

const { t } = useI18n()

const recurring = computed(() => makeRecurring(t))

const tab = ref('outgoing')
const granularity = ref('day')

const days = Array.from({ length: 30 }, (_, i) => `${i + 1}`)
const inflowDay = [8.2, 11.4, 7.6, 13.8, 16.2, 9.4, 0, 12.8, 14.2, 7.0, 11.8, 9.0, 13.4, 16.8, 10.4, 8.6, 12.0, 14.6, 7.8, 11.2, 13.0, 9.4, 15.2, 12.6, 8.8, 11.4, 13.8, 16.0, 10.2, 9.0]
const outflowDay = [5.4, 7.2, 4.8, 9.0, 11.0, 6.0, 0, 8.2, 9.0, 4.4, 7.4, 5.8, 8.6, 11.2, 6.6, 5.4, 7.6, 9.2, 5.0, 7.0, 8.2, 6.0, 9.6, 8.0, 5.6, 7.2, 8.6, 10.4, 6.4, 5.6]

const cfData = computed(() => ({
  labels: days,
  datasets: [
    { type: 'bar', label: t('fincontrol.cashflow.income'), data: inflowDay, backgroundColor: '#003D7C', borderRadius: 4, barThickness: 8 },
    { type: 'bar', label: t('fincontrol.cashflow.expense'), data: outflowDay.map((v) => -v), backgroundColor: '#CBD5E8', borderRadius: 4, barThickness: 8 },
    {
      type: 'line', label: t('fincontrol.cashflow.netCf'),
      data: inflowDay.map((v, i) => v - outflowDay[i]),
      borderColor: '#00A651', backgroundColor: 'rgba(0,166,81,.1)', borderWidth: 2.5, fill: true, tension: 0.4, pointRadius: 0,
    },
  ],
}))
const cfOptions = {
  plugins: { legend: { display: false } },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 10 } } },
    y: { stacked: false, grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 11 }, callback: (v) => `${v}М` } },
  },
}

const pills = computed(() => [
  { key: 'week', label: t('fincontrol.common.week') },
  { key: 'month', label: t('fincontrol.common.month') },
  { key: 'quarter', label: t('fincontrol.common.quarter') },
  { key: 'year', label: t('fincontrol.common.year') },
])
</script>

<template>
  <FcHeader
    :title="t('fincontrol.cashflow.title')"
    :pills="pills"
    active-pill="month"
    :export-button="true"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.cashflow.eyebrow') }}</div>
      <h1>{{ t('fincontrol.cashflow.pageTitle') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.cashflow.subtitle') }}</p>
    </div>

    <!-- KPI strip -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px">
      <div class="fc-kpi" style="border-top:3px solid #00A651">
        <div class="fc-kpi-label">{{ t('fincontrol.cashflow.inflow') }}</div>
        <div class="fc-kpi-value green">320 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:6px"><span class="fc-badge green">▲ 8.2%</span><span class="fc-kpi-sub">{{ t('fincontrol.cashflow.vsPrev1') }}</span></div>
        <FcSparkline :data="[28,31,30,33,36,32,35,38,40,42,38,40]" color="#00A651" :height="36" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #E0384B">
        <div class="fc-kpi-label">{{ t('fincontrol.cashflow.outflow') }}</div>
        <div class="fc-kpi-value red">198 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:6px"><span class="fc-badge red">▼ 3.1%</span><span class="fc-kpi-sub">{{ t('fincontrol.cashflow.vsPrev2') }}</span></div>
        <FcSparkline :data="[20,22,21,24,23,25,22,21,20,19,18,19.8]" color="#E0384B" :height="36" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #003D7C">
        <div class="fc-kpi-label">{{ t('fincontrol.cashflow.netCf') }}</div>
        <div class="fc-kpi-value navy">122 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:6px"><span class="fc-badge blue">▲ 15.0%</span><span class="fc-kpi-sub">{{ t('fincontrol.cashflow.vsPrev3') }}</span></div>
        <FcSparkline :data="[8,9,9,9,13,7,13,17,20,23,20,20.2]" color="#003D7C" :height="36" />
      </div>
    </div>

    <!-- Main grid -->
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:18px">
      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.cashflow.chartTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.cashflow.chartSub') }}</div>
          </div>
          <div class="flex items-center gap-3">
            <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
              <button class="fc-period-pill" :class="{active:granularity==='day'}" @click="granularity='day'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.cashflow.byDay') }}</button>
              <button class="fc-period-pill" :class="{active:granularity==='week'}" @click="granularity='week'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.cashflow.byWeek') }}</button>
              <button class="fc-period-pill" :class="{active:granularity==='month'}" @click="granularity='month'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.cashflow.byMonth') }}</button>
            </div>
          </div>
        </div>
        <div style="display:flex;gap:14px;margin-bottom:8px;font-size:12px;color:#6B7A99">
          <span><span style="display:inline-block;width:10px;height:10px;background:#003D7C;border-radius:2px;margin-right:6px"></span>{{ t('fincontrol.cashflow.income') }}</span>
          <span><span style="display:inline-block;width:10px;height:10px;background:#CBD5E8;border-radius:2px;margin-right:6px"></span>{{ t('fincontrol.cashflow.expense') }}</span>
          <span><span style="display:inline-block;width:10px;height:10px;background:#00A651;border-radius:2px;margin-right:6px"></span>{{ t('fincontrol.cashflow.netCf') }}</span>
        </div>
        <FcChart type="bar" :data="cfData" :options="cfOptions" :height="280" />
        <div class="fc-card-sub" style="margin-top:8px;text-align:center"><AppIcon name="info" style="font-size:14px;vertical-align:middle" /> {{ t('fincontrol.cashflow.tip') }}</div>
      </div>

      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.cashflow.byActivityTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.cashflow.byActivitySub') }}</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:14px">
          <div>
            <div class="flex items-center gap-2" style="margin-bottom:6px">
              <AppIcon name="business_center" style="color:#00A651" />
              <div style="flex:1"><div style="font-weight:700;font-size:13px;color:#1A2B4A">{{ t('fincontrol.cashflow.operCf') }}</div><div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.cashflow.operCfSub') }}</div></div>
              <span class="fc-num green">+98 400 000</span>
            </div>
            <div class="fc-bar"><div class="fc-bar-fill green" style="width:80%"></div></div>
          </div>
          <div>
            <div class="flex items-center gap-2" style="margin-bottom:6px">
              <AppIcon name="precision_manufacturing" style="color:#E0384B" />
              <div style="flex:1"><div style="font-weight:700;font-size:13px;color:#1A2B4A">{{ t('fincontrol.cashflow.investCf') }}</div><div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.cashflow.investCfSub') }}</div></div>
              <span class="fc-num red">−18 200 000</span>
            </div>
            <div class="fc-bar"><div class="fc-bar-fill red" style="width:15%"></div></div>
          </div>
          <div>
            <div class="flex items-center gap-2" style="margin-bottom:6px">
              <AppIcon name="payments" style="color:#0054A6" />
              <div style="flex:1"><div style="font-weight:700;font-size:13px;color:#1A2B4A">{{ t('fincontrol.cashflow.finCf') }}</div><div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.cashflow.finCfSub') }}</div></div>
              <span class="fc-num" style="color:#0054A6">+41 800 000</span>
            </div>
            <div class="fc-bar"><div class="fc-bar-fill blue" style="width:34%"></div></div>
          </div>
          <div style="background:#EEF4FF;padding:12px;border-radius:9px;display:flex;align-items:center;justify-content:space-between">
            <div><div style="font-weight:800;font-size:13px;color:#003D7C">{{ t('fincontrol.cashflow.netCfBox') }}</div><div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.cashflow.netCfBoxSub') }}</div></div>
            <div style="text-align:right">
              <div class="fc-num" style="color:#003D7C;font-size:18px">+122 000 000</div>
              <div style="font-size:11px;color:#00A651;font-weight:700">UZS ▲ 15%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recurring -->
    <div class="fc-card" style="padding:0;overflow:hidden">
      <div class="fc-card-header" style="padding:18px 18px 14px">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.cashflow.recurringTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.cashflow.recurringSub') }}</div>
        </div>
        <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
          <button class="fc-period-pill" :class="{active:tab==='outgoing'}" @click="tab='outgoing'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.cashflow.outgoing') }}</button>
          <button class="fc-period-pill" :class="{active:tab==='incoming'}" @click="tab='incoming'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.cashflow.incoming') }}</button>
        </div>
      </div>
      <table class="fc-table">
        <thead>
          <tr><th>{{ t('fincontrol.cashflow.colName') }}</th><th>{{ t('fincontrol.cashflow.colCategory') }}</th><th>{{ t('fincontrol.cashflow.colPeriod') }}</th><th>{{ t('fincontrol.cashflow.colNext') }}</th><th style="text-align:right">{{ t('fincontrol.cashflow.colAmount') }}</th><th>{{ t('fincontrol.cashflow.colStatus') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in (tab==='outgoing' ? recurring.outgoing : recurring.incoming)" :key="i" :class="{ danger: r.danger }">
            <td><div style="font-weight:700;font-size:13px">{{ r.name }}</div><div style="font-size:11px;color:#6B7A99">{{ r.sub }}</div></td>
            <td><span class="fc-badge" :class="r.categoryTone">{{ r.category }}</span></td>
            <td style="font-size:12px;color:#6B7A99">{{ r.period }}</td>
            <td style="font-size:12.5px;color:#1A2B4A;font-weight:600">{{ r.date }}</td>
            <td style="text-align:right"><span class="fc-num" :class="r.amount.startsWith('+') ? 'green' : 'red'">{{ r.amount }}</span></td>
            <td><span class="fc-badge" :class="r.statusTone">{{ r.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
