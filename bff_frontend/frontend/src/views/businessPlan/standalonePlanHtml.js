/**
 * Generates a fully self-contained HTML document of a business plan.
 * - All CSS inlined.
 * - Chart.js loaded from CDN (so the file stays small ~50KB instead of 200KB+).
 *   Charts render when the user has internet; the rest of the document
 *   (text, tables, metrics) works offline. Print-to-PDF works regardless.
 */

const fmt = (n) => Number(n || 0).toLocaleString('ru-RU')
const fmtPct = (n) => `${Number(n || 0).toFixed(1)}%`

// Bilingual labels embedded so the standalone file doesn't need vue-i18n.
const L = {
  uz: {
    title: 'Biznes-Reja',
    feasibility: 'Loyiha amalga oshirish reytingi',
    verdicts: { high: 'Yuqori', medium: 'Oʻrtacha', low: 'Past' },
    executive: 'Qisqacha xulosa',
    market: 'Bozor konteksti',
    monthlyRevenue: 'Oylik daromad',
    monthlyCosts: 'Oylik xarajat',
    monthlyProfit: 'Oylik foyda',
    breakeven: 'Tenglik nuqtasi',
    grossMargin: 'Yalpi marja',
    ebitda: 'EBITDA marja',
    months: 'oy',
    operations: 'Ishlab chiqarish jarayoni',
    supplyChain: 'Yetkazib berish',
    criticalDeps: 'Asosiy bogʻliqliklar:',
    team: 'Jamoa',
    headcount: 'Xodimlar soni',
    monthlyPayroll: 'Oylik ish haqi',
    annualPayroll: 'Yillik ish haqi',
    milestones: 'Reja qadamlari',
    first90: 'Birinchi 90 kun',
    first6: '6 oy ichida',
    first12: '12 oy ichida',
    risks: 'Xatarlar',
    mitigation: 'Yumshatish',
    kpis: 'Asosiy koʻrsatkichlar (KPI)',
    kpiName: 'Koʻrsatkich',
    kpiTarget: 'Maqsad',
    kpiFreq: 'Davriylik',
    products: 'Tavsiya etilgan NBU kreditlari',
    productsHint: 'Anketa maʼlumotlari asosida tanlangan eng mos NBU mahsulotlari',
    fit: 'Mos kelish',
    rate: 'Stavka',
    term: 'Muddat',
    amount: 'Summa',
    purpose: 'Maqsad',
    nextSteps: 'Keyingi qadamlar — bankka tayyor borish uchun',
    costStructure: 'Xarajatlar tarkibi',
    expenseBreakdown: 'Xarajatlar (oylik)',
    projection12m: '12 oylik prognoz',
    revenue: 'Daromad',
    costs: 'Xarajat',
    profit: 'Foyda',
    monthAbbrev: 'Oy',
    costsLabel: {
      payroll: 'Ish haqi',
      utilities: 'Kommunal',
      rawMaterials: 'Xom ashyo',
      loanPayment: 'Kredit toʻlovi',
      rent: 'Ijara',
      other: 'Boshqa',
    },
    riskTypes: { market: 'Bozor', operational: 'Operatsion', financial: 'Moliyaviy', regulatory: 'Tartibga soluvchi' },
    severity: { high: 'Yuqori', medium: 'Oʻrtacha', low: 'Past' },
    generatedAt: 'Yaratilgan',
    poweredBy: 'NBU AI Hub — Biznes-reja generatori',
    org: 'Tashkilot',
    activity: 'Asosiy faoliyat',
    address: 'Manzil',
    founder: 'Asoschisi',
    inn: 'INN',
    disclaimerTitle: 'Oʻz-oʻzini diagnostika, bank qarori emas',
    disclaimerBody: 'Ushbu hujjat va kreditga layoqatlilik bahosi anketa maʼlumotlari asosida avtomatik hisoblangan. Bu professional kredit tahlilchisining bahosi yoki bankning yakuniy qarori emas. Maʼqullanish ehtimolingizni yaxshiroq tushunish va NBU boʻlimida uchrashuvga tayyorlanish uchun foydalaning — haqiqiy shartlar va maʼqullash toʻliq ariza va hujjatlarni tekshirish asosida belgilanadi.',
  },
  ru: {
    title: 'Бизнес-план',
    feasibility: 'Оценка реалистичности проекта',
    verdicts: { high: 'Высокая', medium: 'Средняя', low: 'Низкая' },
    executive: 'Резюме',
    market: 'Контекст рынка',
    monthlyRevenue: 'Выручка / мес.',
    monthlyCosts: 'Расходы / мес.',
    monthlyProfit: 'Прибыль / мес.',
    breakeven: 'Точка безубыточности',
    grossMargin: 'Валовая маржа',
    ebitda: 'EBITDA маржа',
    months: 'мес.',
    operations: 'Операционная деятельность',
    supplyChain: 'Цепочка поставок',
    criticalDeps: 'Критические зависимости:',
    team: 'Команда',
    headcount: 'Численность',
    monthlyPayroll: 'ФОТ / мес.',
    annualPayroll: 'ФОТ / год',
    milestones: 'Дорожная карта',
    first90: 'Первые 90 дней',
    first6: 'За 6 месяцев',
    first12: 'За 12 месяцев',
    risks: 'Риски',
    mitigation: 'Митигация',
    kpis: 'KPI',
    kpiName: 'Показатель',
    kpiTarget: 'Цель',
    kpiFreq: 'Периодичность',
    products: 'Рекомендуемые продукты НБУ',
    productsHint: 'Подобраны на основании данных анкеты',
    fit: 'Соответствие',
    rate: 'Ставка',
    term: 'Срок',
    amount: 'Сумма',
    purpose: 'Цель',
    nextSteps: 'Следующие шаги — что сделать перед визитом в банк',
    costStructure: 'Структура расходов',
    expenseBreakdown: 'Расходы (мес.)',
    projection12m: 'Прогноз на 12 месяцев',
    revenue: 'Выручка',
    costs: 'Расходы',
    profit: 'Прибыль',
    monthAbbrev: 'Мес.',
    costsLabel: {
      payroll: 'ФОТ',
      utilities: 'Коммунальные',
      rawMaterials: 'Сырьё',
      loanPayment: 'Платёж по кредиту',
      rent: 'Аренда',
      other: 'Прочее',
    },
    riskTypes: { market: 'Рыночный', operational: 'Операционный', financial: 'Финансовый', regulatory: 'Регуляторный' },
    severity: { high: 'Высокая', medium: 'Средняя', low: 'Низкая' },
    generatedAt: 'Сгенерировано',
    poweredBy: 'NBU AI Hub — Генератор бизнес-плана',
    org: 'Организация',
    activity: 'Основная деятельность',
    address: 'Адрес',
    founder: 'Учредитель',
    inn: 'ИНН',
    disclaimerTitle: 'Самодиагностика, не решение банка',
    disclaimerBody: 'Этот документ и оценка кредитоспособности рассчитаны автоматически на основе данных анкеты. Это не профессиональная оценка кредитного аналитика и не итоговое решение банка. Используйте его, чтобы лучше понять свои шансы на одобрение и подготовиться к встрече в отделении НБУ — реальные условия и одобрение определяются на основании полной заявки и проверки документов.',
  },
}

const escape = (s) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

export function renderStandalonePlanHtml({ plan, inputs, candidates: _c, lang, orgName, generatedAt }) {
  const t = L[lang] || L.uz
  const f = plan.financials || {}
  const c = f.monthlyCosts || {}
  const proj = plan.projection12m || []
  const verdictColor = { high: '#16a34a', medium: '#d97706', low: '#dc2626' }[plan.feasibilityVerdict] || '#475569'
  const date = new Date(generatedAt).toLocaleString(lang === 'uz' ? 'uz-UZ' : 'ru-RU')

  const orgInfo = inputs?.organization
  const proj_obj = inputs?.project

  // Cost data for charts
  const costLabels = [t.costsLabel.payroll, t.costsLabel.utilities, t.costsLabel.rawMaterials,
                     t.costsLabel.loanPayment, t.costsLabel.rent, t.costsLabel.other]
  const costData = [c.payroll, c.utilities, c.rawMaterials, c.loanPayment, c.rent, c.other].map((v) => Number(v || 0))

  return `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escape(t.title)} — ${escape(orgName)}</title>
<style>
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
  color: #1e293b;
  background: #f4f6fa;
  line-height: 1.55;
  font-size: 14px;
}
.page { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }
.header {
  background: linear-gradient(135deg, #003d7c 0%, #1e6bb8 100%);
  color: #fff;
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 20px;
}
.header h1 { margin: 0 0 4px 0; font-size: 28px; font-weight: 800; }
.header .org-name { font-size: 18px; opacity: 0.92; margin: 0 0 16px 0; }
.header .meta {
  display: flex; flex-wrap: wrap; gap: 14px 24px;
  font-size: 13px; opacity: 0.88;
  border-top: 1px solid rgba(255,255,255,0.2);
  padding-top: 14px;
}
.header .meta span strong { color: #fff; font-weight: 700; }

.section {
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  break-inside: avoid;
}
.section h2 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 800;
  color: #003d7c;
}
.section p { margin: 0 0 8px 0; }
.section ul, .section ol { margin: 0; padding-left: 22px; }
.section li { padding-bottom: 4px; }

/* Top disclaimer — appears right after the header so it's the first
   thing readers see. */
.disclaimer {
  display: flex; gap: 14px; align-items: flex-start;
  background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
  border: 1px solid #bfdbfe;
  border-left: 4px solid #2563eb;
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 16px;
}
.disclaimer-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: #2563eb; color: #fff;
  display: grid; place-items: center;
  font-family: Georgia, serif; font-weight: 700; font-style: italic; font-size: 18px;
  flex-shrink: 0;
}
.disclaimer-body { flex: 1; }
.disclaimer-body strong {
  display: block; font-size: 13px; font-weight: 800; color: #1e40af;
  text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px;
}
.disclaimer-body p { margin: 0; font-size: 13px; line-height: 1.55; color: #1e3a8a; }

.verdict {
  display: flex; align-items: center; gap: 24px;
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.verdict-score {
  font-size: 56px; font-weight: 800; line-height: 1;
  color: ${verdictColor};
}
.verdict-score small { font-size: 22px; color: #94a3b8; font-weight: 600; }
.verdict-tag {
  display: inline-block; margin-top: 6px; padding: 4px 14px;
  background: ${verdictColor}; color: #fff;
  border-radius: 20px; font-size: 12px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.verdict-summary { font-size: 16px; line-height: 1.55; margin: 0; }

.metrics { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 16px; }
.metric {
  background: #fff; border-radius: 12px; padding: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.metric-val { font-size: 17px; font-weight: 800; color: #003d7c; }
.metric-val small { font-size: 11px; color: #94a3b8; font-weight: 600; }
.metric-val.is-neg { color: #dc2626; }

.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.chart-card { background: #fff; border-radius: 16px; padding: 18px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.chart-card h3 {
  margin: 0 0 8px 0; font-size: 13px; font-weight: 700;
  color: #475569; text-transform: uppercase; letter-spacing: 0.5px;
}
.chart-h { height: 240px; position: relative; }
.chart-h-tall { height: 320px; position: relative; }
.chart-fallback { color: #94a3b8; font-size: 12px; padding: 12px; border: 1px dashed #cbd5e1; border-radius: 8px; text-align: center; }

.team-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
.team-stats > div { background: #f8fafc; border-radius: 10px; padding: 12px 14px; }
.team-stats span { display: block; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
.team-stats strong { font-size: 16px; color: #003d7c; }

.deps {
  margin-top: 12px; padding: 12px;
  background: #fffbeb; border-radius: 8px; border-left: 3px solid #f59e0b;
}

.milestones { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.milestone-col h4 { margin: 0 0 8px 0; font-size: 13px; font-weight: 700; color: #003d7c; text-transform: uppercase; letter-spacing: 0.5px; }
.milestone-col ul { font-size: 13px; line-height: 1.5; padding-left: 16px; }

.risks { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.risk { background: #f8fafc; border-radius: 10px; padding: 14px 16px; border-left: 4px solid #94a3b8; }
.risk.high { border-left-color: #dc2626; background: #fef2f2; }
.risk.medium { border-left-color: #f59e0b; background: #fffbeb; }
.risk.low { border-left-color: #16a34a; background: #f0fdf4; }
.risk-h { display: flex; justify-content: space-between; margin-bottom: 6px; }
.risk-type, .risk-sev { font-size: 11px; font-weight: 700; text-transform: uppercase; }
.risk-type { color: #475569; }
.risk-sev { color: #94a3b8; }
.risk-desc { font-size: 13px; margin-bottom: 6px; }
.risk-mit { font-size: 12px; color: #475569; }

.kpi-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.kpi-table th { text-align: left; padding: 8px 12px; background: #f8fafc; font-size: 11px; text-transform: uppercase; color: #475569; font-weight: 700; letter-spacing: 0.5px; }
.kpi-table td { padding: 8px 12px; border-top: 1px solid #f1f5f9; }

.product { border: 1.5px solid #003d7c; border-radius: 12px; padding: 18px 20px; background: linear-gradient(135deg, rgba(0,61,124,0.04) 0%, #fff 60%); margin-bottom: 12px; }
.product-h { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.product-h h3 { margin: 0; color: #003d7c; font-size: 17px; font-weight: 800; }
.fit-badge { background: #003d7c; color: #fff; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.product-meta { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 8px; }
.product-meta div span { display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; }
.product-meta div strong { font-size: 13px; color: #1e293b; }
.product-purpose { font-size: 13px; color: #475569; margin-bottom: 8px; }
.product-rationale { font-size: 14px; line-height: 1.55; margin: 0; }

.assessment {
  background: #f1f5f9; border-left: 3px solid #003d7c;
  padding: 12px 14px; border-radius: 8px; margin-bottom: 16px;
  font-size: 13px;
}

.footer-note { text-align: center; color: #94a3b8; font-size: 11px; margin-top: 24px; }

/* Print */
@media print {
  body { background: #fff; }
  .page { padding: 12px; }
  .section, .verdict, .metric, .chart-card, .header { box-shadow: none; }
  .section, .chart-card { page-break-inside: avoid; }
}
</style>
</head>
<body>
<div class="page">

<header class="header">
  <h1>${escape(t.title)}</h1>
  <p class="org-name">${escape(orgName)}</p>
  <div class="meta">
    ${orgInfo?.mainActivity ? `<span><strong>${escape(t.activity)}:</strong> ${escape(orgInfo.mainActivity)}</span>` : ''}
    ${orgInfo?.address ? `<span><strong>${escape(t.address)}:</strong> ${escape(orgInfo.address)}</span>` : ''}
    ${orgInfo?.founder ? `<span><strong>${escape(t.founder)}:</strong> ${escape(orgInfo.founder)}</span>` : ''}
    ${orgInfo?.inn ? `<span><strong>${escape(t.inn)}:</strong> ${escape(orgInfo.inn)}</span>` : ''}
    <span><strong>${escape(t.generatedAt)}:</strong> ${escape(date)}</span>
  </div>
</header>

<section class="disclaimer">
  <div class="disclaimer-icon">i</div>
  <div class="disclaimer-body">
    <strong>${escape(t.disclaimerTitle)}</strong>
    <p>${escape(t.disclaimerBody)}</p>
  </div>
</section>

<section class="verdict">
  <div>
    <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#64748b; letter-spacing:0.5px;">${escape(t.feasibility)}</div>
    <div class="verdict-score">${plan.feasibilityScore || 0}<small>/100</small></div>
    <span class="verdict-tag">${escape(t.verdicts[plan.feasibilityVerdict] || t.verdicts.medium)}</span>
  </div>
  <p class="verdict-summary">${escape(plan.summary || '')}</p>
</section>

${plan.executiveSummary ? `
<section class="section">
  <h2>${escape(t.executive)}</h2>
  <p>${escape(plan.executiveSummary)}</p>
</section>` : ''}

${plan.marketContext ? `
<section class="section">
  <h2>${escape(t.market)}</h2>
  <p>${escape(plan.marketContext)}</p>
</section>` : ''}

<div class="metrics">
  <div class="metric"><div class="metric-label">${escape(t.monthlyRevenue)}</div><div class="metric-val">${fmt(f.monthlyRevenue)} <small>UZS</small></div></div>
  <div class="metric"><div class="metric-label">${escape(t.monthlyCosts)}</div><div class="metric-val">${fmt(c.total)} <small>UZS</small></div></div>
  <div class="metric"><div class="metric-label">${escape(t.monthlyProfit)}</div><div class="metric-val ${Number(f.monthlyProfit||0) < 0 ? 'is-neg' : ''}">${fmt(f.monthlyProfit)} <small>UZS</small></div></div>
  <div class="metric"><div class="metric-label">${escape(t.breakeven)}</div><div class="metric-val">${f.breakevenMonths || '—'} <small>${escape(t.months)}</small></div></div>
  <div class="metric"><div class="metric-label">${escape(t.grossMargin)}</div><div class="metric-val">${fmtPct(f.grossMarginPct)}</div></div>
  <div class="metric"><div class="metric-label">${escape(t.ebitda)}</div><div class="metric-val">${fmtPct(f.ebitdaMarginPct)}</div></div>
</div>

<div class="charts-row">
  <div class="chart-card">
    <h3>${escape(t.costStructure)}</h3>
    <div class="chart-h"><canvas id="costDonut"></canvas></div>
  </div>
  <div class="chart-card">
    <h3>${escape(t.expenseBreakdown)}</h3>
    <div class="chart-h"><canvas id="costBar"></canvas></div>
  </div>
</div>

${proj.length ? `
<div class="chart-card" style="margin-bottom:16px;">
  <h3>${escape(t.projection12m)}</h3>
  <div class="chart-h-tall"><canvas id="projLine"></canvas></div>
</div>` : ''}

${f.assessment ? `<p class="assessment">${escape(f.assessment)}</p>` : ''}

${plan.operations ? `
<section class="section">
  <h2>${escape(t.operations)}</h2>
  ${plan.operations.processFlow?.length ? `<ul>${plan.operations.processFlow.map((s) => `<li>${escape(s)}</li>`).join('')}</ul>` : ''}
  ${plan.operations.supplyChain ? `<p><strong>${escape(t.supplyChain)}:</strong> ${escape(plan.operations.supplyChain)}</p>` : ''}
  ${plan.operations.criticalDependencies?.length ? `
    <div class="deps">
      <strong>${escape(t.criticalDeps)}</strong>
      <ul>${plan.operations.criticalDependencies.map((d) => `<li>${escape(d)}</li>`).join('')}</ul>
    </div>` : ''}
</section>` : ''}

${plan.team ? `
<section class="section">
  <h2>${escape(t.team)}</h2>
  <div class="team-stats">
    <div><span>${escape(t.headcount)}</span><strong>${plan.team.totalHeadcount || 0}</strong></div>
    <div><span>${escape(t.monthlyPayroll)}</span><strong>${fmt(plan.team.monthlyPayroll)} UZS</strong></div>
    <div><span>${escape(t.annualPayroll)}</span><strong>${fmt(plan.team.annualPayroll)} UZS</strong></div>
  </div>
  ${plan.team.assessment ? `<p>${escape(plan.team.assessment)}</p>` : ''}
</section>` : ''}

${plan.milestones ? `
<section class="section">
  <h2>${escape(t.milestones)}</h2>
  <div class="milestones">
    <div class="milestone-col">
      <h4>${escape(t.first90)}</h4>
      <ul>${(plan.milestones.first90Days || []).map((m) => `<li>${escape(m)}</li>`).join('')}</ul>
    </div>
    <div class="milestone-col">
      <h4>${escape(t.first6)}</h4>
      <ul>${(plan.milestones.first6Months || []).map((m) => `<li>${escape(m)}</li>`).join('')}</ul>
    </div>
    <div class="milestone-col">
      <h4>${escape(t.first12)}</h4>
      <ul>${(plan.milestones.first12Months || []).map((m) => `<li>${escape(m)}</li>`).join('')}</ul>
    </div>
  </div>
</section>` : ''}

${plan.risks?.length ? `
<section class="section">
  <h2>${escape(t.risks)}</h2>
  <div class="risks">
    ${plan.risks.map((r) => `
      <div class="risk ${escape(r.severity || 'medium')}">
        <div class="risk-h">
          <span class="risk-type">${escape(t.riskTypes[r.type] || r.type || '')}</span>
          <span class="risk-sev">${escape(t.severity[r.severity] || r.severity || '')}</span>
        </div>
        <div class="risk-desc">${escape(r.description || '')}</div>
        <div class="risk-mit"><strong>${escape(t.mitigation)}:</strong> ${escape(r.mitigation || '')}</div>
      </div>`).join('')}
  </div>
</section>` : ''}

${plan.kpis?.length ? `
<section class="section">
  <h2>${escape(t.kpis)}</h2>
  <table class="kpi-table">
    <thead><tr><th>${escape(t.kpiName)}</th><th>${escape(t.kpiTarget)}</th><th>${escape(t.kpiFreq)}</th></tr></thead>
    <tbody>
      ${plan.kpis.map((k) => `<tr><td>${escape(k.name || '')}</td><td>${escape(k.target || '')}</td><td>${escape(k.frequency || '')}</td></tr>`).join('')}
    </tbody>
  </table>
</section>` : ''}

${plan.recommendedProducts?.length ? `
<section class="section">
  <h2>${escape(t.products)}</h2>
  <p style="color:#64748b; font-size:13px; margin-bottom:14px;">${escape(t.productsHint)}</p>
  ${plan.recommendedProducts.map((p) => `
    <div class="product">
      <div class="product-h">
        <h3>${escape(p.name || '')}</h3>
        <span class="fit-badge">${escape(t.fit)}: ${p.fitScore || 0}/100</span>
      </div>
      <div class="product-meta">
        <div><span>${escape(t.rate)}</span><strong>${escape(p.rate || '')}</strong></div>
        <div><span>${escape(t.term)}</span><strong>${escape(p.term || '')}</strong></div>
        <div><span>${escape(t.amount)}</span><strong>${escape(p.amount || '')}</strong></div>
      </div>
      <div class="product-purpose"><strong>${escape(t.purpose)}:</strong> ${escape(p.purpose || '')}</div>
      <p class="product-rationale">${escape(p.rationale || '')}</p>
    </div>`).join('')}
</section>` : ''}

${plan.actionableNextSteps?.length ? `
<section class="section">
  <h2>${escape(t.nextSteps)}</h2>
  <ol>${plan.actionableNextSteps.map((s) => `<li>${escape(s)}</li>`).join('')}</ol>
</section>` : ''}

<p class="footer-note">${escape(t.poweredBy)}</p>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
<script>
(function() {
  if (typeof Chart === 'undefined') {
    document.querySelectorAll('.chart-h, .chart-h-tall').forEach(function(el) {
      el.innerHTML = '<div class="chart-fallback">${escape(lang === 'uz' ? 'Diagrammalarni koʻrish uchun internetga ulaning.' : 'Для отображения графиков нужен интернет.')}</div>';
    });
    return;
  }

  var costLabels = ${JSON.stringify(costLabels)};
  var costData = ${JSON.stringify(costData)};
  var proj = ${JSON.stringify(proj)};
  var L = ${JSON.stringify({ revenue: t.revenue, costs: t.costs, profit: t.profit, monthAbbrev: t.monthAbbrev })};

  var donutEl = document.getElementById('costDonut');
  if (donutEl) new Chart(donutEl, {
    type: 'doughnut',
    data: {
      labels: costLabels,
      datasets: [{ data: costData, backgroundColor: ['#003d7c','#1e6bb8','#2957A2','#5b89c6','#9bb5d6','#cad6e6'], borderWidth: 0 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { font: { size: 11 }, boxWidth: 12 } } },
      cutout: '60%'
    }
  });

  var barEl = document.getElementById('costBar');
  if (barEl) new Chart(barEl, {
    type: 'bar',
    data: { labels: costLabels, datasets: [{ data: costData, backgroundColor: '#003d7c', borderRadius: 6 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { callback: function(v) { return v.toLocaleString('ru-RU'); } } } }
    }
  });

  var lineEl = document.getElementById('projLine');
  if (lineEl && proj.length) new Chart(lineEl, {
    type: 'line',
    data: {
      labels: proj.map(function(p) { return L.monthAbbrev + ' ' + p.month; }),
      datasets: [
        { label: L.revenue, data: proj.map(function(p) { return Number(p.revenue||0); }), borderColor: '#16a34a', backgroundColor: 'rgba(22,163,74,0.12)', tension: 0.35, fill: true },
        { label: L.costs, data: proj.map(function(p) { return Number(p.costs||0); }), borderColor: '#dc2626', backgroundColor: 'rgba(220,38,38,0.08)', tension: 0.35, fill: false },
        { label: L.profit, data: proj.map(function(p) { return Number(p.profit||0); }), borderColor: '#003d7c', tension: 0.35, fill: false, borderDash: [4,4] }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: false, ticks: { callback: function(v) { return v.toLocaleString('ru-RU'); } } } }
    }
  });
})();
</script>
</body>
</html>`
}
