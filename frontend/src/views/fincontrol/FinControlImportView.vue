<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcHeader from '@/components/fincontrol/FcHeader.vue'
import AppIcon from '@/components/AppIcon.vue'

const { t } = useI18n()

const selectedBank = ref('Hamkorbank')
const fileName = ref(t('fincontrol.import.defaultFileName'))
const analyzing = ref(false)
const showPreview = ref(true)
const toast = ref(null)

const previewRows = computed(() => [
  { date: t('fincontrol.import.prevDate1'), name: 'Asiatech Logistics', av: 'AT', avTone: 'blue', amount: '−45 200 000', tone: 'red', category: t('fincontrol.import.catPurchases'), confLabel: t('fincontrol.import.confHigh'), conf: 94, confTone: 'green' },
  { date: t('fincontrol.import.prevDate2'), name: t('fincontrol.import.prevName2'), av: 'ОС', avTone: 'green', amount: '+120 000 000', tone: 'green', category: t('fincontrol.import.catRevenue'), confLabel: t('fincontrol.import.confHigh'), conf: 98, confTone: 'green' },
  { date: t('fincontrol.import.prevDate3'), name: t('fincontrol.import.prevName3'), av: 'НФ', avTone: 'purple', amount: '−12 800 000', tone: 'red', category: t('fincontrol.import.catTaxes'), confLabel: t('fincontrol.import.confHigh'), conf: 91, confTone: 'green' },
  { date: t('fincontrol.import.prevDate4'), name: t('fincontrol.import.prevName4'), av: 'ТК', avTone: 'amber', amount: '−8 500 000', tone: 'red', category: t('fincontrol.import.catEquipmentQ'), confLabel: t('fincontrol.import.confMedium'), conf: 62, confTone: 'amber', rowBg: 'rgba(245,158,11,.06)' },
  { date: t('fincontrol.import.prevDate5'), name: 'Asiatech Logistics', av: 'АТ', avTone: 'red', amount: '−45 200 000', tone: 'red', category: t('fincontrol.import.catPurchases'), duplicate: true, conf: 30, confTone: 'red', rowBg: 'rgba(224,56,75,.06)' },
  { date: t('fincontrol.import.prevDate6'), name: t('fincontrol.import.prevName6'), av: 'НН', avTone: 'slate', amount: '−3 200 000', tone: 'red', category: t('fincontrol.import.catOtherQ'), confLabel: t('fincontrol.import.confMedium'), conf: 54, confTone: 'amber', rowBg: 'rgba(245,158,11,.06)' },
  { date: t('fincontrol.import.prevDate7'), name: t('fincontrol.import.prevName7'), av: 'УТ', avTone: 'blue', amount: '−1 850 000', tone: 'red', category: t('fincontrol.import.catComms'), confLabel: t('fincontrol.import.confHigh'), conf: 87, confTone: 'green' },
])

const history = computed(() => [
  { date: t('fincontrol.import.histDate1'), bank: 'Hamkorbank', bankColor: '#F97316', period: t('fincontrol.import.histPeriod1'), count: 47, status: t('fincontrol.import.statusImported'), statusTone: 'green', action: 'delete' },
  { date: t('fincontrol.import.histDate2'), bank: 'NBU Institutional', bankColor: '#003D7C', period: t('fincontrol.import.histPeriod2'), count: null, status: t('fincontrol.import.statusProcessing'), statusTone: 'blue', action: 'cancel' },
  { date: t('fincontrol.import.histDate3'), bank: 'Hamkorbank', bankColor: '#F97316', period: t('fincontrol.import.histPeriod3'), count: 124, status: t('fincontrol.import.statusImported'), statusTone: 'green', action: 'delete' },
  { date: t('fincontrol.import.histDate4'), bank: 'Ipoteka Bank', bankColor: '#0054A6', period: t('fincontrol.import.histPeriod4'), count: null, status: t('fincontrol.import.statusError'), statusTone: 'red', action: 'delete' },
  { date: t('fincontrol.import.histDate5'), bank: 'NBU Institutional', bankColor: '#003D7C', period: t('fincontrol.import.histPeriod5'), count: 209, status: t('fincontrol.import.statusImported'), statusTone: 'green', action: 'delete' },
])

function showToast(text, tone = 'green') {
  toast.value = { text, tone }
  setTimeout(() => { toast.value = null }, 3000)
}
function analyze() {
  if (!fileName.value) return
  analyzing.value = true
  setTimeout(() => {
    analyzing.value = false
    showPreview.value = true
    showToast(t('fincontrol.import.toastAnalyzed'))
  }, 2000)
}
function confirmImport() {
  showPreview.value = false
  showToast(t('fincontrol.import.toastImported'))
}
function removeFile() {
  fileName.value = ''
  showPreview.value = false
}
</script>

<template>
  <FcHeader :title="t('fincontrol.import.title')" />

  <div class="fc-content">
    <div class="fc-page-title">
      <div class="eyebrow">{{ t('fincontrol.import.eyebrow') }}</div>
      <h1>{{ t('fincontrol.import.pageTitle') }}</h1>
      <p class="subtitle"><span class="fc-green-line"></span>{{ t('fincontrol.import.subtitle') }}</p>
    </div>

    <!-- Source cards -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px">
      <div class="fc-card" style="border-top:3px solid #00A651;background:linear-gradient(180deg,rgba(0,166,81,.04),white)">
        <div class="flex items-center gap-3" style="margin-bottom:10px">
          <div style="width:42px;height:42px;border-radius:10px;background:linear-gradient(135deg,#003D7C,#0054A6);color:white;display:flex;align-items:center;justify-content:center;font-family:'Manrope';font-weight:800;font-size:12px">НБУ</div>
          <div style="flex:1">
            <div style="font-weight:700;font-size:14px;color:#1A2B4A">{{ t('fincontrol.import.nbuName') }}</div>
            <div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.import.nbuSub') }}</div>
          </div>
          <span class="fc-badge green">{{ t('fincontrol.import.auto') }}</span>
        </div>
        <div class="flex items-center gap-2" style="font-size:12px;color:#6B7A99;margin-bottom:12px">
          <span style="width:8px;height:8px;border-radius:50%;background:#00A651;box-shadow:0 0 0 0 rgba(0,166,81,.4);animation:fc-pulse 1.8s infinite"></span>
          {{ t('fincontrol.import.syncActive') }}
        </div>
        <div class="flex gap-2">
          <button class="fc-cta-ghost" style="flex:1;padding:6px 10px;font-size:12px"><AppIcon name="refresh" /> {{ t('fincontrol.import.sync') }}</button>
          <button class="fc-cta-ghost" style="padding:6px 10px;font-size:12px"><AppIcon name="settings" /></button>
        </div>
      </div>

      <div class="fc-card">
        <div class="flex items-center gap-3" style="margin-bottom:10px">
          <div style="width:42px;height:42px;border-radius:10px;background:linear-gradient(135deg,#F59E0B,#F97316);color:white;display:flex;align-items:center;justify-content:center;font-family:'Manrope';font-weight:800;font-size:13px">HB</div>
          <div style="flex:1">
            <div style="font-weight:700;font-size:14px;color:#1A2B4A">{{ t('fincontrol.import.hbName') }}</div>
            <div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.import.hbSub') }}</div>
          </div>
          <span class="fc-badge amber">{{ t('fincontrol.import.manual') }}</span>
        </div>
        <div class="flex items-center gap-2" style="font-size:12px;color:#6B7A99;margin-bottom:12px">
          <AppIcon name="schedule" style="font-size:14px" />
          {{ t('fincontrol.import.lastUpload') }}
        </div>
        <div class="flex gap-2">
          <button class="fc-cta-ghost" style="flex:1;padding:6px 10px;font-size:12px"><AppIcon name="refresh" /> {{ t('fincontrol.import.refresh') }}</button>
          <button class="fc-cta-ghost" style="padding:6px 10px;font-size:12px;color:#E0384B">{{ t('fincontrol.import.disconnect') }}</button>
        </div>
      </div>

      <div class="fc-card" style="border:2px dashed #DDE3EE;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;cursor:pointer" @click="showToast(t('fincontrol.import.addSourceToast'), 'blue')">
        <div style="width:48px;height:48px;border-radius:12px;background:#F0F4FA;display:flex;align-items:center;justify-content:center;margin-bottom:10px">
          <AppIcon name="add" style="color:#6B7A99;font-size:24px" />
        </div>
        <div style="font-weight:700;font-size:14px;color:#1A2B4A;margin-bottom:4px">{{ t('fincontrol.import.addSource') }}</div>
        <div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.import.addSourceSub') }}</div>
      </div>
    </div>

    <!-- Preview -->
    <div v-if="showPreview" class="fc-card" style="padding:0;overflow:hidden;margin-bottom:18px;border:1px solid rgba(0,166,81,.3)">
      <div class="flex items-center gap-3" style="background:rgba(0,166,81,.08);padding:14px 18px;border-bottom:1px solid #DDE3EE">
        <div style="width:36px;height:36px;border-radius:9px;background:rgba(0,166,81,.15);display:flex;align-items:center;justify-content:center">
          <AppIcon name="description" style="color:#00A651" />
        </div>
        <div style="flex:1">
          <div style="font-weight:700;font-size:14px;color:#1A2B4A">{{ fileName }}</div>
          <div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.import.fileInfoStatic') }}</div>
        </div>
        <button class="fc-icon-btn" @click="showPreview = false"><AppIcon name="close" /></button>
      </div>

      <div class="fc-banner amber" style="margin:12px 18px;border-radius:9px">
        <AppIcon name="warning" />
        <span v-html="t('fincontrol.import.duplicates')"></span>
      </div>

      <table class="fc-table">
        <thead>
          <tr><th>{{ t('fincontrol.import.colDate') }}</th><th>{{ t('fincontrol.import.colCounterparty') }}</th><th style="text-align:right">{{ t('fincontrol.import.colAmount') }}</th><th>{{ t('fincontrol.import.colCategoryAi') }}</th><th>{{ t('fincontrol.import.colConfidence') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in previewRows" :key="i" :style="r.rowBg ? { background: r.rowBg } : {}">
            <td style="font-size:12px;color:#6B7A99">{{ r.date }}</td>
            <td>
              <div class="flex items-center gap-2">
                <span class="fc-av" :class="r.avTone" style="width:26px;height:26px;font-size:10px">{{ r.av }}</span>
                <span style="font-weight:600;font-size:13px">{{ r.name }}</span>
              </div>
            </td>
            <td style="text-align:right" class="fc-num" :class="r.tone === 'green' ? 'green' : 'red'">{{ r.amount }}</td>
            <td>
              <span v-if="r.duplicate" class="fc-badge red"><AppIcon name="warning" style="font-size:12px" /> {{ t('fincontrol.import.duplicate') }}</span>
              <span v-else style="display:inline-flex;align-items:center;gap:6px;font-size:12px">
                <span class="fc-badge purple" style="font-size:10px">AI</span>
                {{ r.category }}
              </span>
            </td>
            <td style="min-width:160px">
              <div class="flex items-center gap-2">
                <span style="font-size:11px;color:#6B7A99;min-width:70px">{{ r.confLabel || '' }} {{ r.conf }}%</span>
                <div class="fc-bar" style="flex:1"><div class="fc-bar-fill" :class="r.confTone" :style="{ width: r.conf + '%' }"></div></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div style="display:flex;justify-content:space-between;align-items:center;background:#FAFBFD;padding:14px 18px;border-top:1px solid #DDE3EE">
        <span style="font-size:12px;color:#6B7A99">{{ t('fincontrol.import.shown7of47') }}</span>
        <div class="flex gap-3">
          <button class="fc-cta-ghost" @click="showPreview = false">{{ t('fincontrol.import.cancel') }}</button>
          <button class="fc-cta-primary" @click="confirmImport"><AppIcon name="download" /> {{ t('fincontrol.import.confirmImport') }}</button>
        </div>
      </div>
    </div>

    <!-- Main grid: upload + instructions -->
    <div style="display:grid;grid-template-columns:7fr 5fr;gap:16px;margin-bottom:18px">
      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.import.uploadTitle') }}</div>
            <div class="fc-card-sub">{{ t('fincontrol.import.uploadSub') }}</div>
          </div>
          <span class="fc-badge blue"><AppIcon name="auto_awesome" filled style="font-size:12px" /> {{ t('fincontrol.import.aiCategorization') }}</span>
        </div>

        <div class="fc-form-field">
          <label>{{ t('fincontrol.import.chooseBank') }}</label>
          <select class="fc-select" v-model="selectedBank">
            <option>Kapitalbank</option>
            <option>Hamkorbank</option>
            <option>Ipoteka Bank</option>
            <option>Asaka Bank</option>
            <option>{{ t('fincontrol.import.bankOther') }}</option>
          </select>
        </div>

        <div :style="`border:2px dashed ${fileName ? '#00A651' : '#DDE3EE'};border-radius:11px;padding:28px;text-align:center;background:${fileName ? 'rgba(0,166,81,.04)' : '#FAFBFD'};margin:12px 0 14px`">
          <div v-if="!fileName">
            <div style="width:52px;height:52px;border-radius:13px;background:#EEF4FF;display:flex;align-items:center;justify-content:center;margin:0 auto 10px">
              <AppIcon name="cloud_upload" style="color:#003D7C;font-size:26px" />
            </div>
            <div style="font-weight:700;color:#1A2B4A;font-size:15px;margin-bottom:4px">{{ t('fincontrol.import.dropTitle') }}</div>
            <div style="font-size:12px;color:#6B7A99;margin-bottom:14px">{{ t('fincontrol.import.dropSub') }}</div>
            <button class="fc-cta-primary" style="padding:8px 18px" @click="fileName = t('fincontrol.import.defaultFileName')">{{ t('fincontrol.import.chooseFile') }}</button>
          </div>
          <div v-else>
            <div style="width:52px;height:52px;border-radius:13px;background:rgba(0,166,81,.15);display:flex;align-items:center;justify-content:center;margin:0 auto 10px">
              <AppIcon name="check_circle" filled style="color:#00A651;font-size:26px" />
            </div>
            <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(0,166,81,.1);color:#00A651;padding:6px 12px;border-radius:20px;font-weight:700;font-size:13px;margin-bottom:6px">
              <AppIcon name="description" /> {{ fileName }}
            </div>
            <div><button class="fc-link" style="color:#E0384B;font-size:12px" @click="removeFile">{{ t('fincontrol.import.remove') }}</button></div>
          </div>
        </div>

        <div style="font-size:11px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">{{ t('fincontrol.import.supportedFmt') }}</div>
        <div class="flex gap-2" style="margin-bottom:10px">
          <span class="fc-badge green"><AppIcon name="check" style="font-size:11px" /> XLS</span>
          <span class="fc-badge green"><AppIcon name="check" style="font-size:11px" /> XLSX</span>
          <span class="fc-badge green"><AppIcon name="check" style="font-size:11px" /> CSV</span>
          <span class="fc-badge slate" style="text-decoration:line-through;opacity:.7">✕ PDF</span>
        </div>
        <div style="font-size:11.5px;color:#6B7A99;margin-bottom:14px" v-html="t('fincontrol.import.maxSize')"></div>

        <button class="fc-cta-primary" style="width:100%;padding:10px" :disabled="!fileName || analyzing" @click="analyze">
          <AppIcon :name="analyzing ? 'refresh' : 'cloud_upload'" :style="analyzing ? 'animation:fc-spin 1s linear infinite' : ''" />
          {{ analyzing ? t('fincontrol.import.analyzing') : t('fincontrol.import.uploadAndAnalyze') }}
        </button>
      </div>

      <div class="fc-card">
        <div class="fc-card-header">
          <div>
            <div class="fc-card-title">{{ t('fincontrol.import.instructions') }}</div>
          </div>
          <span style="font-size:11px;color:#6B7A99">{{ t('fincontrol.import.steps3') }}</span>
        </div>
        <div style="display:flex;flex-direction:column;gap:14px">
          <div v-for="(s, i) in [
            { t: t('fincontrol.import.step1Title'), d: t('fincontrol.import.step1Desc') },
            { t: t('fincontrol.import.step2Title'), d: t('fincontrol.import.step2Desc') },
            { t: t('fincontrol.import.step3Title'), d: t('fincontrol.import.step3Desc') },
          ]" :key="i" class="flex gap-3">
            <div style="width:28px;height:28px;border-radius:50%;background:#003D7C;color:white;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;flex-shrink:0">{{ i + 1 }}</div>
            <div>
              <div style="font-weight:700;font-size:13px;color:#1A2B4A;margin-bottom:2px">{{ s.t }}</div>
              <div style="font-size:12px;color:#6B7A99;line-height:1.5">{{ s.d }}</div>
            </div>
          </div>
        </div>

        <div style="border-top:1px solid #DDE3EE;margin:16px 0 10px"></div>
        <div style="font-size:11px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">{{ t('fincontrol.import.bankInstr') }}</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          <button v-for="b in ['NBU Institutional','Hamkorbank','Kapitalbank','Ipoteka Bank']" :key="b" class="fc-link" style="display:flex;justify-content:space-between;align-items:center;font-size:13px;padding:4px 0">
            <span>{{ b }}</span>
            <AppIcon name="open_in_new" style="font-size:14px" />
          </button>
        </div>
      </div>
    </div>

    <!-- Import history -->
    <div class="fc-card" style="padding:0;overflow:hidden">
      <div class="fc-card-header" style="padding:18px 18px 14px">
        <div>
          <div class="fc-card-title">{{ t('fincontrol.import.historyTitle') }}</div>
          <div class="fc-card-sub">{{ t('fincontrol.import.historySub') }}</div>
        </div>
        <button class="fc-cta-ghost" style="padding:6px 12px;font-size:12px"><AppIcon name="refresh" /> {{ t('fincontrol.import.refresh') }}</button>
      </div>
      <table class="fc-table">
        <thead>
          <tr><th>{{ t('fincontrol.import.histColDate') }}</th><th>{{ t('fincontrol.import.histColBank') }}</th><th>{{ t('fincontrol.import.histColPeriod') }}</th><th style="text-align:center">{{ t('fincontrol.import.histColTx') }}</th><th>{{ t('fincontrol.import.histColStatus') }}</th><th style="text-align:right">{{ t('fincontrol.import.histColActions') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="(h, i) in history" :key="i">
            <td style="font-size:12.5px">{{ h.date }}</td>
            <td>
              <span class="flex items-center gap-2">
                <span :style="{ width:'8px', height:'8px', borderRadius:'50%', background:h.bankColor }"></span>
                <span style="font-size:12.5px">{{ h.bank }}</span>
              </span>
            </td>
            <td style="font-size:12px;color:#6B7A99">{{ h.period }}</td>
            <td style="text-align:center;font-weight:700">{{ h.count ?? '—' }}</td>
            <td>
              <span class="fc-badge" :class="h.statusTone">
                <AppIcon v-if="h.statusTone === 'green'" name="check" style="font-size:11px" />
                <AppIcon v-else-if="h.statusTone === 'blue'" name="refresh" style="font-size:11px;animation:fc-spin 1.5s linear infinite" />
                <AppIcon v-else-if="h.statusTone === 'red'" name="close" style="font-size:11px" />
                {{ h.status }}
              </span>
            </td>
            <td style="text-align:right">
              <button class="fc-icon-btn" style="width:28px;height:28px">
                <AppIcon :name="h.action === 'cancel' ? 'close' : 'delete'" style="font-size:16px" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Toast -->
    <div v-if="toast" :style="`position:fixed;bottom:24px;right:24px;z-index:300;background:#1A2B4A;color:white;padding:12px 18px;border-radius:10px;border-left:3px solid ${toast.tone === 'green' ? '#00A651' : toast.tone === 'red' ? '#E0384B' : '#0054A6'};box-shadow:0 10px 30px rgba(0,0,0,.2);font-size:13px`">
      {{ toast.text }}
    </div>
  </div>
</template>

<style scoped>
@keyframes fc-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,166,81,.6); }
  50% { box-shadow: 0 0 0 6px rgba(0,166,81,0); }
}
@keyframes fc-spin {
  to { transform: rotate(360deg); }
}
</style>
