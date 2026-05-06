<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import PageHeader from '@/components/PageHeader.vue'
import { businessPlanApi } from '@/services/businessPlanApi'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const detail = ref(null)
const loading = ref(true)
const error = ref('')
const showInputs = ref(false)

async function load() {
  loading.value = true
  const res = await businessPlanApi.adminDetail(route.params.id)
  loading.value = false
  if (!res.ok) {
    error.value = res.status === 403 ? t('businessPlanAdmin.errors.forbidden') : t('businessPlanAdmin.errors.notFound')
    return
  }
  detail.value = res.data
}

const fmt = (n) => Number(n || 0).toLocaleString('ru-RU')
const fmtDate = (iso) => new Date(iso).toLocaleString('ru-RU')

function viewAsUser() {
  // Cache the plan into sessionStorage and navigate to the result view, so the
  // admin can see exactly what the user saw (including charts).
  if (!detail.value) return
  // Cache the same blob shape the result view expects, so admin sees
  // exactly what the user saw (output + creditScore + inputs).
  try {
    sessionStorage.setItem(
      `bp_${detail.value.id}`,
      JSON.stringify({
        id: detail.value.id,
        output: detail.value.output,
        recommendedProductsCandidates: detail.value.recommendedProductsCandidates,
        creditScore: detail.value.creditScore || null,
        inputs: detail.value.inputs || {},
      }),
    )
  } catch (_) {}
  router.push(`/tools/business-plan/result/${detail.value.id}`)
}

const candidatesList = computed(() => detail.value?.recommendedProductsCandidates || [])
const creditScore = computed(() => detail.value?.creditScore || null)

onMounted(load)
</script>

<template>
  <section class="p-6 lg:p-8 space-y-6">
    <button class="bp-admin-back" @click="router.push('/admin/business-plans')">
      <AppIcon name="arrow_back" />
      {{ t('businessPlanAdmin.backToList') }}
    </button>

    <div v-if="loading" class="bp-admin-loading"><div class="bp-admin-spinner"></div></div>

    <div v-else-if="error" class="bp-admin-error">
      <AppIcon name="error_outline" />
      {{ error }}
    </div>

    <template v-else-if="detail">
      <PageHeader :title="detail.orgName || '—'" :subtitle="t('businessPlanAdmin.detailSubtitle')" />

      <!-- meta row -->
      <div class="bp-admin-meta">
        <div><span>{{ t('businessPlanAdmin.cols.date') }}</span><strong>{{ fmtDate(detail.createdAt) }}</strong></div>
        <div><span>{{ t('businessPlanAdmin.cols.user') }}</span><strong>{{ detail.userEmail || t('businessPlanAdmin.anon') }}</strong></div>
        <div><span>{{ t('businessPlanAdmin.cols.type') }}</span><strong>{{ detail.orgType === 'legal_entity' ? t('businessPlan.orgTypes.legal_entity') : t('businessPlan.orgTypes.individual') }}</strong></div>
        <div><span>{{ t('businessPlanAdmin.cols.lang') }}</span><strong>{{ detail.lang.toUpperCase() }}</strong></div>
        <div><span>{{ t('businessPlanAdmin.cols.model') }}</span><strong>{{ detail.model || '—' }}</strong></div>
        <div><span>{{ t('businessPlanAdmin.cols.tokens') }}</span><strong>{{ fmt(detail.inputTokens + detail.outputTokens) }}</strong></div>
      </div>

      <!-- error if generation failed -->
      <div v-if="detail.error" class="bp-admin-error">
        <strong>{{ t('businessPlanAdmin.statusError') }}:</strong>
        <pre>{{ detail.error }}</pre>
      </div>

      <div v-else class="bp-admin-actions">
        <button class="bp-admin-cta" @click="viewAsUser">
          <AppIcon name="visibility" />
          {{ t('businessPlanAdmin.viewAsUser') }}
        </button>
      </div>

      <!-- summary -->
      <section v-if="detail.output?.summary" class="bp-admin-card">
        <h3>{{ t('businessPlanAdmin.summary') }}</h3>
        <p>{{ detail.output.summary }}</p>
        <div class="bp-admin-verdict">
          <span :class="`v-${detail.output.feasibilityVerdict}`">
            {{ t(`businessPlan.result.verdicts.${detail.output.feasibilityVerdict || 'medium'}`) }}
          </span>
          · {{ detail.output.feasibilityScore || 0 }}/100
        </div>
      </section>

      <!-- credit scoring -->
      <section v-if="creditScore" class="bp-admin-card">
        <h3>{{ t('businessPlanAdmin.creditScoring') }}</h3>
        <div :class="['bp-admin-fin-banner', `is-${creditScore.verdict}`]">
          <span>{{ t(`businessPlan.scoring.verdicts.${creditScore.verdict}`) }}</span>
          <strong>{{ creditScore.points }}/{{ creditScore.maxPoints }} ({{ creditScore.percent }}%)</strong>
        </div>
        <p class="muted">{{ creditScore.summary }}</p>
        <details>
          <summary>{{ t('businessPlanAdmin.showRatios') }}</summary>
          <ul class="bp-admin-list">
            <li v-for="(info, key) in creditScore.ratios" :key="key">
              {{ t(`businessPlan.scoring.ratioNames.${key}`) }}:
              <strong>{{ info.value }}{{ info.unit }}</strong>
              <span class="muted"> · {{ info.benchmark }}</span>
            </li>
          </ul>
        </details>
      </section>

      <!-- recommended product candidates (input) -->
      <section v-if="candidatesList.length" class="bp-admin-card">
        <h3>{{ t('businessPlanAdmin.candidates') }}</h3>
        <p class="muted">{{ t('businessPlanAdmin.candidatesHint') }}</p>
        <ul class="bp-admin-list">
          <li v-for="c in candidatesList" :key="c.id">
            <strong>{{ c.name }}</strong>
            <span class="muted"> · {{ c.rate }} · {{ c.term }} · {{ c.amount }}</span>
          </li>
        </ul>
      </section>

      <!-- raw inputs (toggle) -->
      <section class="bp-admin-card">
        <button class="bp-admin-toggle" @click="showInputs = !showInputs">
          <AppIcon :name="showInputs ? 'expand_less' : 'expand_more'" />
          {{ showInputs ? t('businessPlanAdmin.hideInputs') : t('businessPlanAdmin.showInputs') }}
        </button>
        <pre v-if="showInputs" class="bp-admin-json">{{ JSON.stringify(detail.inputs, null, 2) }}</pre>
      </section>
    </template>
  </section>
</template>

<style scoped>
.bp-admin-back {
  display: inline-flex; align-items: center; gap: 6px;
  background: transparent; border: 0; cursor: pointer;
  color: #003d7c; font-weight: 700; font-size: 14px; padding: 0;
}
.bp-admin-back:hover { text-decoration: underline; }

.bp-admin-loading { display: grid; place-items: center; padding: 60px; }
.bp-admin-spinner {
  width: 48px; height: 48px; border-radius: 50%;
  border: 4px solid rgba(0,61,124,0.15); border-top-color: #003d7c;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.bp-admin-error {
  background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
  padding: 14px 18px; border-radius: 10px;
}
.bp-admin-error pre { white-space: pre-wrap; margin: 6px 0 0 0; font-size: 12px; }

.bp-admin-meta {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  background: #fff; padding: 18px; border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.bp-admin-meta > div {
  display: flex; flex-direction: column; gap: 2px;
}
.bp-admin-meta span {
  font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;
}
.bp-admin-meta strong { color: #1e293b; font-size: 14px; }

.bp-admin-actions { display: flex; gap: 10px; }
.bp-admin-cta {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 18px; background: #003d7c; color: #fff;
  border: 0; border-radius: 10px; font-weight: 700; cursor: pointer;
}
.bp-admin-cta:hover { background: #00306a; }

.bp-admin-card {
  background: #fff; border-radius: 12px; padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.bp-admin-card h3 {
  margin: 0 0 10px 0; font-size: 14px; font-weight: 700;
  color: #003d7c; text-transform: uppercase; letter-spacing: 0.5px;
}
.bp-admin-card p { margin: 0 0 8px 0; color: #1e293b; line-height: 1.55; }
.muted { color: #64748b; font-size: 13px; }

.bp-admin-verdict {
  margin-top: 8px; font-size: 13px; color: #475569;
}
.bp-admin-verdict span {
  padding: 2px 10px; border-radius: 12px;
  font-size: 12px; font-weight: 700; color: #fff;
}
.v-high { background: #16a34a; }
.v-medium { background: #d97706; }
.v-low { background: #dc2626; }

.bp-admin-list { margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.7; }

.bp-admin-toggle {
  background: transparent; border: 0; cursor: pointer;
  display: inline-flex; align-items: center; gap: 6px;
  color: #003d7c; font-weight: 700; font-size: 14px; padding: 0;
}
.bp-admin-fin-banner {
  display: inline-flex; gap: 12px; align-items: center;
  padding: 6px 14px; border-radius: 20px; color: #fff;
  font-size: 12px; font-weight: 700; margin: 0 0 8px 0;
}
.bp-admin-fin-banner.is-high { background: #16a34a; }
.bp-admin-fin-banner.is-medium { background: #d97706; }
.bp-admin-fin-banner.is-low { background: #dc2626; }
.bp-admin-fin-banner span { text-transform: uppercase; letter-spacing: 0.5px; }
.bp-admin-card details summary {
  cursor: pointer; font-size: 13px; color: #003d7c; font-weight: 700; margin-top: 8px;
}

.bp-admin-json {
  background: #0f172a; color: #cbd5e1;
  padding: 16px; border-radius: 10px;
  font-size: 12px; line-height: 1.5;
  margin: 12px 0 0 0; overflow-x: auto;
  font-family: "JetBrains Mono", monospace;
}

@media (max-width: 700px) {
  .bp-admin-meta { grid-template-columns: 1fr 1fr; }
}
</style>
