<script setup>
import { ref, nextTick, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import FcChart from '@/components/fincontrol/FcChart.vue'
import AppIcon from '@/components/AppIcon.vue'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
const inputText = ref('')
const messages = ref([])
const typing = ref(false)
const scrollRef = ref(null)

const quickQuestions = computed(() => [
  { icon: 'trending_up', text: t('fincontrol.ai.qExpenseGrowth') },
  { icon: 'schedule', text: t('fincontrol.ai.qCashGap') },
  { icon: 'group', text: t('fincontrol.ai.qTopPayer') },
  { icon: 'insights', text: t('fincontrol.ai.qCompare') },
  { icon: 'percent', text: t('fincontrol.ai.qTaxShare') },
  { icon: 'show_chart', text: t('fincontrol.ai.qCfTrend') },
])

const cannedAnswers = [
  { match: /расход|выросл|xarajat|o'sgan/i, kind: 'expenseGrowth' },
  { match: /сравн|поток|денеж|cf|solishtir|oqim/i, kind: 'cfCompare' },
  { match: /разрыв|кассов|ликвид|uzilish|kassa|likvid/i, kind: 'cashGap' },
  { match: /налог|зарплат|soliq|ish haqi/i, kind: 'taxShare' },
  { match: /контрагент|плательщик|поступ|kontragent|to'lovchi/i, kind: 'topPayer' },
]
let fallbackIdx = 0
const fallbackKinds = ['balance', 'topPayer', 'taxShare', 'cfTrend']

const seed = () => [
  { role: 'user', time: '10:14', text: t('fincontrol.ai.qExpenseGrowth') },
  { role: 'ai', time: '10:14', kind: 'expenseGrowth' },
  { role: 'user', time: '10:16', text: t('fincontrol.ai.qCompare') },
  { role: 'ai', time: '10:16', kind: 'cfCompare' },
  { role: 'user', time: '10:19', text: t('fincontrol.ai.qCashGap') },
  { role: 'ai', time: '10:19', kind: 'cashGap' },
]

messages.value = seed()

const hasMessages = computed(() => messages.value.length > 0)

const compareData = computed(() => ({
  labels: [t('fincontrol.ai.compareLblIncome'), t('fincontrol.ai.compareLblExpense'), t('fincontrol.ai.compareLblCf')],
  datasets: [
    { label: t('fincontrol.ai.dsAprApril'), data: [295, 173, 142], backgroundColor: 'rgba(0,61,124,.18)', borderColor: '#003D7C', borderWidth: 1.5, borderRadius: 4 },
    { label: t('fincontrol.ai.dsAprMay'), data: [320, 198, 122], backgroundColor: ['rgba(0,166,81,.55)', 'rgba(224,56,75,.55)', 'rgba(0,84,166,.55)'], borderColor: ['#00A651', '#E0384B', '#0054A6'], borderWidth: 1.5, borderRadius: 4 },
  ],
}))
const compareOptions = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6B7A99', font: { size: 10 } } },
    y: { grid: { color: '#F0F4FA' }, ticks: { color: '#6B7A99', font: { size: 10 }, callback: (v) => `${v}М` } },
  },
}

const obligations = computed(() => [
  { dot:'#F59E0B', name: t('fincontrol.ai.obligationVat'), date: t('fincontrol.ai.obligationVatDate'), amt:'−18 400 000 UZS' },
  { dot:'#00A651', name: t('fincontrol.ai.obligationSalary'), date: t('fincontrol.ai.obligationSalaryDate'), amt:'−50 000 000 UZS' },
  { dot:'#E0384B', name: t('fincontrol.ai.obligationRent'), date: t('fincontrol.ai.obligationRentDate'), amt:'−8 500 000 UZS' },
])

function nowTime() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
function scroll() {
  nextTick(() => {
    if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  })
}
function pickKind(text) {
  for (const c of cannedAnswers) if (c.match.test(text)) return c.kind
  const k = fallbackKinds[fallbackIdx % fallbackKinds.length]
  fallbackIdx += 1
  return k
}
function send(text) {
  const tt = (text ?? inputText.value).trim()
  if (!tt) return
  messages.value.push({ role: 'user', time: nowTime(), text: tt })
  inputText.value = ''
  typing.value = true
  scroll()
  setTimeout(() => {
    typing.value = false
    messages.value.push({ role: 'ai', time: nowTime(), kind: pickKind(tt) })
    scroll()
  }, 1500)
}
function newDialog() {
  messages.value = []
  typing.value = false
}
function onKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<template>
  <!-- Compact chat header (replaces FcHeader) -->
  <header class="fc-header" style="gap:14px">
    <div class="flex items-center gap-3" style="flex:1">
      <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#F59E0B,#F97316);display:flex;align-items:center;justify-content:center;color:white">
        <AppIcon name="auto_awesome" filled />
      </div>
      <div>
        <div style="font-family:'Manrope';font-weight:800;font-size:16px;color:#1A2B4A">{{ t('fincontrol.ai.headerTitle') }}</div>
        <div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.ai.headerSub') }}</div>
      </div>
    </div>

    <div style="display:flex;background:#F0F4FA;border-radius:8px;padding:2px">
      <button class="fc-period-pill" :class="{active:locale==='ru'}" @click="setLocale('ru')" style="font-size:11px;padding:4px 10px;border-radius:6px">RU</button>
      <button class="fc-period-pill" :class="{active:locale==='uz'}" @click="setLocale('uz')" style="font-size:11px;padding:4px 10px;border-radius:6px">UZ</button>
    </div>
    <button class="fc-primary-btn" @click="newDialog"><AppIcon name="add" /> {{ t('fincontrol.ai.newDialog') }}</button>
    <button class="fc-icon-btn"><AppIcon name="help" /></button>
    <div class="fc-avatar">АБ</div>
  </header>

  <div class="fc-content" style="padding:0;display:grid;grid-template-columns:264px 1fr;gap:0;height:calc(100vh - 60px);overflow:hidden">
    <!-- LEFT: Quick questions -->
    <aside style="background:white;border-right:1px solid #DDE3EE;padding:18px;overflow-y:auto">
      <div class="flex items-center gap-2" style="margin-bottom:3px">
        <AppIcon name="auto_awesome" filled style="color:#F59E0B" />
        <div style="font-family:'Manrope';font-weight:800;font-size:14px;color:#1A2B4A">{{ t('fincontrol.ai.quickQ') }}</div>
      </div>
      <div style="font-size:11px;color:#6B7A99;margin-bottom:14px">{{ t('fincontrol.ai.quickQSub') }}</div>

      <div style="display:flex;flex-direction:column;gap:6px">
        <button v-for="q in quickQuestions" :key="q.text"
          class="flex items-center gap-2" style="text-align:left;padding:9px 10px;border-radius:9px;background:#F8FAFC;border:1px solid transparent;cursor:pointer;transition:all .15s"
          @mouseover="(e) => { e.currentTarget.style.background = 'rgba(245,158,11,.08)'; e.currentTarget.style.borderColor = 'rgba(245,158,11,.2)' }"
          @mouseleave="(e) => { e.currentTarget.style.background = '#F8FAFC'; e.currentTarget.style.borderColor = 'transparent' }"
          @click="send(q.text)">
          <div style="width:28px;height:28px;border-radius:7px;background:rgba(245,158,11,.12);display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <AppIcon :name="q.icon" style="color:#F59E0B;font-size:15px" />
          </div>
          <span style="flex:1;font-size:12px;color:#1A2B4A;line-height:1.3">{{ q.text }}</span>
          <AppIcon name="chevron_right" style="color:#CBD5E8;font-size:16px" />
        </button>
      </div>

      <div style="border-top:1px solid #DDE3EE;margin:16px 0 12px"></div>
      <div style="font-size:10.5px;color:#6B7A99;text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin-bottom:8px">{{ t('fincontrol.ai.ctxTitle') }}</div>
      <div style="display:flex;flex-direction:column;gap:6px;font-size:12px">
        <div class="flex justify-between"><span style="color:#6B7A99">{{ t('fincontrol.ai.ctxPeriod') }}</span><span style="color:#1A2B4A;font-weight:600">{{ t('fincontrol.ai.ctxPeriodVal') }}</span></div>
        <div class="flex justify-between"><span style="color:#6B7A99">{{ t('fincontrol.ai.ctxAccounts') }}</span><span style="color:#1A2B4A;font-weight:600">{{ t('fincontrol.ai.ctxAccountsVal') }}</span></div>
        <div class="flex justify-between"><span style="color:#6B7A99">{{ t('fincontrol.ai.ctxCurrency') }}</span><span style="color:#1A2B4A;font-weight:600">UZS</span></div>
        <div class="flex justify-between"><span style="color:#6B7A99">{{ t('fincontrol.ai.ctxData') }}</span><button class="fc-link" style="font-size:12px">{{ t('fincontrol.ai.changePeriod') }}</button></div>
      </div>

      <div style="border-top:1px solid #DDE3EE;margin:16px 0 12px"></div>
      <div style="font-size:11.5px;color:#6B7A99;line-height:1.5" v-html="t('fincontrol.ai.aboutAi')"></div>

      <div style="font-size:10.5px;color:#94A3B8;font-style:italic;margin-top:18px;line-height:1.4">{{ t('fincontrol.ai.disclaimer') }}</div>
    </aside>

    <!-- CENTER: Chat -->
    <div style="display:flex;flex-direction:column;background:#F7F9FB;overflow:hidden">
      <!-- Chat sub-header -->
      <div class="flex items-center gap-3" style="padding:12px 20px;background:white;border-bottom:1px solid #DDE3EE">
        <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#F59E0B,#F97316);display:flex;align-items:center;justify-content:center;color:white">
          <AppIcon name="auto_awesome" filled />
        </div>
        <div style="flex:1">
          <div style="font-family:'Manrope';font-weight:800;font-size:14px;color:#1A2B4A">{{ t('fincontrol.ai.subTitle') }}</div>
          <div style="font-size:11px;color:#6B7A99">{{ t('fincontrol.ai.subSub') }}</div>
        </div>
        <span class="fc-badge blue">{{ locale.toUpperCase() }}</span>
        <div class="flex items-center gap-1">
          <span style="width:8px;height:8px;border-radius:50%;background:#00A651;animation:ai-pulse 1.8s infinite"></span>
          <span style="font-size:11px;color:#6B7A99">{{ t('fincontrol.ai.online') }}</span>
        </div>
      </div>

      <!-- Messages -->
      <div ref="scrollRef" style="flex:1;overflow-y:auto;padding:20px">
        <!-- Empty state -->
        <div v-if="!hasMessages" style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">
          <div style="width:72px;height:72px;border-radius:18px;background:rgba(245,158,11,.12);display:flex;align-items:center;justify-content:center;margin-bottom:16px;box-shadow:0 0 30px rgba(245,158,11,.25)">
            <AppIcon name="auto_awesome" filled style="color:#F59E0B;font-size:38px" />
          </div>
          <h2 style="font-family:'Manrope';font-weight:800;font-size:20px;color:#1A2B4A;margin-bottom:8px">{{ t('fincontrol.ai.emptyTitle') }}</h2>
          <p style="font-size:13.5px;color:#6B7A99;max-width:440px;margin-bottom:18px">{{ t('fincontrol.ai.emptySub') }}</p>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;max-width:560px">
            <button v-for="q in quickQuestions.slice(0,3)" :key="q.text"
              style="padding:12px;background:white;border:1px solid #DDE3EE;border-radius:11px;font-size:12px;color:#1A2B4A;cursor:pointer;text-align:left"
              @click="send(q.text)">
              <AppIcon :name="q.icon" style="color:#F59E0B;font-size:16px;margin-bottom:6px" />
              <div>{{ q.text }}</div>
            </button>
          </div>
        </div>

        <!-- Messages list -->
        <div v-else style="display:flex;flex-direction:column;gap:16px">
          <template v-for="(m, idx) in messages" :key="idx">
            <!-- USER -->
            <div v-if="m.role === 'user'" class="flex gap-2" style="justify-content:flex-end">
              <div style="max-width:70%">
                <div style="background:linear-gradient(135deg,#003D7C,#0054A6);color:white;padding:10px 14px;border-radius:14px 14px 4px 14px;font-size:13.5px;line-height:1.5">{{ m.text }}</div>
                <div style="font-size:10.5px;color:#94A3B8;margin-top:4px;text-align:right">{{ m.time }}</div>
              </div>
              <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#003D7C,#0054A6);color:white;font-family:'Manrope';font-weight:700;font-size:11px;display:flex;align-items:center;justify-content:center;flex-shrink:0">АБ</div>
            </div>

            <!-- AI -->
            <div v-else class="flex gap-2" style="align-items:flex-start">
              <div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#F59E0B,#F97316);display:flex;align-items:center;justify-content:center;color:white;flex-shrink:0">
                <AppIcon name="auto_awesome" filled style="font-size:18px" />
              </div>
              <div :style="`max-width:75%;background:white;border:1px solid #DDE3EE;padding:14px;border-radius:14px 14px 14px 4px;${m.kind === 'cashGap' ? 'border-left:3px solid #F59E0B;' : ''}`">
                <!-- Expense growth -->
                <template v-if="m.kind === 'expenseGrowth'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A;margin-bottom:10px" v-html="t('fincontrol.ai.expGrowthIntro')"></div>
                  <div style="border:1px solid #DDE3EE;border-radius:9px;overflow:hidden;margin-bottom:10px">
                    <table class="fc-table" style="margin:0">
                      <thead><tr><th>{{ t('fincontrol.ai.colCategory') }}</th><th style="text-align:right">{{ t('fincontrol.ai.colSum') }}</th><th style="text-align:right">{{ t('fincontrol.ai.colDeltaApr') }}</th></tr></thead>
                      <tbody>
                        <tr><td><span class="flex items-center gap-2"><span style="width:8px;height:8px;border-radius:50%;background:#A855F7"></span>{{ t('fincontrol.ai.labelMarketing') }}</span></td><td style="text-align:right" class="fc-num">13 200 000 UZS</td><td style="text-align:right"><span class="fc-badge red">▲ +18%</span></td></tr>
                        <tr><td><span class="flex items-center gap-2"><span style="width:8px;height:8px;border-radius:50%;background:#0054A6"></span>{{ t('fincontrol.ai.labelPurchases') }}</span></td><td style="text-align:right" class="fc-num">61 600 000 UZS</td><td style="text-align:right"><span class="fc-badge red">▲ +12%</span></td></tr>
                        <tr><td><span class="flex items-center gap-2"><span style="width:8px;height:8px;border-radius:50%;background:#F59E0B"></span>{{ t('fincontrol.ai.labelTaxes') }}</span></td><td style="text-align:right" class="fc-num">27 600 000 UZS</td><td style="text-align:right"><span class="fc-badge amber">▲ +5%</span></td></tr>
                      </tbody>
                    </table>
                  </div>
                  <div style="font-size:12.5px;color:#6B7A99;line-height:1.5;margin-bottom:8px">{{ t('fincontrol.ai.expGrowthNote') }}</div>
                  <button class="fc-link" style="font-size:13px">{{ t('fincontrol.ai.openIncExp') }}</button>
                </template>

                <!-- CF compare -->
                <template v-else-if="m.kind === 'cfCompare'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A;margin-bottom:10px" v-html="t('fincontrol.ai.cfCompareIntro')"></div>
                  <div style="border:1px solid #DDE3EE;border-radius:9px;padding:10px;margin-bottom:10px">
                    <FcChart type="bar" :data="compareData" :options="compareOptions" :height="140" />
                  </div>
                  <div style="font-size:12.5px;color:#6B7A99;line-height:1.5;margin-bottom:8px">{{ t('fincontrol.ai.cfCompareNote') }}</div>
                  <button class="fc-link" style="font-size:13px">{{ t('fincontrol.ai.openCashflow') }}</button>
                </template>

                <!-- Cash gap -->
                <template v-else-if="m.kind === 'cashGap'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A;margin-bottom:10px">{{ t('fincontrol.ai.cashGapIntro') }}</div>
                  <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:10px">
                    <div v-for="o in obligations" :key="o.name" class="flex items-center gap-2" style="background:#F8FAFC;padding:9px 11px;border-radius:8px">
                      <span :style="{ width:'8px', height:'8px', borderRadius:'50%', background:o.dot }"></span>
                      <div style="flex:1">
                        <div style="font-weight:700;font-size:12.5px;color:#1A2B4A">{{ o.name }}</div>
                        <div style="font-size:11px;color:#6B7A99">{{ o.date }}</div>
                      </div>
                      <span class="fc-num red" style="font-weight:700">{{ o.amt }}</span>
                    </div>
                  </div>
                  <div style="font-size:12.5px;color:#1A2B4A;margin-bottom:8px" v-html="t('fincontrol.ai.cashGapSummary')"></div>
                  <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(0,166,81,.1);color:#00A651;padding:6px 12px;border-radius:20px;font-weight:700;font-size:12px;margin-bottom:8px">
                    <AppIcon name="check_circle" filled style="font-size:14px" /> {{ t('fincontrol.ai.cashGapOk') }}
                  </div>
                  <div><button class="fc-link" style="font-size:13px">{{ t('fincontrol.ai.openPlanning') }}</button></div>
                </template>

                <template v-else-if="m.kind === 'balance'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A" v-html="t('fincontrol.ai.balanceAns')"></div>
                </template>
                <template v-else-if="m.kind === 'topPayer'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A" v-html="t('fincontrol.ai.topPayerAns')"></div>
                </template>
                <template v-else-if="m.kind === 'taxShare'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A" v-html="t('fincontrol.ai.taxShareAns')"></div>
                </template>
                <template v-else-if="m.kind === 'cfTrend'">
                  <div style="font-size:13.5px;line-height:1.5;color:#1A2B4A" v-html="t('fincontrol.ai.cfTrendAns')"></div>
                </template>

                <div style="font-size:10.5px;color:#94A3B8;font-style:italic;border-top:1px solid #F0F4FA;margin-top:10px;padding-top:6px">{{ t('fincontrol.ai.msgDisclaimer') }}</div>
                <div style="font-size:10.5px;color:#94A3B8;margin-top:4px">{{ m.time }}</div>
              </div>
            </div>
          </template>

          <!-- Typing indicator -->
          <div v-if="typing" class="flex gap-2" style="align-items:flex-start">
            <div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#F59E0B,#F97316);display:flex;align-items:center;justify-content:center;color:white;flex-shrink:0">
              <AppIcon name="auto_awesome" filled style="font-size:18px" />
            </div>
            <div style="background:white;border:1px solid #DDE3EE;padding:12px 14px;border-radius:14px 14px 14px 4px;display:flex;gap:4px">
              <span v-for="i in 3" :key="i" :style="{ width:'7px', height:'7px', borderRadius:'50%', background:'#F59E0B', animation:'ai-dot 1.4s infinite', animationDelay: `${i * 0.15}s` }"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div style="padding:14px 20px;background:white;border-top:1px solid #DDE3EE">
        <div style="display:flex;gap:8px;align-items:flex-end;background:#F8FAFC;border:1px solid #DDE3EE;border-radius:12px;padding:8px 10px">
          <textarea v-model="inputText" @keydown="onKey" rows="1"
            :placeholder="t('fincontrol.ai.inputPh')"
            style="flex:1;resize:none;border:0;background:transparent;outline:none;font-family:inherit;font-size:13.5px;color:#1A2B4A;padding:6px 4px;min-height:22px;max-height:120px"></textarea>
          <button class="fc-primary-btn" :disabled="!inputText.trim()" style="padding:8px 10px" @click="send()">
            <AppIcon name="send" />
          </button>
        </div>
        <div class="flex items-center gap-2" style="font-size:11px;color:#6B7A99;margin-top:8px">
          <AppIcon name="schedule" style="font-size:12px" />
          <span v-html="t('fincontrol.ai.footer')"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes ai-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,166,81,.6); }
  50% { box-shadow: 0 0 0 6px rgba(0,166,81,0); }
}
@keyframes ai-dot {
  0%, 80%, 100% { opacity: .3; transform: scale(.8); }
  40% { opacity: 1; transform: scale(1.2); }
}
</style>
