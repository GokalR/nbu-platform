<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'
import { businessPlanApi } from '@/services/businessPlanApi'

const { t } = useI18n()
const router = useRouter()

const items = ref([])
const loading = ref(true)
const error = ref('')

function fmtDate(iso) {
  const d = new Date(iso)
  return d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

async function load() {
  loading.value = true
  error.value = ''
  const res = await businessPlanApi.adminList()
  loading.value = false
  if (!res.ok) {
    error.value = res.status === 403 ? t('businessPlanAdmin.errors.forbidden') : t('businessPlanAdmin.errors.loadFailed')
    return
  }
  items.value = res.data
}

onMounted(load)
</script>

<template>
  <section class="p-6 lg:p-8 space-y-6">
    <PageHeader :title="t('businessPlanAdmin.title')" :subtitle="t('businessPlanAdmin.subtitle')" />

    <div v-if="loading" class="bp-admin-loading">
      <div class="bp-admin-spinner"></div>
    </div>

    <div v-else-if="error" class="bp-admin-error">
      <AppIcon name="error_outline" />
      {{ error }}
    </div>

    <div v-else-if="!items.length" class="bp-admin-empty">
      <AppIcon name="inbox" />
      <p>{{ t('businessPlanAdmin.empty') }}</p>
    </div>

    <div v-else class="bp-admin-table-wrap">
      <table class="bp-admin-table">
        <thead>
          <tr>
            <th>{{ t('businessPlanAdmin.cols.date') }}</th>
            <th>{{ t('businessPlanAdmin.cols.org') }}</th>
            <th>{{ t('businessPlanAdmin.cols.type') }}</th>
            <th>{{ t('businessPlanAdmin.cols.user') }}</th>
            <th>{{ t('businessPlanAdmin.cols.lang') }}</th>
            <th class="num">{{ t('businessPlanAdmin.cols.tokens') }}</th>
            <th>{{ t('businessPlanAdmin.cols.status') }}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="it in items" :key="it.id">
            <td class="muted">{{ fmtDate(it.createdAt) }}</td>
            <td><strong>{{ it.orgName || '—' }}</strong></td>
            <td>
              <span class="bp-admin-pill">
                {{ it.orgType === 'legal_entity' ? t('businessPlan.orgTypes.legal_entity') : t('businessPlan.orgTypes.individual') }}
              </span>
            </td>
            <td class="muted">{{ it.userEmail || t('businessPlanAdmin.anon') }}</td>
            <td><span class="bp-admin-pill">{{ it.lang.toUpperCase() }}</span></td>
            <td class="num muted">{{ (it.inputTokens + it.outputTokens).toLocaleString('ru-RU') }}</td>
            <td>
              <span v-if="it.hasError" class="bp-admin-pill bp-admin-pill-err">
                {{ t('businessPlanAdmin.statusError') }}
              </span>
              <span v-else class="bp-admin-pill bp-admin-pill-ok">
                {{ t('businessPlanAdmin.statusOk') }}
              </span>
            </td>
            <td class="actions">
              <button class="bp-admin-link" @click="router.push(`/admin/business-plans/${it.id}`)">
                {{ t('businessPlanAdmin.view') }}
                <AppIcon name="arrow_forward" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.bp-admin-loading {
  display: grid; place-items: center; padding: 60px;
}
.bp-admin-spinner {
  width: 48px; height: 48px; border-radius: 50%;
  border: 4px solid rgba(0,61,124,0.15); border-top-color: #003d7c;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.bp-admin-error {
  background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
  padding: 14px 18px; border-radius: 10px;
  display: flex; align-items: center; gap: 10px;
}
.bp-admin-empty {
  text-align: center; color: #94a3b8; padding: 60px 0;
}
.bp-admin-empty p { margin-top: 12px; }
.bp-admin-table-wrap {
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  overflow-x: auto;
}
.bp-admin-table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 900px; }
.bp-admin-table th {
  text-align: left; padding: 12px 16px;
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;
  background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.bp-admin-table th.num, .bp-admin-table td.num { text-align: right; }
.bp-admin-table td {
  padding: 12px 16px; border-top: 1px solid #f1f5f9;
}
.bp-admin-table td.muted { color: #64748b; }
.bp-admin-table tbody tr:hover { background: #f8fafc; }
.bp-admin-pill {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  background: #e0e7ff; color: #003d7c; font-size: 12px; font-weight: 700;
}
.bp-admin-pill-ok { background: #d1fae5; color: #065f46; }
.bp-admin-pill-err { background: #fee2e2; color: #991b1b; }
.bp-admin-link {
  display: inline-flex; align-items: center; gap: 4px;
  background: transparent; border: 0; cursor: pointer;
  color: #003d7c; font-weight: 700; font-size: 13px;
}
.bp-admin-link:hover { text-decoration: underline; }
.actions { text-align: right; }
</style>
