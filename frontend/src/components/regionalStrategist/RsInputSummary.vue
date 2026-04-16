<script setup>
import { computed } from 'vue'

const props = defineProps({
  profile: { type: Object, required: true },
  finance: { type: Object, required: true },
  lang: { type: String, default: 'ru' },
})

const L = {
  ru: {
    profile: 'Профиль',
    finance: 'Финансы',
    idea: 'Идея',
    empty: '—',
    fields: {
      name: 'Имя',
      ageRange: 'Возраст',
      gender: 'Пол',
      hasHigherEducation: 'Высшее образование',
      educationField: 'Направление образования',
      maritalStatus: 'Семейное положение',
      dependents: 'Иждивенцы',
      currentStatus: 'Текущий статус',
      experienceLevel: 'Опыт работы',
      domainExperience: 'Опыт в отрасли',
      hasTraining: 'Проходил обучение',
      hasMentor: 'Есть ментор',
      viloyat: 'Область',
      hudud: 'Город / туман',
      mahalla: 'Махалля',
      urbanRural: 'Тип местности',
      businessAge: 'Возраст бизнеса',
      employeeCount: 'Число сотрудников',
      entityType: 'Тип субъекта',
      registrationForm: 'Форма регистрации',
      businessSize: 'Размер бизнеса',
      businessDirection: 'Направление бизнеса',
      hasBusinessPlan: 'Есть бизнес-план',
      needsLoan: 'Нужен кредит',
      hasOwnFunds: 'Собственные средства',
      hasCollateral: 'Есть залог',
      collateralType: 'Тип залога',
      loanAmount: 'Сумма кредита',
      monthlyIncome: 'Доход/мес',
      monthlyExpenses: 'Расходы/мес',
      existingDebt: 'Текущий долг',
      hasRegisteredBusiness: 'Бизнес зарегистрирован',
      businessGoal: 'Цель кредита',
      timeline: 'Сроки',
      hasSpace: 'Есть помещение',
      hasEquipment: 'Есть оборудование',
      ideaDescription: 'Описание идеи',
      whyThisBusiness: 'Почему этот бизнес',
      targetCustomer: 'Целевой клиент',
      mainProblem: 'Главная проблема',
    },
  },
  uz: {
    profile: 'Профил',
    finance: 'Молия',
    idea: 'Ғоя',
    empty: '—',
    fields: {
      name: 'Исм', ageRange: 'Ёш', gender: 'Жинси',
      hasHigherEducation: 'Олий таълим', educationField: 'Таълим йўналиши',
      maritalStatus: 'Оилавий ҳолат', dependents: 'Иждивентлар',
      currentStatus: 'Ҳозирги ҳолат', experienceLevel: 'Иш тажрибаси',
      domainExperience: 'Соҳадаги тажриба', hasTraining: 'Ўқитишдан ўтган',
      hasMentor: 'Ментор бор', viloyat: 'Вилоят', hudud: 'Шаҳар / туман',
      mahalla: 'Маҳалла', urbanRural: 'Жой тури',
      businessAge: 'Бизнес ёши', employeeCount: 'Ходимлар',
      entityType: 'Субъект тури', registrationForm: 'Рўйхатга олиш шакли',
      businessSize: 'Бизнес ҳажми',
      businessDirection: 'Бизнес йўналиши', hasBusinessPlan: 'Бизнес-режа бор',
      needsLoan: 'Кредит керак', hasOwnFunds: 'Ўз маблағлари',
      hasCollateral: 'Гаров бор', collateralType: 'Гаров тури',
      loanAmount: 'Кредит суммаси', monthlyIncome: 'Ойлик даромад',
      monthlyExpenses: 'Ойлик харажат', existingDebt: 'Ҳозирги қарз',
      hasRegisteredBusiness: 'Бизнес рўйхатдан ўтган', businessGoal: 'Кредит мақсади',
      timeline: 'Муддатлар', hasSpace: 'Бино бор', hasEquipment: 'Жиҳоз бор',
      ideaDescription: 'Ғоя тавсифи', whyThisBusiness: 'Нега бу бизнес',
      targetCustomer: 'Мақсадли мижоз', mainProblem: 'Асосий муаммо',
    },
  },
}

const PROFILE_FIELDS = ['name', 'ageRange', 'gender', 'maritalStatus', 'dependents',
  'hasHigherEducation', 'educationField', 'currentStatus',
  'experienceLevel', 'domainExperience', 'hasTraining', 'hasMentor',
  'viloyat', 'hudud', 'mahalla', 'urbanRural',
  'entityType', 'registrationForm', 'businessAge', 'employeeCount', 'businessSize']

const FINANCE_FIELDS = ['businessDirection', 'needsLoan', 'loanAmount',
  'hasOwnFunds', 'hasCollateral', 'collateralType',
  'monthlyIncome', 'monthlyExpenses', 'existingDebt',
  'hasRegisteredBusiness', 'businessGoal', 'timeline',
  'hasSpace', 'hasEquipment']

const IDEA_FIELDS = ['hasBusinessPlan', 'ideaDescription', 'whyThisBusiness', 'targetCustomer', 'mainProblem']

const t = computed(() => L[props.lang] ?? L.ru)

const formatValue = (v) => {
  if (v === null || v === undefined || v === '') return t.value.empty
  if (typeof v === 'number') return v.toLocaleString('ru-RU')
  const s = String(v).trim()
  if (!s) return t.value.empty
  // If the value looks numeric (with cleanup), format it.
  const num = Number(s.replace(/[^\d.-]/g, ''))
  if (/^\s*[\d\s.,-]+\s*$/.test(s) && Number.isFinite(num) && num >= 1000) {
    return num.toLocaleString('ru-RU')
  }
  return s
}

const buildRows = (fields, src) =>
  fields
    .map((f) => ({ key: f, label: t.value.fields[f] ?? f, value: formatValue(src[f]) }))
    .filter((r) => r.value !== t.value.empty)

const profileRows = computed(() => buildRows(PROFILE_FIELDS, props.profile))
const financeRows = computed(() => buildRows(FINANCE_FIELDS, props.finance))
const ideaRows = computed(() => buildRows(IDEA_FIELDS, props.finance))
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div v-for="block in [
      { title: t.profile, rows: profileRows },
      { title: t.finance, rows: financeRows },
      { title: t.idea, rows: ideaRows },
    ]" :key="block.title"
      class="border border-rs-border rounded-[10px] overflow-hidden"
    >
      <div class="px-4 py-3 bg-navy-900/[0.03] border-b border-rs-border">
        <span class="font-sans text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ block.title }}</span>
        <span class="ml-2 font-mono text-[11px] text-steel-500/70">{{ block.rows.length }}</span>
      </div>
      <div v-if="block.rows.length" class="divide-y divide-rs-border">
        <div v-for="r in block.rows" :key="r.key" class="flex gap-3 py-[10px] px-4">
          <div class="w-[45%] shrink-0 text-[12px] font-medium text-steel-500">{{ r.label }}</div>
          <div class="flex-1 text-[13px] font-medium text-carbon break-words">{{ r.value }}</div>
        </div>
      </div>
      <div v-else class="py-6 px-4 text-[12px] text-steel-500 italic">
        {{ lang === 'uz' ? 'Бўш' : 'Не заполнено' }}
      </div>
    </div>
  </div>
</template>
