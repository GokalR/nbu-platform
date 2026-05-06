<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import AddressCascade from './AddressCascade.vue'

const props = defineProps({
  category: { type: Object, required: true },
  sphereIdx: { type: Number, required: true },
  sphereCount: { type: Number, required: true },
  initialAnswers: { type: Array, default: () => [] },
})
const emit = defineEmits(['next', 'back'])

const { t, locale } = useI18n()

const initMap = {}
props.initialAnswers.forEach((a) => {
  initMap[a.question_id] = a.answer
})
const answers = ref({ ...initMap })

function setAnswer(id, val) {
  answers.value = { ...answers.value, [id]: val }
}

function isChecked(qid, opt) {
  return (answers.value[qid] || '').split(',').filter(Boolean).includes(opt)
}
function toggleCheckbox(qid, opt) {
  const current = (answers.value[qid] || '').split(',').filter(Boolean)
  const next = current.includes(opt) ? current.filter((v) => v !== opt) : [...current, opt]
  setAnswer(qid, next.join(','))
}

const relatedCount = computed(() =>
  Math.max(0, Math.min(20, parseInt(answers.value['related_companies_count'] || '0', 10) || 0)),
)

function handleNext() {
  const baseAnswers = props.category.questions.map((q) => ({
    question_id: q.id,
    question_text_ru: q.text.ru,
    question_text_uz: q.text.uz,
    answer: answers.value[q.id] || '',
  }))
  const dyn = []
  for (let i = 0; i < relatedCount.value; i++) {
    const key = `related_company_inn_${i}`
    dyn.push({
      question_id: key,
      question_text_ru: `Связанная компания ${i + 1} — ИНН`,
      question_text_uz: `Bog'liq kompaniya ${i + 1} — INN`,
      answer: answers.value[key] || '',
    })
  }
  emit('next', { answers: [...baseAnswers, ...dyn] })
}

const isLast = computed(() => props.sphereIdx === props.sphereCount - 1)

const inputCls =
  'w-full px-4 py-3 border border-outline-variant rounded-btn text-sm bg-white text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors'
</script>

<template>
  <div class="space-y-6">
    <div class="text-center space-y-2">
      <div class="inline-flex items-center justify-center w-14 h-14 bg-primary/10 rounded-2xl">
        <AppIcon name="quiz" class="text-primary text-2xl" />
      </div>
      <h2 class="text-2xl font-bold text-on-surface">{{ t('smeProfile.questions.title') }}</h2>
      <p class="text-sm text-on-surface-variant">
        {{
          t('smeProfile.questions.subtitle', {
            n: sphereIdx + 1,
            total: sphereCount,
            category: locale === 'ru' ? category.name.ru : category.name.uz,
          })
        }}
      </p>
    </div>

    <div class="bg-surface-container-lowest rounded-card p-6 shadow-sm space-y-7">
      <div v-for="(q, idx) in category.questions" :key="q.id" class="space-y-2">
        <label class="block text-sm font-semibold text-on-surface">
          <span class="text-primary mr-1.5">{{ idx + 1 }}.</span>
          {{ locale === 'ru' ? q.text.ru : q.text.uz }}
        </label>

        <input
          v-if="q.type === 'text'"
          type="text"
          :value="answers[q.id] || ''"
          @input="setAnswer(q.id, $event.target.value)"
          :class="inputCls"
        />

        <input
          v-else-if="q.type === 'number'"
          type="number"
          min="0"
          :value="answers[q.id] || ''"
          @input="setAnswer(q.id, $event.target.value)"
          :class="inputCls"
        />

        <textarea
          v-else-if="q.type === 'textarea'"
          rows="3"
          :value="answers[q.id] || ''"
          @input="setAnswer(q.id, $event.target.value)"
          :class="[inputCls, 'resize-y']"
        />

        <select
          v-else-if="q.type === 'select'"
          :value="answers[q.id] || ''"
          @change="setAnswer(q.id, $event.target.value)"
          :class="[inputCls, 'cursor-pointer']"
        >
          <option value="">{{ t('smeProfile.selectPlaceholder') }}</option>
          <option v-for="o in (locale === 'ru' ? q.options.ru : q.options.uz)" :key="o" :value="o">
            {{ o }}
          </option>
        </select>

        <div v-else-if="q.type === 'radio'" class="space-y-1 pt-1">
          <label
            v-for="o in (locale === 'ru' ? q.options.ru : q.options.uz)"
            :key="o"
            class="flex items-center gap-3 cursor-pointer p-2 rounded-btn hover:bg-primary/5"
          >
            <input
              type="radio"
              :name="`${q.id}_s${sphereIdx}`"
              :value="o"
              :checked="answers[q.id] === o"
              @change="setAnswer(q.id, o)"
              class="w-4 h-4 accent-primary"
            />
            <span class="text-sm text-on-surface">{{ o }}</span>
          </label>
        </div>

        <div v-else-if="q.type === 'checkbox'" class="space-y-1 pt-1">
          <label
            v-for="o in (locale === 'ru' ? q.options.ru : q.options.uz)"
            :key="o"
            class="flex items-center gap-3 cursor-pointer p-2 rounded-btn hover:bg-primary/5"
          >
            <input
              type="checkbox"
              :checked="isChecked(q.id, o)"
              @change="toggleCheckbox(q.id, o)"
              class="w-4 h-4 accent-primary rounded"
            />
            <span class="text-sm text-on-surface">{{ o }}</span>
          </label>
        </div>

        <AddressCascade
          v-else-if="q.type === 'address_cascade'"
          :model-value="answers[q.id] || ''"
          @update:model-value="setAnswer(q.id, $event)"
        />

        <!-- Dynamic INN inputs after related_companies_count -->
        <div v-if="q.id === 'related_companies_count' && relatedCount > 0" class="mt-3 space-y-2 pl-1">
          <div v-for="i in relatedCount" :key="i">
            <label class="block text-xs font-semibold text-on-surface-variant mb-1">
              {{ t('smeProfile.questions.relatedCompany', { n: i }) }}
            </label>
            <input
              type="text"
              :value="answers[`related_company_inn_${i - 1}`] || ''"
              @input="setAnswer(`related_company_inn_${i - 1}`, $event.target.value)"
              :class="inputCls"
              :placeholder="t('smeProfile.questions.relatedCompanyPlaceholder', { n: i })"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="flex gap-3">
      <button
        class="inline-flex items-center justify-center gap-2 flex-1 px-5 py-3 bg-surface-container text-on-surface border border-outline-variant rounded-btn text-sm font-semibold hover:bg-surface-container-high transition-all"
        @click="emit('back')"
      >
        <AppIcon name="arrow_back" />
        {{ t('smeProfile.back') }}
      </button>
      <button
        class="inline-flex items-center justify-center gap-2 flex-1 px-5 py-3 bg-primary text-white rounded-btn text-sm font-semibold hover:bg-primary/90 active:scale-[0.99] transition-all shadow-sm"
        @click="handleNext"
      >
        {{ isLast ? t('smeProfile.summary.title') : t('smeProfile.next') }}
        <AppIcon name="arrow_forward" />
      </button>
    </div>
  </div>
</template>
