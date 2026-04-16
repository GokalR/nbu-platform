<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import FcSparkline from '@/components/fincontrol/FcSparkline.vue'
import AppIcon from '@/components/AppIcon.vue'
import { makePnlRows } from '@/data/fincontrol'

const { t, tm } = useI18n()

const pnlRows = computed(() => makePnlRows(t))

const dismissDisclaimer = ref(false)

const trendData = computed(() => ({
  labels: tm('fincontrol.pnl.months'),
  datasets: [
    { label: t('fincontrol.pnl.lblRevenue'), data: [265, 278, 270, 295, 308, 320], borderColor: '#003D7C', backgroundColor: 'rgba(0,61,124,.06)', borderWidth: 2.5, tension: 0.4, pointRadius: 3, pointHoverRadius: 5, fill: false },
    { label: t('fincontrol.pnl.lblGross'), data: [95, 102, 96, 108, 106, 122], borderColor: '#0054A6', backgroundColor: 'rgba(0,84,166,.06)', borderWidth: 2.5, tension: 0.4, pointRadius: 3, fill: false },
    { label: t('fincontrol.pnl.lblNetEst'), data: [38, 44, 40, 50, 56, 65], borderColor: '#F59E0B', backgroundColor: 'rgba(245,158,11,.15)', borderWidth: 2.5, borderDash: [6, 4], tension: 0.4, pointRadius: 3, fill: true },
  ],
}))
const trendOptions = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 11 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 11 }, callback: (v) => `${v}М` } },
  },
}

const pills = computed(() => [
  { key: 'q1', label: t('fincontrol.pnl.q1') },
  { key: 'may', label: t('fincontrol.pnl.may') },
  { key: 'h1', label: t('fincontrol.pnl.h1') },
  { key: 'year', label: t('fincontrol.pnl.year') },
])
</script>

<template>
  <FcHeader
    :title="t('fincontrol.pnl.title')"
    :pills="pills"
    active-pill="may"
    :pdf-excel="true"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.pnl.eyebrow') }}</div>
      <h1>{{ t('fincontrol.pnl.pageTitle') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.pnl.subtitle') }}</p>
    </div>

    <!-- Disclaimer -->
    <div v-if="!dismissDisclaimer" class="fc-banner amber" style="margin-bottom:18px;align-items:center">
      <AppIcon name="warning" />
      <span style="flex:1" v-html="t('fincontrol.pnl.disclaimer')"></span>
      <button class="fc-icon-btn" style="background:transparent" @click="dismissDisclaimer = true"><AppIcon name="close" /></button>
    </div>

    <!-- KPI strip -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px">
      <div class="fc-kpi" style="border-top:3px solid #00A651">
        <div class="fc-kpi-label">{{ t('fincontrol.pnl.revenue') }}</div>
        <div class="fc-kpi-value green">320 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge green">▲ 8.2%</span></div>
        <div class="fc-kpi-sub">{{ t('fincontrol.pnl.aprPrefix') }}: 295 700 000 UZS</div>
        <FcSparkline :data="[265,278,270,295,308,320]" color="#00A651" :height="34" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #003D7C">
        <div class="fc-kpi-label">{{ t('fincontrol.pnl.grossProfit') }}</div>
        <div class="fc-kpi-value navy">122 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge blue">{{ t('fincontrol.pnl.margin38') }}</span><span class="fc-badge green">▲ 15%</span></div>
        <div class="fc-kpi-sub">{{ t('fincontrol.pnl.aprPrefix') }}: 106 100 000 UZS</div>
        <FcSparkline :data="[95,102,96,108,106,122]" color="#003D7C" :height="34" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #0054A6">
        <div class="fc-kpi-label">{{ t('fincontrol.pnl.operProfit') }}</div>
        <div class="fc-kpi-value navy">77 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge blue">{{ t('fincontrol.pnl.margin24') }}</span></div>
        <div class="fc-kpi-sub">{{ t('fincontrol.pnl.aprPrefix') }}: 68 400 000 UZS</div>
        <FcSparkline :data="[58,62,55,64,65,77]" color="#0054A6" :height="34" />
      </div>
      <div class="fc-kpi" style="border-top:3px solid #F59E0B">
        <div class="fc-kpi-label">{{ t('fincontrol.pnl.netProfit') }}</div>
        <div class="fc-kpi-value amber">~ 65 000 000 <span style="font-size:12px;opacity:.55">UZS</span></div>
        <div class="flex items-center gap-2" style="margin-top:4px"><span class="fc-badge amber">{{ t('fincontrol.pnl.estimated') }}</span></div>
        <div class="fc-kpi-sub">{{ t('fincontrol.pnl.marginEst') }}</div>
        <FcSparkline :data="[38,44,40,50,56,65]" color="#F59E0B" :height="34" />
      </div>
    </div>

    <!-- Main grid: P&L table + Trend chart -->
    <div style="display:grid;grid-template-columns:1.6fr 1fr;gap:16px;margin-bottom:18px">
      <div class="fc-card" style="padding:0;overflow:hidden">
        <div class="fc-card-header" style="padding:18px 18px 8px">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.pnl.tableTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.pnl.tableSub') }}</div>
          </div>
          <span class="flex items-center gap-1" style="font-size:11px;color:#6B7A99"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#F59E0B"></span> {{ t('fincontrol.pnl.estLegend') }}</span>
        </div>
        <table class="fc-table">
          <thead>
            <tr><th>{{ t('fincontrol.pnl.colItem') }}</th><th style="text-align:right">{{ t('fincontrol.pnl.colMay') }}</th><th style="text-align:right">{{ t('fincontrol.pnl.colApr') }}</th><th style="text-align:right">Δ%</th></tr>
          </thead>
          <tbody>
            <template v-for="(row, i) in pnlRows" :key="i">
              <tr v-if="row.type === 'group'" class="group-row"><td colspan="4">{{ row.label }}</td></tr>
              <tr v-else-if="row.type === 'result'" class="result-row" :class="row.tone">
                <td>
                  {{ row.label }}
                  <span v-if="row.meta" style="font-weight:600;font-size:11px;opacity:.7;margin-left:6px">[{{ row.meta }}]</span>
                  <span v-if="row.estimated" class="fc-badge amber" style="margin-left:6px">{{ t('fincontrol.pnl.estimated') }}</span>
                </td>
                <td style="text-align:right" class="fc-num">{{ row.may }}</td>
                <td style="text-align:right;opacity:.7" class="fc-num">{{ row.apr }}</td>
                <td style="text-align:right"><span class="fc-badge" :class="row.deltaTone">{{ row.delta }}</span></td>
              </tr>
              <tr v-else class="clickable">
                <td style="padding-left:24px">
                  <span v-if="row.icon" style="margin-right:6px">{{ row.icon }}</span>
                  {{ row.label }}
                  <span v-if="row.estimated" class="fc-badge amber" style="margin-left:6px">{{ t('fincontrol.pnl.estimated') }}</span>
                  <span v-if="row.warning" class="fc-badge red" style="margin-left:6px">⚠ {{ row.warning }}</span>
                </td>
                <td style="text-align:right" class="fc-num" :class="(row.may || '').startsWith('−') ? 'red' : 'green'">{{ row.may }}</td>
                <td style="text-align:right;color:#6B7A99" class="fc-num">{{ row.apr }}</td>
                <td style="text-align:right"><span class="fc-badge" :class="row.deltaTone">{{ row.delta }}</span></td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.pnl.trendTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.pnl.trendSub') }}</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;font-size:12px;color:#6B7A99;margin-bottom:8px">
          <span><span style="display:inline-block;width:18px;height:2.5px;background:#003D7C;margin-right:6px;vertical-align:middle"></span>{{ t('fincontrol.pnl.lblRevenue') }}</span>
          <span><span style="display:inline-block;width:18px;height:2.5px;background:#0054A6;margin-right:6px;vertical-align:middle"></span>{{ t('fincontrol.pnl.lblGross') }}</span>
          <span><span style="display:inline-block;width:18px;height:2.5px;background:#F59E0B;margin-right:6px;vertical-align:middle;border-bottom:1px dashed #F59E0B"></span>{{ t('fincontrol.pnl.lblNetEst') }}</span>
        </div>
        <FcChart type="line" :data="trendData" :options="trendOptions" :height="340" />
      </div>
    </div>

    <!-- Export card -->
    <div class="fc-card" style="border:2px dashed #DDE3EE;text-align:center;padding:24px">
      <div class="fc-card-title" style="font-size:16px">{{ t('fincontrol.pnl.exportTitle') }}</div>
      <div class="fc-card-sub" style="margin:6px 0 14px">{{ t('fincontrol.pnl.exportSub') }}</div>
      <div class="flex items-center justify-center gap-3">
        <button class="fc-export-btn" style="height:42px;padding:0 22px"><AppIcon name="picture_as_pdf" /> {{ t('fincontrol.pnl.exportPdf') }}</button>
        <button class="fc-export-btn green" style="height:42px;padding:0 22px"><AppIcon name="grid_on" /> {{ t('fincontrol.pnl.exportExcel') }}</button>
      </div>
    </div>
  </div>
</template>
