<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Chart,
  BarController,
  LineController,
  DoughnutController,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import AppIcon from '@/components/AppIcon.vue'
import { businessPlanApi } from '@/services/businessPlanApi'
import { renderStandalonePlanHtml } from './standalonePlanHtml.js'

Chart.register(
  BarController, LineController, DoughnutController,
  BarElement, LineElement, PointElement, ArcElement,
  CategoryScale, LinearScale, Tooltip, Legend, Filler,
)

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const id = route.params.id
const loading = ref(true)
const error = ref('')
const plan = ref(null)
const inputs = ref(null)
const candidates = ref([])
const creditScore = ref(null)

// Refs for chart canvases
const expenseChartEl = ref(null)
const revenueChartEl = ref(null)
const costStructureEl = ref(null)

// ---------- formatters ----------
const fmt = (n) => Number(n || 0).toLocaleString('ru-RU')
const fmtPct = (n) => `${Number(n || 0).toFixed(1)}%`

// ---------- load ----------
async function load() {
  loading.value = true
  error.value = ''

  // Try sessionStorage cache first (the wizard puts the result there on submit)
  const cached = sessionStorage.getItem(`bp_${id}`)
  if (cached) {
    try {
      const parsed = JSON.parse(cached)
      plan.value = parsed.output
      candidates.value = parsed.recommendedProductsCandidates || []
      inputs.value = parsed.inputs || null
      creditScore.value = parsed.creditScore || null
      loading.value = false
      await nextTick()
      drawCharts()
      return
    } catch (_) {
      /* fall through to API */
    }
  }

  const res = await businessPlanApi.getPlan(id)
  if (!res.ok) {
    error.value = res.error || t('businessPlan.errors.notFound')
    loading.value = false
    return
  }
  plan.value = res.data.output
  candidates.value = res.data.recommendedProductsCandidates || []
  inputs.value = res.data.inputs || null
  creditScore.value = res.data.creditScore || null
  loading.value = false
  await nextTick()
  drawCharts()
}

// ---------- charts ----------
let chartsRefs = []

function destroyCharts() {
  chartsRefs.forEach((c) => c?.destroy?.())
  chartsRefs = []
}

function drawCharts() {
  destroyCharts()
  if (!plan.value) return

  const f = plan.value.financials || {}
  const c = f.monthlyCosts || {}
  const proj = plan.value.projection12m || []

  // 1) Cost structure donut
  if (costStructureEl.value) {
    const labels = [
      t('businessPlan.costs.payroll'),
      t('businessPlan.costs.utilities'),
      t('businessPlan.costs.rawMaterials'),
      t('businessPlan.costs.loanPayment'),
      t('businessPlan.costs.rent'),
      t('businessPlan.costs.other'),
    ]
    const data = [c.payroll, c.utilities, c.rawMaterials, c.loanPayment, c.rent, c.other].map((v) => Number(v || 0))
    chartsRefs.push(
      new Chart(costStructureEl.value, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [
            {
              data,
              backgroundColor: ['#003d7c', '#1e6bb8', '#2957A2', '#5b89c6', '#9bb5d6', '#cad6e6'],
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { font: { size: 12 }, boxWidth: 14 } },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.label}: ${fmt(ctx.raw)} UZS`,
              },
            },
          },
          cutout: '60%',
        },
      }),
    )
  }

  // 2) Monthly expense bar
  if (expenseChartEl.value) {
    const labels = [
      t('businessPlan.costs.payroll'),
      t('businessPlan.costs.utilities'),
      t('businessPlan.costs.rawMaterials'),
      t('businessPlan.costs.loanPayment'),
      t('businessPlan.costs.rent'),
      t('businessPlan.costs.other'),
    ]
    const data = [c.payroll, c.utilities, c.rawMaterials, c.loanPayment, c.rent, c.other].map((v) => Number(v || 0))
    chartsRefs.push(
      new Chart(expenseChartEl.value, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              data,
              backgroundColor: '#003d7c',
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { callback: (v) => fmt(v) },
            },
          },
        },
      }),
    )
  }

  // 3) 12-month revenue / costs / profit line
  if (revenueChartEl.value && proj.length) {
    chartsRefs.push(
      new Chart(revenueChartEl.value, {
        type: 'line',
        data: {
          labels: proj.map((p) => `${t('businessPlan.units.monthAbbrev')} ${p.month}`),
          datasets: [
            {
              label: t('businessPlan.charts.revenue'),
              data: proj.map((p) => Number(p.revenue || 0)),
              borderColor: '#16a34a',
              backgroundColor: 'rgba(22, 163, 74, 0.12)',
              tension: 0.35,
              fill: true,
            },
            {
              label: t('businessPlan.charts.costs'),
              data: proj.map((p) => Number(p.costs || 0)),
              borderColor: '#dc2626',
              backgroundColor: 'rgba(220, 38, 38, 0.08)',
              tension: 0.35,
              fill: false,
            },
            {
              label: t('businessPlan.charts.profit'),
              data: proj.map((p) => Number(p.profit || 0)),
              borderColor: '#003d7c',
              backgroundColor: 'rgba(0, 61, 124, 0.12)',
              tension: 0.35,
              fill: false,
              borderDash: [4, 4],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
          scales: {
            y: {
              beginAtZero: false,
              ticks: { callback: (v) => fmt(v) },
            },
          },
        },
      }),
    )
  }
}

// ---------- download ----------
function download() {
  if (!plan.value) return
  const html = renderStandalonePlanHtml({
    plan: plan.value,
    inputs: inputs.value,
    candidates: candidates.value,
    lang: locale.value,
    orgName: inputs.value?.organization?.name || 'Business Plan',
    generatedAt: new Date().toISOString(),
  })
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const safe = (inputs.value?.organization?.name || 'business-plan')
    .replace(/[^a-zA-Z0-9-_]+/g, '_')
    .slice(0, 60)
  a.href = url
  a.download = `${safe}_${id.slice(0, 8)}.html`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

const verdictColor = computed(() => {
  const v = plan.value?.feasibilityVerdict
  if (v === 'high') return '#16a34a'
  if (v === 'medium') return '#d97706'
  return '#dc2626'
})

onMounted(load)
</script>

<template>
  <div class="bpr-page">
    <!-- top bar -->
    <header class="bpr-topbar">
      <button class="bpr-back" @click="router.push('/tools')">
        <AppIcon name="arrow_back" />
      </button>
      <div class="bpr-brand">
        <img src="/nbu_logo.png" alt="NBU" />
        <div>
          <div class="bpr-brand-title">{{ t('businessPlan.result.title') }}</div>
          <div class="bpr-brand-sub">{{ inputs?.organization?.name || '' }}</div>
        </div>
      </div>
      <button v-if="plan" class="bpr-download" @click="download">
        <AppIcon name="download" />
        {{ t('businessPlan.result.download') }}
      </button>
    </header>

    <main class="bpr-main">
      <div v-if="loading" class="bpr-loading">
        <div class="bpr-spinner"></div>
        <p>{{ t('businessPlan.result.loading') }}</p>
      </div>

      <div v-else-if="error" class="bpr-error-block">
        <AppIcon name="error_outline" />
        <p>{{ error }}</p>
        <button @click="router.push('/tools/business-plan')">
          {{ t('businessPlan.result.retry') }}
        </button>
      </div>

      <div v-else-if="plan" class="bpr-content">
        <!-- Verdict header -->
        <section class="bpr-verdict-card">
          <div class="bpr-verdict-left">
            <div class="bpr-verdict-label">{{ t('businessPlan.result.feasibility') }}</div>
            <div class="bpr-verdict-score" :style="{ color: verdictColor }">
              {{ plan.feasibilityScore || 0 }}<span>/100</span>
            </div>
            <div class="bpr-verdict-tag" :style="{ background: verdictColor }">
              {{ t(`businessPlan.result.verdicts.${plan.feasibilityVerdict || 'medium'}`) }}
            </div>
          </div>
          <p class="bpr-verdict-summary">{{ plan.summary }}</p>
        </section>

        <!-- Credit scoring — computed from anketa inputs at submit time -->
        <section v-if="creditScore" class="bpr-section bpr-fin-section">
          <h2><AppIcon name="account_balance_wallet" /> {{ t('businessPlan.result.creditScoring') }}</h2>
          <div :class="['bpr-fin-banner', `is-${creditScore.verdict}`]">
            <div class="bpr-fin-tag">
              {{ t(`businessPlan.scoring.verdicts.${creditScore.verdict}`) }}
            </div>
            <div class="bpr-fin-points">
              {{ creditScore.points }} / {{ creditScore.maxPoints }}
              <small>({{ creditScore.percent }}%)</small>
            </div>
            <p class="bpr-fin-summary">{{ creditScore.summary }}</p>
          </div>
          <table class="bpr-fin-ratios">
            <thead>
              <tr>
                <th>{{ t('businessPlan.scoring.cols.ratio') }}</th>
                <th class="num">{{ t('businessPlan.scoring.cols.value') }}</th>
                <th>{{ t('businessPlan.scoring.cols.benchmark') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(info, key) in creditScore.ratios" :key="key">
                <td>{{ t(`businessPlan.scoring.ratioNames.${key}`) }}</td>
                <td class="num">
                  <span :class="['bpr-fin-bullet', `s-${info.score}`]"></span>
                  {{ info.value }}{{ info.unit }}
                </td>
                <td class="muted">{{ info.benchmark }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- Executive summary -->
        <section class="bpr-section">
          <h2><AppIcon name="article" /> {{ t('businessPlan.result.executiveSummary') }}</h2>
          <p>{{ plan.executiveSummary }}</p>
        </section>

        <!-- Market context -->
        <section v-if="plan.marketContext" class="bpr-section">
          <h2><AppIcon name="public" /> {{ t('businessPlan.result.marketContext') }}</h2>
          <p>{{ plan.marketContext }}</p>
        </section>

        <!-- KEY METRICS -->
        <section class="bpr-metrics">
          <div class="bpr-metric">
            <div class="bpr-metric-label">{{ t('businessPlan.result.monthlyRevenue') }}</div>
            <div class="bpr-metric-val">{{ fmt(plan.financials?.monthlyRevenue) }} <small>UZS</small></div>
          </div>
          <div class="bpr-metric">
            <div class="bpr-metric-label">{{ t('businessPlan.result.monthlyCosts') }}</div>
            <div class="bpr-metric-val">{{ fmt(plan.financials?.monthlyCosts?.total) }} <small>UZS</small></div>
          </div>
          <div class="bpr-metric">
            <div class="bpr-metric-label">{{ t('businessPlan.result.monthlyProfit') }}</div>
            <div class="bpr-metric-val" :class="{ 'is-neg': Number(plan.financials?.monthlyProfit || 0) < 0 }">
              {{ fmt(plan.financials?.monthlyProfit) }} <small>UZS</small>
            </div>
          </div>
          <div class="bpr-metric">
            <div class="bpr-metric-label">{{ t('businessPlan.result.breakeven') }}</div>
            <div class="bpr-metric-val">{{ plan.financials?.breakevenMonths || '—' }} <small>{{ t('businessPlan.units.months') }}</small></div>
          </div>
          <div class="bpr-metric">
            <div class="bpr-metric-label">{{ t('businessPlan.result.grossMargin') }}</div>
            <div class="bpr-metric-val">{{ fmtPct(plan.financials?.grossMarginPct) }}</div>
          </div>
          <div class="bpr-metric">
            <div class="bpr-metric-label">{{ t('businessPlan.result.ebitda') }}</div>
            <div class="bpr-metric-val">{{ fmtPct(plan.financials?.ebitdaMarginPct) }}</div>
          </div>
        </section>

        <!-- Charts row 1 -->
        <section class="bpr-charts-row">
          <div class="bpr-chart-card">
            <h3>{{ t('businessPlan.charts.costStructure') }}</h3>
            <div class="bpr-chart-h"><canvas ref="costStructureEl"></canvas></div>
          </div>
          <div class="bpr-chart-card">
            <h3>{{ t('businessPlan.charts.expenseBreakdown') }}</h3>
            <div class="bpr-chart-h"><canvas ref="expenseChartEl"></canvas></div>
          </div>
        </section>

        <!-- 12-month projection -->
        <section class="bpr-chart-card-wide">
          <h3>{{ t('businessPlan.charts.projection12m') }}</h3>
          <div class="bpr-chart-h-tall"><canvas ref="revenueChartEl"></canvas></div>
        </section>

        <p v-if="plan.financials?.assessment" class="bpr-assessment">
          <AppIcon name="insights" />
          {{ plan.financials.assessment }}
        </p>

        <!-- Operations -->
        <section v-if="plan.operations" class="bpr-section">
          <h2><AppIcon name="settings_suggest" /> {{ t('businessPlan.result.operations') }}</h2>
          <ul v-if="plan.operations.processFlow?.length">
            <li v-for="(step, i) in plan.operations.processFlow" :key="i">{{ step }}</li>
          </ul>
          <p v-if="plan.operations.supplyChain"><strong>{{ t('businessPlan.result.supplyChain') }}:</strong> {{ plan.operations.supplyChain }}</p>
          <div v-if="plan.operations.criticalDependencies?.length" class="bpr-deps">
            <strong>{{ t('businessPlan.result.criticalDeps') }}</strong>
            <ul>
              <li v-for="(d, i) in plan.operations.criticalDependencies" :key="i">{{ d }}</li>
            </ul>
          </div>
        </section>

        <!-- Team -->
        <section v-if="plan.team" class="bpr-section bpr-team-card">
          <h2><AppIcon name="groups" /> {{ t('businessPlan.result.team') }}</h2>
          <div class="bpr-team-stats">
            <div>
              <span>{{ t('businessPlan.result.headcount') }}</span>
              <strong>{{ plan.team.totalHeadcount }}</strong>
            </div>
            <div>
              <span>{{ t('businessPlan.result.monthlyPayroll') }}</span>
              <strong>{{ fmt(plan.team.monthlyPayroll) }} UZS</strong>
            </div>
            <div>
              <span>{{ t('businessPlan.result.annualPayroll') }}</span>
              <strong>{{ fmt(plan.team.annualPayroll) }} UZS</strong>
            </div>
          </div>
          <p v-if="plan.team.assessment">{{ plan.team.assessment }}</p>
        </section>

        <!-- Milestones -->
        <section v-if="plan.milestones" class="bpr-section">
          <h2><AppIcon name="flag" /> {{ t('businessPlan.result.milestones') }}</h2>
          <div class="bpr-milestone-grid">
            <div class="bpr-milestone-col">
              <h4>{{ t('businessPlan.result.first90') }}</h4>
              <ul><li v-for="(m, i) in plan.milestones.first90Days" :key="i">{{ m }}</li></ul>
            </div>
            <div class="bpr-milestone-col">
              <h4>{{ t('businessPlan.result.first6') }}</h4>
              <ul><li v-for="(m, i) in plan.milestones.first6Months" :key="i">{{ m }}</li></ul>
            </div>
            <div class="bpr-milestone-col">
              <h4>{{ t('businessPlan.result.first12') }}</h4>
              <ul><li v-for="(m, i) in plan.milestones.first12Months" :key="i">{{ m }}</li></ul>
            </div>
          </div>
        </section>

        <!-- Risks -->
        <section v-if="plan.risks?.length" class="bpr-section">
          <h2><AppIcon name="warning" /> {{ t('businessPlan.result.risks') }}</h2>
          <div class="bpr-risk-grid">
            <div v-for="(r, i) in plan.risks" :key="i" :class="['bpr-risk', `is-${r.severity || 'medium'}`]">
              <div class="bpr-risk-h">
                <span class="bpr-risk-type">{{ t(`businessPlan.riskTypes.${r.type || 'operational'}`) }}</span>
                <span class="bpr-risk-sev">{{ t(`businessPlan.severity.${r.severity || 'medium'}`) }}</span>
              </div>
              <div class="bpr-risk-desc">{{ r.description }}</div>
              <div class="bpr-risk-mit"><strong>{{ t('businessPlan.result.mitigation') }}:</strong> {{ r.mitigation }}</div>
            </div>
          </div>
        </section>

        <!-- KPIs -->
        <section v-if="plan.kpis?.length" class="bpr-section">
          <h2><AppIcon name="speed" /> {{ t('businessPlan.result.kpis') }}</h2>
          <table class="bpr-kpi-table">
            <thead>
              <tr>
                <th>{{ t('businessPlan.result.kpiName') }}</th>
                <th>{{ t('businessPlan.result.kpiTarget') }}</th>
                <th>{{ t('businessPlan.result.kpiFreq') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(k, i) in plan.kpis" :key="i">
                <td>{{ k.name }}</td>
                <td>{{ k.target }}</td>
                <td>{{ k.frequency }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- Recommended NBU products -->
        <section v-if="plan.recommendedProducts?.length" class="bpr-section bpr-products">
          <h2><AppIcon name="account_balance" /> {{ t('businessPlan.result.recommendedProducts') }}</h2>
          <p class="bpr-products-hint">{{ t('businessPlan.result.recommendedHint') }}</p>
          <div class="bpr-product-list">
            <div v-for="(p, i) in plan.recommendedProducts" :key="i" class="bpr-product-card">
              <div class="bpr-product-h">
                <h3>{{ p.name }}</h3>
                <span class="bpr-fit">{{ t('businessPlan.result.fit') }}: {{ p.fitScore }}/100</span>
              </div>
              <div class="bpr-product-meta">
                <div><span>{{ t('businessPlan.result.rate') }}</span><strong>{{ p.rate }}</strong></div>
                <div><span>{{ t('businessPlan.result.term') }}</span><strong>{{ p.term }}</strong></div>
                <div><span>{{ t('businessPlan.result.amount') }}</span><strong>{{ p.amount }}</strong></div>
              </div>
              <div class="bpr-product-purpose"><strong>{{ t('businessPlan.result.purpose') }}:</strong> {{ p.purpose }}</div>
              <p class="bpr-product-rationale">{{ p.rationale }}</p>
            </div>
          </div>
        </section>

        <!-- Actionable steps -->
        <section v-if="plan.actionableNextSteps?.length" class="bpr-section bpr-next">
          <h2><AppIcon name="task_alt" /> {{ t('businessPlan.result.nextSteps') }}</h2>
          <ol>
            <li v-for="(s, i) in plan.actionableNextSteps" :key="i">{{ s }}</li>
          </ol>
        </section>

        <footer class="bpr-footer">
          <button class="bpr-btn-primary" @click="download">
            <AppIcon name="download" />
            {{ t('businessPlan.result.download') }}
          </button>
          <button class="bpr-btn-secondary" @click="router.push('/tools/business-plan')">
            {{ t('businessPlan.result.newPlan') }}
          </button>
        </footer>
      </div>
    </main>
  </div>
</template>

<style scoped>
.bpr-page {
  min-height: 100vh;
  background: #f4f6fa;
}
.bpr-topbar {
  background: #fff;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.bpr-back {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  display: grid;
  place-items: center;
  color: #475569;
}
.bpr-back:hover { background: #f1f5f9; }
.bpr-brand { display: flex; gap: 12px; align-items: center; flex: 1; }
.bpr-brand img { height: 36px; }
.bpr-brand-title { font-weight: 800; color: #003d7c; font-size: 17px; line-height: 1.1; }
.bpr-brand-sub { color: #64748b; font-size: 12px; }
.bpr-download {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #003d7c;
  color: #fff;
  border: 0;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}
.bpr-download:hover { background: #00306a; }

.bpr-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
.bpr-loading,
.bpr-error-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  color: #64748b;
}
.bpr-spinner {
  width: 56px; height: 56px; border-radius: 50%;
  border: 4px solid rgba(0, 61, 124, 0.15);
  border-top-color: #003d7c;
  animation: spin 0.9s linear infinite;
  margin-bottom: 24px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.bpr-error-block button {
  margin-top: 16px; padding: 10px 18px; background: #003d7c; color: #fff;
  border: 0; border-radius: 10px; font-weight: 700; cursor: pointer;
}

.bpr-content { display: flex; flex-direction: column; gap: 20px; }

/* Verdict */
.bpr-verdict-card {
  background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.bpr-verdict-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}
.bpr-verdict-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;
}
.bpr-verdict-score {
  font-size: 56px; font-weight: 800; line-height: 1;
}
.bpr-verdict-score span {
  font-size: 24px; color: #94a3b8; font-weight: 600;
}
.bpr-verdict-tag {
  margin-top: 8px;
  padding: 4px 14px;
  border-radius: 20px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.bpr-verdict-summary {
  margin: 0;
  color: #1e293b;
  font-size: 16px;
  line-height: 1.55;
}

/* Sections */
.bpr-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.bpr-section h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 14px 0;
  font-size: 18px;
  font-weight: 800;
  color: #003d7c;
}
.bpr-section p {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 15px;
  line-height: 1.6;
}
.bpr-section ul {
  margin: 0; padding-left: 24px;
  color: #1e293b; font-size: 14px; line-height: 1.7;
}
.bpr-section ol {
  margin: 0; padding-left: 24px;
  color: #1e293b; font-size: 15px; line-height: 1.7;
}
.bpr-section ol li { padding-bottom: 6px; }

/* Metrics */
.bpr-metrics {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}
.bpr-metric {
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.bpr-metric-label {
  font-size: 11px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;
}
.bpr-metric-val { font-size: 18px; font-weight: 800; color: #003d7c; }
.bpr-metric-val.is-neg { color: #dc2626; }
.bpr-metric-val small { font-size: 11px; color: #94a3b8; font-weight: 600; }

/* Charts */
.bpr-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.bpr-chart-card,
.bpr-chart-card-wide {
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.bpr-chart-card h3,
.bpr-chart-card-wide h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.bpr-chart-h { height: 240px; position: relative; }
.bpr-chart-h-tall { height: 320px; position: relative; }

.bpr-assessment {
  background: #f1f5f9;
  border-left: 3px solid #003d7c;
  padding: 14px 16px;
  border-radius: 8px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.55;
  margin: 0;
}

/* Team */
.bpr-team-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}
.bpr-team-stats > div {
  background: #f8fafc;
  border-radius: 10px;
  padding: 12px 14px;
}
.bpr-team-stats span {
  display: block;
  font-size: 11px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.bpr-team-stats strong {
  font-size: 16px; color: #003d7c;
}

.bpr-deps {
  margin-top: 12px;
  padding: 12px;
  background: #fffbeb;
  border-radius: 8px;
  border-left: 3px solid #f59e0b;
}

/* Milestones */
.bpr-milestone-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
.bpr-milestone-col h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 700;
  color: #003d7c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.bpr-milestone-col ul {
  padding-left: 16px;
  font-size: 14px;
  line-height: 1.5;
}

/* Risks */
.bpr-risk-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.bpr-risk {
  background: #f8fafc;
  border-radius: 10px;
  padding: 14px 16px;
  border-left: 4px solid #94a3b8;
}
.bpr-risk.is-high { border-left-color: #dc2626; background: #fef2f2; }
.bpr-risk.is-medium { border-left-color: #f59e0b; background: #fffbeb; }
.bpr-risk.is-low { border-left-color: #16a34a; background: #f0fdf4; }
.bpr-risk-h {
  display: flex; justify-content: space-between; margin-bottom: 6px;
}
.bpr-risk-type { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; }
.bpr-risk-sev { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #94a3b8; }
.bpr-risk-desc { font-size: 14px; color: #1e293b; margin-bottom: 6px; }
.bpr-risk-mit { font-size: 13px; color: #475569; }

/* KPIs */
.bpr-kpi-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.bpr-kpi-table th {
  text-align: left;
  padding: 10px 14px;
  background: #f8fafc;
  font-size: 11px;
  text-transform: uppercase;
  color: #475569;
  font-weight: 700;
}
.bpr-kpi-table td {
  padding: 10px 14px;
  border-top: 1px solid #f1f5f9;
  color: #1e293b;
}

/* Products */
.bpr-products-hint {
  color: #64748b !important; font-size: 13px !important; margin-bottom: 16px !important;
}
.bpr-product-list { display: grid; gap: 12px; }
.bpr-product-card {
  border: 1.5px solid #003d7c;
  border-radius: 12px;
  padding: 18px 20px;
  background: linear-gradient(135deg, rgba(0, 61, 124, 0.04) 0%, #fff 60%);
}
.bpr-product-h {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
}
.bpr-product-h h3 { margin: 0; color: #003d7c; font-size: 17px; font-weight: 800; }
.bpr-fit {
  background: #003d7c; color: #fff;
  padding: 4px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 700;
}
.bpr-product-meta {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 10px;
}
.bpr-product-meta div span {
  display: block;
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;
}
.bpr-product-meta div strong {
  font-size: 14px; color: #1e293b;
}
.bpr-product-purpose {
  font-size: 13px; color: #475569; margin-bottom: 8px;
}
.bpr-product-rationale {
  margin: 0 !important; font-size: 14px !important; color: #1e293b !important; line-height: 1.55 !important;
}

/* Footer */
.bpr-footer {
  display: flex; gap: 12px; justify-content: center; margin-top: 12px; padding: 24px 0;
}
.bpr-btn-primary,
.bpr-btn-secondary {
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  border: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.bpr-btn-primary { background: #003d7c; color: #fff; }
.bpr-btn-primary:hover { background: #00306a; }
.bpr-btn-secondary { background: #f1f5f9; color: #475569; }
.bpr-btn-secondary:hover { background: #e2e8f0; }

/* Historical financial scoring */
.bpr-fin-section .bpr-fin-banner {
  border-radius: 12px; padding: 18px 22px; color: #fff;
  display: grid; grid-template-columns: auto auto 1fr; gap: 12px 16px; align-items: center;
  margin-bottom: 14px;
}
.bpr-fin-banner.is-high   { background: linear-gradient(135deg, #16a34a 0%, #15803d 100%); }
.bpr-fin-banner.is-medium { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); }
.bpr-fin-banner.is-low    { background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); }
.bpr-fin-tag {
  background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px;
  font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;
}
.bpr-fin-points { font-size: 18px; font-weight: 800; }
.bpr-fin-points small { font-size: 12px; opacity: 0.85; font-weight: 600; }
.bpr-fin-summary { margin: 0; font-size: 14px; line-height: 1.5; grid-column: 1 / -1; }

.bpr-fin-ratios { width: 100%; border-collapse: collapse; font-size: 13px; }
.bpr-fin-ratios th { text-align: left; padding: 10px 14px; background: #f8fafc; font-size: 11px; text-transform: uppercase; color: #475569; font-weight: 700; letter-spacing: 0.5px; }
.bpr-fin-ratios th.num, .bpr-fin-ratios td.num { text-align: right; }
.bpr-fin-ratios td { padding: 10px 14px; border-top: 1px solid #f1f5f9; color: #1e293b; }
.bpr-fin-ratios .muted { color: #64748b; font-size: 12px; }
.bpr-fin-bullet {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; vertical-align: middle;
}
.bpr-fin-bullet.s-0 { background: #dc2626; }
.bpr-fin-bullet.s-1 { background: #d97706; }
.bpr-fin-bullet.s-2 { background: #16a34a; }

@media (max-width: 900px) {
  .bpr-metrics { grid-template-columns: 1fr 1fr; }
  .bpr-charts-row { grid-template-columns: 1fr; }
  .bpr-milestone-grid { grid-template-columns: 1fr; }
  .bpr-risk-grid { grid-template-columns: 1fr; }
  .bpr-team-stats { grid-template-columns: 1fr; }
}
</style>
