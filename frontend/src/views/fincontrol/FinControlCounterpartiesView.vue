<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import FcChart from '@/components/fincontrol/FcChart.vue'
import AppIcon from '@/components/AppIcon.vue'
import { makeCounterparties } from '@/data/fincontrol'

const { t, tm } = useI18n()

const counterparties = computed(() => makeCounterparties(t))

const filter = ref('all')
const showRiskBanner = ref(true)
const showAddModal = ref(false)
const detail = ref(null)

const detailChartData = computed(() => ({
  labels: tm('fincontrol.counterparties.detailMonths'),
  datasets: [{
    data: [4.8, 5.2, 6.1, 7.0, 8.4, 10.0],
    backgroundColor: 'rgba(0,166,81,.6)',
    borderColor: '#00A651',
    borderWidth: 1,
    borderRadius: 5,
  }],
}))
const detailChartOptions = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 10 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 10 }, callback: (v) => `${v}М` } },
  },
}

function open(cp) { detail.value = cp }
function close() { detail.value = null }

const primaryAction = computed(() => ({ label: t('fincontrol.counterparties.add'), icon: 'add' }))
const filterTabs = computed(() => [
  { k: 'all', l: t('fincontrol.counterparties.filterAll') },
  { k: 'payers', l: t('fincontrol.counterparties.filterPayers') },
  { k: 'recipients', l: t('fincontrol.counterparties.filterRecipients') },
  { k: 'regular', l: t('fincontrol.counterparties.filterRegular') },
])
</script>

<template>
  <FcHeader
    :title="t('fincontrol.counterparties.title')"
    :search="t('fincontrol.counterparties.search')"
    :primary-action="primaryAction"
    @primary="showAddModal = true"
  />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.counterparties.eyebrow') }}</div>
      <h1>{{ t('fincontrol.counterparties.title') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.counterparties.subtitle') }}</p>
    </div>

    <!-- KPI strip -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px">
      <div class="fc-kpi" style="border-top:3px solid #003D7C">
        <div class="fc-kpi-label">{{ t('fincontrol.counterparties.total') }}</div>
        <div class="fc-kpi-value navy">47</div>
        <div class="fc-kpi-sub">{{ t('fincontrol.counterparties.totalSub') }}</div>
      </div>
      <div class="fc-kpi" style="border-top:3px solid #00A651">
        <div class="fc-kpi-label">{{ t('fincontrol.counterparties.topPayer') }}</div>
        <div style="font-weight:700;font-size:15px;color:#1A2B4A">{{ t('fincontrol.data.cp.ipRashidov') }}</div>
        <div class="fc-kpi-value green" style="font-size:18px;margin-top:2px">35 600 000 <span style="font-size:11px;opacity:.55">UZS</span></div>
        <div class="fc-kpi-sub" style="color:#00A651">{{ t('fincontrol.counterparties.topPayerShare') }}</div>
      </div>
      <div class="fc-kpi" style="border-top:3px solid #F59E0B">
        <div class="fc-kpi-label">{{ t('fincontrol.counterparties.topReceiver') }}</div>
        <div style="font-weight:700;font-size:15px;color:#1A2B4A">{{ t('fincontrol.data.cp.arendaGroup') }}</div>
        <div class="fc-kpi-value amber" style="font-size:18px;margin-top:2px">12 800 000 <span style="font-size:11px;opacity:.55">UZS</span></div>
        <div class="fc-kpi-sub">{{ t('fincontrol.counterparties.receiverShare') }}</div>
      </div>
    </div>

    <!-- Risk banner -->
    <div v-if="showRiskBanner" class="fc-banner red" style="margin-bottom:18px;align-items:center">
      <AppIcon name="warning" />
      <span style="flex:1" v-html="t('fincontrol.counterparties.riskBanner')"></span>
      <button class="fc-icon-btn" style="background:transparent" @click="showRiskBanner = false"><AppIcon name="close" /></button>
    </div>

    <!-- Counterparties table -->
    <div class="fc-card" style="padding:0;overflow:hidden">
      <div class="fc-card-header" style="padding:18px 18px 14px">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.counterparties.allCpTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.counterparties.allCpSub') }}</div>
        </div>
        <div class="flex items-center gap-2">
          <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
            <button v-for="ft in filterTabs" :key="ft.k"
              class="fc-period-pill" :class="{active:filter===ft.k}" @click="filter=ft.k" style="font-size:11px;padding:4px 10px;border-radius:6px">{{ ft.l }}</button>
          </div>
          <select class="fc-select" style="width:auto;height:34px;font-size:12px;padding:0 10px"><option>{{ t('fincontrol.counterparties.sortBySum') }}</option><option>{{ t('fincontrol.counterparties.sortByName') }}</option><option>{{ t('fincontrol.counterparties.sortByTx') }}</option><option>{{ t('fincontrol.counterparties.sortByDate') }}</option></select>
          <span style="font-size:12px;color:#6B7A99">{{ t('fincontrol.counterparties.count47') }}</span>
        </div>
      </div>
      <table class="fc-table">
        <thead>
          <tr><th>{{ t('fincontrol.counterparties.colCounterparty') }}</th><th>{{ t('fincontrol.counterparties.colType') }}</th><th style="text-align:center">{{ t('fincontrol.counterparties.colTx') }}</th><th style="text-align:right">{{ t('fincontrol.counterparties.colTotalSum') }}</th><th>{{ t('fincontrol.counterparties.colLast') }}</th><th>{{ t('fincontrol.counterparties.colStatus') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="cp in counterparties" :key="cp.inn" class="clickable" @click="open(cp)">
            <td>
              <div class="flex items-center gap-3">
                <span class="fc-av" :class="cp.tone">{{ cp.initials }}</span>
                <div>
                  <div style="font-weight:700;font-size:13px;color:#1A2B4A">{{ cp.name }}</div>
                  <div style="font-size:11px;color:#6B7A99;font-family:'Manrope';font-variant-numeric:tabular-nums">{{ t('fincontrol.counterparties.innLabel') }}: {{ cp.inn }}</div>
                </div>
              </div>
            </td>
            <td><span class="fc-badge" :class="cp.typeTone">{{ cp.type }}</span></td>
            <td style="text-align:center;font-weight:700">{{ cp.tx }}</td>
            <td style="text-align:right" class="fc-num" :class="cp.amountTone">{{ cp.amount }}</td>
            <td style="font-size:12px;color:#6B7A99">{{ cp.last }}</td>
            <td><span class="fc-badge" :class="cp.statusTone">{{ cp.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <div style="display:flex;justify-content:space-between;padding:14px 18px;border-top:1px solid #DDE3EE">
        <button class="fc-cta-ghost" style="padding:6px 12px;font-size:12px"><AppIcon name="expand_more" /> {{ t('fincontrol.counterparties.loadMore') }}</button>
        <div class="flex items-center gap-1">
          <button class="fc-period-pill active" style="padding:4px 10px">1</button>
          <button class="fc-period-pill" style="padding:4px 10px">2</button>
          <button class="fc-period-pill" style="padding:4px 10px">3</button>
        </div>
      </div>
    </div>

    <!-- Slide panel -->
    <div class="fc-panel-overlay" :class="{ open: detail }" @click="close"></div>
    <aside class="fc-panel" :class="{ open: detail }">
      <template v-if="detail">
        <header class="fc-panel-head">
          <div class="flex items-center gap-3">
            <span class="fc-av" :class="detail.tone" style="width:48px;height:48px;font-size:16px;border-radius:12px">{{ detail.initials }}</span>
            <div>
              <div style="font-family:'Manrope';font-weight:800;font-size:18px;color:#003D7C">{{ detail.name }}</div>
              <div style="font-size:12px;color:#6B7A99">{{ t('fincontrol.counterparties.panelInn') }}: {{ detail.inn }} · <span class="fc-badge" :class="detail.statusTone" style="margin-left:4px">● {{ detail.status }}</span></div>
            </div>
          </div>
          <button class="fc-icon-btn" @click="close"><AppIcon name="close" /></button>
        </header>
        <div class="fc-panel-body">
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px">
            <div style="background:#F8FAFC;padding:12px;border-radius:9px;text-align:center">
              <div style="font-size:11px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px">{{ t('fincontrol.counterparties.panelTxLabel') }}</div>
              <div class="fc-num" style="color:#003D7C;font-size:18px">{{ detail.tx }}</div>
            </div>
            <div style="background:#F8FAFC;padding:12px;border-radius:9px;text-align:center">
              <div style="font-size:11px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px">{{ t('fincontrol.counterparties.panelTurnover') }}</div>
              <div class="fc-num" :class="detail.amountTone" style="font-size:18px">{{ detail.amount }}</div>
            </div>
            <div style="background:#F8FAFC;padding:12px;border-radius:9px;text-align:center">
              <div style="font-size:11px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px">{{ t('fincontrol.counterparties.panelLast') }}</div>
              <div class="fc-num" style="color:#003D7C;font-size:14px">{{ detail.last }}</div>
            </div>
          </div>

          <div class="fc-card-title" style="font-size:13px;margin-bottom:8px">{{ t('fincontrol.counterparties.income6m') }}</div>
          <FcChart type="bar" :data="detailChartData" :options="detailChartOptions" :height="180" />

          <div class="fc-card-title" style="font-size:13px;margin:18px 0 8px">{{ t('fincontrol.counterparties.txHistory') }}</div>
          <table class="fc-table" style="border-radius:8px;border:1px solid #DDE3EE">
            <tbody>
              <tr v-for="(tx, i) in [
                { date: t('fincontrol.counterparties.panelTx1Date'), desc: t('fincontrol.counterparties.panelTx1Desc'), acc: 'NBU •4402', cat: t('fincontrol.counterparties.panelTxCatSales'), amt: '+14 200 000' },
                { date: t('fincontrol.counterparties.panelTx2Date'), desc: t('fincontrol.counterparties.panelTx2Desc'), acc: 'NBU •4402', cat: t('fincontrol.counterparties.panelTxCatSales'), amt: '+10 000 000' },
                { date: t('fincontrol.counterparties.panelTx3Date'), desc: t('fincontrol.counterparties.panelTx3Desc'), acc: 'HBK •1192', cat: t('fincontrol.counterparties.panelTxCatSales'), amt: '+7 400 000' },
                { date: t('fincontrol.counterparties.panelTx4Date'), desc: t('fincontrol.counterparties.panelTx4Desc'), acc: 'NBU •4402', cat: t('fincontrol.counterparties.panelTxCatSales'), amt: '+4 000 000' },
              ]" :key="i">
                <td style="font-size:11.5px;color:#6B7A99">{{ tx.date }}</td>
                <td style="font-size:12px"><div>{{ tx.desc }}</div><div style="color:#6B7A99;font-size:10.5px">{{ tx.acc }} · {{ tx.cat }}</div></td>
                <td style="text-align:right" class="fc-num green">{{ tx.amt }}</td>
              </tr>
            </tbody>
          </table>

          <div class="fc-banner amber" style="margin-top:18px">
            <AppIcon name="auto_awesome" filled />
            <div v-html="t('fincontrol.counterparties.aiAnalysis')"></div>
          </div>
        </div>
        <footer class="fc-panel-foot">
          <button class="fc-cta-ghost">{{ t('fincontrol.counterparties.editBtn') }}</button>
          <button class="fc-cta-primary">{{ t('fincontrol.counterparties.allTxBtn') }}</button>
        </footer>
      </template>
    </aside>

    <!-- Add modal -->
    <div v-if="showAddModal" style="position:fixed;inset:0;background:rgba(15,23,42,.5);z-index:200;display:flex;align-items:center;justify-content:center" @click.self="showAddModal = false">
      <div style="background:white;border-radius:14px;padding:22px;max-width:480px;width:92%">
        <div class="flex items-center justify-between" style="margin-bottom:16px">
          <h3 class="fc-card-title" style="font-size:17px">{{ t('fincontrol.counterparties.addModalTitle') }}</h3>
          <button class="fc-icon-btn" @click="showAddModal = false"><AppIcon name="close" /></button>
        </div>
        <div class="fc-form-field"><label>{{ t('fincontrol.counterparties.nameLabel') }}</label><input class="fc-input" :placeholder="t('fincontrol.counterparties.namePh')" /></div>
        <div class="grid grid-cols-2 gap-3">
          <div class="fc-form-field"><label>{{ t('fincontrol.counterparties.innLabel') }}</label><input class="fc-input" :placeholder="t('fincontrol.counterparties.innPh')" maxlength="15" /></div>
          <div class="fc-form-field"><label>{{ t('fincontrol.counterparties.typeLabel') }}</label>
            <select class="fc-select"><option>{{ t('fincontrol.counterparties.typePayer') }}</option><option>{{ t('fincontrol.counterparties.typeRecipient') }}</option><option>{{ t('fincontrol.counterparties.typeBoth') }}</option><option>{{ t('fincontrol.counterparties.typeGov') }}</option></select>
          </div>
        </div>
        <div class="fc-form-field"><label>{{ t('fincontrol.counterparties.orgFormLabel') }}</label>
          <select class="fc-select"><option>{{ t('fincontrol.counterparties.orgOoo') }}</option><option>{{ t('fincontrol.counterparties.orgAo') }}</option><option selected>{{ t('fincontrol.counterparties.orgIp') }}</option><option>{{ t('fincontrol.counterparties.orgFl') }}</option><option>{{ t('fincontrol.counterparties.orgGov') }}</option></select>
        </div>
        <div class="fc-form-field"><label>{{ t('fincontrol.counterparties.commentLabel') }}</label><textarea class="fc-textarea" :placeholder="t('fincontrol.counterparties.commentPh')"></textarea></div>
        <div class="flex gap-3 justify-end" style="margin-top:16px">
          <button class="fc-cta-ghost" @click="showAddModal = false">{{ t('fincontrol.counterparties.cancel') }}</button>
          <button class="fc-cta-primary" @click="showAddModal = false">{{ t('fincontrol.counterparties.save') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>
