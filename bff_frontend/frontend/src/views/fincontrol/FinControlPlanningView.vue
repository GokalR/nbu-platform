<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import AppIcon from '@/components/AppIcon.vue'

const { t } = useI18n()

const showWarning = ref(true)
const showModal = ref(false)
const chartTab = ref('income')
const modalPeriod = ref('month')
const saveSuccess = ref(false)

const categories = ref([
  { key: 'purchases', nameKey: 'catPurchases', color: '#0054A6', plan: 55000000, fact: 61600000, tone: 'red', icon: 'inventory_2' },
  { key: 'salary', nameKey: 'catSalary', color: '#00A651', plan: 50000000, fact: 50500000, tone: 'amber', icon: 'person' },
  { key: 'tax', nameKey: 'catTax', color: '#F59E0B', plan: 30000000, fact: 27600000, tone: 'green', icon: 'star' },
  { key: 'rent', nameKey: 'catRent', color: '#E0384B', plan: 25000000, fact: 24750000, tone: 'green', icon: 'home' },
  { key: 'marketing', nameKey: 'catMarketing', color: '#A855F7', plan: 10000000, fact: 13200000, tone: 'red', icon: 'campaign', warn: true },
  { key: 'other', nameKey: 'catOther', color: '#94A3B8', plan: 10000000, fact: 8800000, tone: 'green', icon: 'more_horiz' },
])

const modalInputs = ref(categories.value.map((c) => ({ ...c })))

const fmt = (n) => n.toLocaleString('ru-RU')
const pct = (c) => Math.round((c.fact / c.plan) * 100)
const diff = (c) => c.plan - c.fact
const statusLabel = (tone) => (tone === 'red' ? t('fincontrol.planning.statusOverspend') : tone === 'amber' ? t('fincontrol.planning.statusEdge') : t('fincontrol.planning.statusNormal'))
const statusBadge = (tone) => (tone === 'red' ? 'red' : tone === 'amber' ? 'amber' : 'green')

const totalPlan = computed(() => categories.value.reduce((s, c) => s + c.plan, 0))
const totalFact = computed(() => categories.value.reduce((s, c) => s + c.fact, 0))
const totalDelta = computed(() => totalPlan.value - totalFact.value)
const totalPct = computed(() => Math.round((totalFact.value / totalPlan.value) * 100))
const modalTotal = computed(() => modalInputs.value.reduce((s, c) => s + Number(c.plan || 0), 0))

const days = Array.from({ length: 31 }, (_, i) => `${i + 1}`)
const todayIdx = 18

function buildChartData() {
  const planIncome = days.map((_, i) => 11.29 * (i + 1))
  const planExpense = days.map((_, i) => 5.8 * (i + 1))
  const planCf = planIncome.map((v, i) => v - planExpense[i])
  const factIncome = days.slice(0, todayIdx).map((_, i) => 11.29 * (i + 1) * 0.96 + (i % 3 === 0 ? 2 : 0))
  const factExpense = days.slice(0, todayIdx).map((_, i) => 5.8 * (i + 1) * 1.08 + (i % 4 === 0 ? 1 : 0))
  const factCf = factIncome.map((v, i) => v - factExpense[i])
  const forecastIncome = Array(todayIdx).fill(null).concat(days.slice(todayIdx).map((_, i) => 11.29 * (i + todayIdx + 1) * 0.96))
  const forecastExpense = Array(todayIdx).fill(null).concat(days.slice(todayIdx).map((_, i) => 5.8 * (i + todayIdx + 1) * 1.08))
  const forecastCf = forecastIncome.map((v, i) => (v == null ? null : v - forecastExpense[i]))
  const plan = chartTab.value === 'income' ? planIncome : chartTab.value === 'expense' ? planExpense : planCf
  const fact = chartTab.value === 'income' ? factIncome : chartTab.value === 'expense' ? factExpense : factCf
  const forecast = chartTab.value === 'income' ? forecastIncome : chartTab.value === 'expense' ? forecastExpense : forecastCf
  return {
    labels: days,
    datasets: [
      { label: t('fincontrol.planning.plan'), data: plan, borderColor: '#94A3B8', borderDash: [6, 4], borderWidth: 2, tension: 0.35, pointRadius: 0, fill: false },
      { label: t('fincontrol.planning.fact'), data: fact.concat(Array(31 - fact.length).fill(null)), borderColor: '#003D7C', backgroundColor: 'rgba(0,166,81,.13)', borderWidth: 2.5, tension: 0.35, pointRadius: 0, fill: true },
      { label: t('fincontrol.planning.forecast'), data: forecast, borderColor: '#003D7C', borderDash: [5, 4], borderWidth: 2, tension: 0.35, pointRadius: 0, fill: false },
    ],
  }
}
const chartData = computed(() => buildChartData())
const chartOptions = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 10 }, maxTicksLimit: 10 } },
    y: { grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 11 }, callback: (v) => `${v}М` } },
  },
}

function openModal() {
  modalInputs.value = categories.value.map((c) => ({ ...c }))
  showModal.value = true
}
function saveModal() {
  categories.value = categories.value.map((c, i) => ({ ...c, plan: Number(modalInputs.value[i].plan || 0) }))
  showModal.value = false
  saveSuccess.value = true
  setTimeout(() => { saveSuccess.value = false }, 2200)
}

const pills = computed(() => [
  { key: 'month', label: t('fincontrol.common.month') },
  { key: 'quarter', label: t('fincontrol.common.quarter') },
  { key: 'year', label: t('fincontrol.common.year') },
])
const secondaryAction = computed(() => ({ label: t('fincontrol.planning.editBudget'), icon: 'edit' }))
const primaryAction = computed(() => ({
  label: saveSuccess.value ? t('fincontrol.planning.planSaved') : t('fincontrol.planning.createPlan'),
  icon: saveSuccess.value ? 'check' : 'add',
}))
const modalPeriods = computed(() => [
  { k: 'month', l: t('fincontrol.common.month') },
  { k: 'quarter', l: t('fincontrol.common.quarter') },
  { k: 'year', l: t('fincontrol.common.year') },
])
</script>

<template>
  <FcHeader
    :title="t('fincontrol.planning.title')"
    :pills="pills"
    active-pill="month"
    :secondary-action="secondaryAction"
    :primary-action="primaryAction"
    @primary="openModal"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.planning.eyebrow') }}</div>
      <h1>{{ t('fincontrol.planning.pageTitle') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.planning.subtitle') }}</p>
    </div>

    <!-- Warning banner -->
    <div v-if="showWarning" class="fc-banner amber" style="margin-bottom:18px;align-items:center">
      <AppIcon name="warning" />
      <div style="flex:1">
        <b>{{ t('fincontrol.planning.warning') }}</b>
        <div style="font-size:12.5px;color:#6B7A99;margin-top:2px">{{ t('fincontrol.planning.warningText') }}</div>
      </div>
      <button class="fc-icon-btn" style="background:transparent" @click="showWarning = false"><AppIcon name="close" /></button>
    </div>

    <!-- KPI strip -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px">
      <div class="fc-kpi" style="border-top:3px solid #00A651">
        <div class="flex items-center justify-between" style="margin-bottom:8px">
          <div style="width:36px;height:36px;border-radius:9px;background:rgba(0,166,81,.12);display:flex;align-items:center;justify-content:center"><AppIcon name="trending_up" style="color:#00A651" /></div>
          <span class="fc-badge green">{{ t('fincontrol.planning.completedPct') }}</span>
        </div>
        <div class="fc-kpi-label">{{ t('fincontrol.planning.incomePlan') }}</div>
        <div class="flex items-baseline gap-2">
          <div class="fc-kpi-value green" style="font-size:22px">320 000 000</div>
          <span style="font-size:11px;color:#6B7A99">{{ t('fincontrol.planning.planSlashLabel') }}</span>
        </div>
        <div class="fc-bar" style="margin-top:10px"><div class="fc-bar-fill green" style="width:91%"></div></div>
        <div style="font-size:11px;color:#00A651;font-weight:700;margin-top:6px">{{ t('fincontrol.planning.done91') }}</div>
      </div>

      <div class="fc-kpi" style="border-top:3px solid #E0384B;background:rgba(224,56,75,.03)">
        <div class="flex items-center justify-between" style="margin-bottom:8px">
          <div style="width:36px;height:36px;border-radius:9px;background:rgba(224,56,75,.12);display:flex;align-items:center;justify-content:center"><AppIcon name="trending_down" style="color:#E0384B" /></div>
          <span class="fc-badge red">{{ t('fincontrol.planning.overspendBadge') }}</span>
        </div>
        <div class="fc-kpi-label">{{ t('fincontrol.planning.expensePlan') }}</div>
        <div class="flex items-baseline gap-2">
          <div class="fc-kpi-value red" style="font-size:22px">198 000 000</div>
          <span style="font-size:11px;color:#6B7A99">{{ t('fincontrol.planning.planSlashExpense') }}</span>
        </div>
        <div class="fc-bar" style="margin-top:10px;position:relative">
          <div class="fc-bar-fill red" style="width:100%"></div>
          <span style="position:absolute;right:-4px;top:-3px;width:10px;height:10px;border-radius:50%;background:#E0384B;border:2px solid white"></span>
        </div>
        <div style="font-size:11px;color:#E0384B;font-weight:700;margin-top:6px"><AppIcon name="warning" style="font-size:12px;vertical-align:middle" /> {{ t('fincontrol.planning.overspendAmount') }}</div>
      </div>

      <div class="fc-kpi" style="border-top:3px solid #003D7C">
        <div class="flex items-center justify-between" style="margin-bottom:8px">
          <div style="width:36px;height:36px;border-radius:9px;background:rgba(0,61,124,.12);display:flex;align-items:center;justify-content:center"><AppIcon name="schedule" style="color:#003D7C" /></div>
          <span class="fc-badge blue">{{ t('fincontrol.planning.daysLeft') }}</span>
        </div>
        <div class="fc-kpi-label">{{ t('fincontrol.planning.tillEndPeriod') }}</div>
        <div class="fc-kpi-value navy" style="font-size:32px">{{ t('fincontrol.planning.daysValue') }}</div>
        <div style="font-size:11px;color:#6B7A99;margin-top:2px" v-html="t('fincontrol.planning.balanceLeft')"></div>
        <div class="fc-bar" style="margin-top:10px"><div class="fc-bar-fill blue" style="width:58%"></div></div>
        <div class="flex items-center justify-between" style="font-size:10.5px;color:#6B7A99;margin-top:4px">
          <span>{{ t('fincontrol.planning.day18') }}</span><span style="color:#003D7C;font-weight:700">{{ t('fincontrol.planning.today') }}</span><span>{{ t('fincontrol.planning.day31') }}</span>
        </div>
      </div>
    </div>

    <!-- Main grid -->
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:18px">
      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.planning.chartTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.planning.chartSub') }}</div>
          </div>
          <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
            <button class="fc-period-pill" :class="{active:chartTab==='income'}" @click="chartTab='income'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.planning.chartIncome') }}</button>
            <button class="fc-period-pill" :class="{active:chartTab==='expense'}" @click="chartTab='expense'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.planning.chartExpense') }}</button>
            <button class="fc-period-pill" :class="{active:chartTab==='cf'}" @click="chartTab='cf'" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ t('fincontrol.planning.chartCf') }}</button>
          </div>
        </div>
        <div style="display:flex;gap:14px;margin-bottom:8px;font-size:12px;color:#6B7A99">
          <span><span style="display:inline-block;width:18px;height:2.5px;background:#003D7C;margin-right:6px;vertical-align:middle"></span>{{ t('fincontrol.planning.fact') }}</span>
          <span><span style="display:inline-block;width:18px;height:2.5px;border-top:2px dashed #94A3B8;margin-right:6px;vertical-align:middle"></span>{{ t('fincontrol.planning.plan') }}</span>
          <span><span style="display:inline-block;width:18px;height:2.5px;border-top:2px dashed #003D7C;margin-right:6px;vertical-align:middle"></span>{{ t('fincontrol.planning.forecast') }}</span>
        </div>
        <FcChart type="line" :data="chartData" :options="chartOptions" :height="290" />
      </div>

      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.planning.budgetCatTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.planning.budgetCatSub') }}</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <div v-for="c in categories" :key="c.key"
            :style="c.tone === 'red' ? 'background:rgba(224,56,75,.06);padding:10px;border-radius:9px;margin:-10px -10px 0' : c.tone === 'amber' ? 'background:rgba(245,158,11,.06);padding:10px;border-radius:9px;margin:-10px -10px 0' : ''">
            <div class="flex items-center gap-2" style="margin-bottom:6px">
              <span :style="{ width:'10px', height:'10px', borderRadius:'2px', background:c.color }"></span>
              <span style="flex:1;font-weight:600;font-size:13px;color:#1A2B4A">{{ t('fincontrol.planning.' + c.nameKey) }}</span>
              <AppIcon v-if="c.warn" name="warning" style="color:#E0384B;font-size:14px" />
              <span class="fc-num" :class="statusBadge(c.tone)" style="font-size:13px">{{ pct(c) }}%</span>
            </div>
            <div class="fc-bar"><div class="fc-bar-fill" :class="c.tone === 'red' ? 'red' : c.tone === 'amber' ? 'amber' : 'green'" :style="{ width: Math.min(pct(c), 100) + '%' }"></div></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Budget table -->
    <div class="fc-card" style="padding:0;overflow:hidden">
      <div class="fc-card-header" style="padding:18px 18px 14px">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.planning.detailBudgetTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.planning.detailBudgetSub') }}</div>
        </div>
        <div class="flex items-center gap-2">
          <span style="font-size:11px;color:#6B7A99">{{ t('fincontrol.planning.allInUzs') }}</span>
          <button class="fc-cta-ghost" style="height:30px;padding:0 10px;font-size:11px"><AppIcon name="file_download" /> {{ t('fincontrol.planning.export') }}</button>
        </div>
      </div>
      <table class="fc-table">
        <thead>
          <tr><th>{{ t('fincontrol.planning.colCategory') }}</th><th style="text-align:right">{{ t('fincontrol.planning.colPlanSum') }}</th><th style="text-align:right">{{ t('fincontrol.planning.colFact') }}</th><th style="text-align:right">{{ t('fincontrol.planning.colRemainder') }}</th><th style="text-align:right">%</th><th>{{ t('fincontrol.planning.colStatus') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in categories" :key="c.key"
            :style="c.tone === 'red' ? 'background:rgba(224,56,75,.04)' : c.tone === 'amber' ? 'background:rgba(245,158,11,.04)' : ''">
            <td>
              <div class="flex items-center gap-2">
                <span :style="{ width:'10px', height:'10px', borderRadius:'2px', background:c.color }"></span>
                <span style="font-weight:600">{{ t('fincontrol.planning.' + c.nameKey) }}</span>
                <AppIcon v-if="c.warn" name="warning" style="color:#E0384B;font-size:14px" />
              </div>
            </td>
            <td style="text-align:right">
              <input
                type="number"
                v-model.number="c.plan"
                class="fc-input"
                style="width:140px;height:30px;font-size:12px;text-align:right;background:#EEF4FF;padding:0 8px"
              />
            </td>
            <td style="text-align:right" class="fc-num" :class="c.tone === 'red' ? 'red' : ''">{{ fmt(c.fact) }}</td>
            <td style="text-align:right" class="fc-num" :class="diff(c) < 0 ? 'red' : 'green'">{{ diff(c) >= 0 ? '+' : '' }}{{ fmt(diff(c)) }}</td>
            <td style="text-align:right" class="fc-num" :class="statusBadge(c.tone)">{{ pct(c) }}%</td>
            <td><span class="fc-badge" :class="statusBadge(c.tone)">{{ statusLabel(c.tone) }}</span></td>
          </tr>
          <tr style="background:#F8FAFC;font-weight:700">
            <td>{{ t('fincontrol.planning.totalRow') }}</td>
            <td style="text-align:right" class="fc-num">{{ fmt(totalPlan) }}</td>
            <td style="text-align:right" class="fc-num red">{{ fmt(totalFact) }}</td>
            <td style="text-align:right" class="fc-num red">{{ fmt(totalDelta) }}</td>
            <td style="text-align:right" class="fc-num red">{{ totalPct }}%</td>
            <td><span class="fc-badge red">{{ t('fincontrol.planning.statusOverspend') }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create plan modal -->
    <div v-if="showModal" style="position:fixed;inset:0;background:rgba(15,23,42,.5);backdrop-filter:blur(4px);z-index:200;display:flex;align-items:center;justify-content:center" @click.self="showModal = false">
      <div style="background:white;border-radius:14px;padding:22px;width:540px;max-width:92%;max-height:90vh;overflow:auto">
        <div class="flex items-center justify-between" style="margin-bottom:16px">
          <h3 class="fc-card-title" style="font-size:17px">{{ t('fincontrol.planning.modalTitle') }}</h3>
          <button class="fc-icon-btn" @click="showModal = false"><AppIcon name="close" /></button>
        </div>

        <div style="font-size:11px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">{{ t('fincontrol.planning.periodType') }}</div>
        <div style="display:flex;background:#F0F4FA;border-radius:9px;padding:3px;margin-bottom:14px">
          <button v-for="p in modalPeriods" :key="p.k"
            class="fc-period-pill" :class="{active:modalPeriod===p.k}" @click="modalPeriod=p.k"
            style="flex:1;font-size:13px;padding:8px 12px;border-radius:7px">{{ p.l }}</button>
        </div>

        <div class="grid grid-cols-2 gap-3" style="margin-bottom:14px">
          <div class="fc-form-field"><label>{{ t('fincontrol.planning.periodStart') }}</label><input class="fc-input" type="date" value="2026-05-01" /></div>
          <div class="fc-form-field"><label>{{ t('fincontrol.planning.periodEnd') }}</label><input class="fc-input" type="date" value="2026-05-31" /></div>
        </div>

        <div style="font-size:13px;font-weight:700;color:#1A2B4A;margin-bottom:8px">{{ t('fincontrol.planning.planByCats') }}</div>
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px">
          <div v-for="c in modalInputs" :key="c.key" class="flex items-center gap-3" style="background:#F8FAFC;padding:8px;border-radius:9px">
            <div :style="{ width:'32px', height:'32px', borderRadius:'8px', background:c.color+'22', display:'flex', alignItems:'center', justifyContent:'center' }">
              <AppIcon :name="c.icon" :style="{ color: c.color, fontSize: '16px' }" />
            </div>
            <span style="flex:1;font-weight:600;font-size:13px;color:#1A2B4A">{{ t('fincontrol.planning.' + c.nameKey) }}</span>
            <input type="number" v-model.number="c.plan" class="fc-input" style="width:140px;height:32px;font-size:12px;text-align:right" />
          </div>
        </div>

        <div style="background:rgba(0,61,124,.08);padding:12px 14px;border-radius:10px;display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
          <span style="font-size:12px;color:#003D7C;font-weight:600">{{ t('fincontrol.planning.totalPlanExpenses') }}</span>
          <span class="fc-num" style="color:#003D7C;font-size:18px">{{ fmt(modalTotal) }} UZS</span>
        </div>

        <div class="flex gap-3 justify-end">
          <button class="fc-cta-ghost" @click="showModal = false">{{ t('fincontrol.planning.cancel') }}</button>
          <button class="fc-cta-primary" @click="saveModal">{{ t('fincontrol.planning.saveBtn') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>
