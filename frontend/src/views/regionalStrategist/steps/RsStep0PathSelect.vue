<script setup>
import { computed, ref } from 'vue'
import { useRsLang } from '@/composables/useRsLang'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'

const emit = defineEmits(['select'])
const { lang } = useRsLang()

const T = {
  ru: {
    badge: 'AI БИЗНЕС-СОВЕТНИК',
    heading: 'С чего начнём?',
    sub: 'Выберите свой путь — и мы зададим правильные вопросы, чтобы дать вам точный анализ',
    cta: 'Начать',
    trust: 'Ваши данные не передаются третьим лицам и используются только для анализа',
    paths: [
      {
        title: 'Хочу начать бизнес',
        subtitle: 'У меня есть идея, и я хочу понять — стоит ли начинать',
        bullets: [
          'Анализ рынка в вашем районе',
          'Расчёт стартовых затрат',
          'Оценка конкуренции',
          'Подбор кредитных продуктов NBU',
          'Пошаговый план действий',
        ],
      },
      {
        title: 'У меня уже есть бизнес',
        subtitle: 'Хочу развить, расширить или решить проблему',
        bullets: [
          'Диагностика текущего состояния',
          'Анализ финансовых показателей',
          'Выявление точек роста',
          'Подбор подходящих кредитов NBU',
          'Стратегия масштабирования',
        ],
      },
    ],
  },
  uz: {
    badge: 'AI BIZNES-MASLAHATChI',
    heading: 'Nimadan boshlaymiz?',
    sub: 'O'z yo'lingizni tanlang — va biz sizga aniq tahlil berish uchun to'g'ri savollar beramiz',
    cta: 'Boshlash',
    trust: 'Ma'lumotlaringiz uchinchi shaxslarga berilmaydi va faqat tahlil uchun ishlatiladi',
    paths: [
      {
        title: 'Biznes boshlamoqchiman',
        subtitle: 'Menda g'oya bor va tushunmoqchiman — boshlashga arziydimi',
        bullets: [
          'Hududingizdagi bozor tahlili',
          'Boshlang'ich xarajatlar hisobi',
          'Raqobat bahosi',
          'NBU kredit mahsulotlarini tanlash',
          'Bosqichma-bosqich harakat rejasi',
        ],
      },
      {
        title: 'Menda biznes bor',
        subtitle: 'Rivojlantirish, kengaytirish yoki muammoni hal qilmoqchiman',
        bullets: [
          'Joriy holatni tashxislash',
          'Moliyaviy ko'rsatkichlar tahlili',
          'O'sish nuqtalarini aniqlash',
          'NBU mos kreditlarini tanlash',
          'Kengaytirish strategiyasi',
        ],
      },
    ],
  },
}

const t = computed(() => T[lang.value])
const selected = ref(null)

const PATH_IDS = ['new', 'existing']
const PATH_STYLES = [
  { iconBg: 'bg-navy-900/10', iconColor: 'text-navy-900', gradient: 'linear-gradient(90deg, #193F72, #2957A2)' },
  { iconBg: 'bg-gold-500/10', iconColor: 'text-gold-500', gradient: 'linear-gradient(90deg, #D7B56D, #C4A35A)' },
]
const PATH_ICONS = ['rocket', 'building-2']

const select = (id) => { selected.value = id }
const proceed = () => {
  if (selected.value) emit('select', selected.value)
}
</script>

<template>
  <div class="animate-rs-fade-in-up">
    <div class="text-center mb-10">
      <span class="inline-flex items-center text-[12px] font-semibold text-gold-500 bg-gold-500/[0.08] rounded-[6px] py-1 px-3">
        {{ t.badge }}
      </span>
      <h1 class="text-[28px] md:text-[32px] font-bold text-carbon mt-4 tracking-[-0.5px]">{{ t.heading }}</h1>
      <p class="text-[15px] md:text-[16px] text-[#898989] leading-[1.5] mt-2 max-w-[520px] mx-auto">{{ t.sub }}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <button
        v-for="(id, idx) in PATH_IDS" :key="id"
        type="button"
        @click="select(id)"
        :class="[
          'relative text-left rounded-[14px] border-[2px] p-6 md:p-8 transition-all duration-200',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-500/40',
          selected === id
            ? 'border-navy-900 bg-white shadow-[0_4px_20px_rgba(25,63,114,0.12)]'
            : 'border-rs-border bg-white hover:border-steel-500/50 hover:shadow-[0_2px_12px_rgba(0,0,0,0.06)]',
        ]"
      >
        <!-- selection dot -->
        <div
          :class="[
            'absolute top-5 right-5 w-[22px] h-[22px] rounded-full border-[2px] transition-all duration-200 flex items-center justify-center',
            selected === id ? 'border-navy-900 bg-navy-900' : 'border-rs-border bg-white',
          ]"
        >
          <svg v-if="selected === id" width="10" height="8" viewBox="0 0 10 8" fill="none">
            <path d="M1 4L3.5 6.5L9 1" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>

        <div :class="['w-[52px] h-[52px] rounded-[12px] flex items-center justify-center mb-5', PATH_STYLES[idx].iconBg]">
          <RsIcon :name="PATH_ICONS[idx]" :size="26" :stroke-width="1.75" :class="PATH_STYLES[idx].iconColor" />
        </div>

        <h2 class="text-[18px] md:text-[20px] font-bold text-carbon">{{ t.paths[idx].title }}</h2>
        <p class="text-[13px] md:text-[14px] font-normal text-[#898989] mt-1">{{ t.paths[idx].subtitle }}</p>

        <ul class="mt-5 space-y-[10px]">
          <li v-for="b in t.paths[idx].bullets" :key="b" class="flex items-start gap-[10px]">
            <span :class="['w-[6px] h-[6px] rounded-full mt-[6px] shrink-0', selected === id ? 'bg-navy-900' : 'bg-steel-500/50']" />
            <span class="text-[13px] text-[#898989] leading-[1.4]">{{ b }}</span>
          </li>
        </ul>

        <div
          :class="[
            'absolute bottom-0 left-4 right-4 h-[3px] rounded-full transition-opacity duration-200',
            selected === id ? 'opacity-100' : 'opacity-0',
          ]"
          :style="{ background: PATH_STYLES[idx].gradient }"
        />
      </button>
    </div>

    <div class="mt-8 flex justify-center">
      <button
        type="button"
        :disabled="!selected"
        @click="proceed"
        :class="[
          'inline-flex items-center text-[15px] font-semibold rounded-btn py-[14px] px-10 transition-all duration-200',
          selected ? 'text-white bg-navy-900 hover:bg-navy-700 cursor-pointer' : 'text-steel-500 bg-gray-100 cursor-not-allowed',
        ]"
      >
        {{ t.cta }}
        <RsIcon name="arrow-right" :size="18" :stroke-width="2.25" class="ml-2" />
      </button>
    </div>

    <p class="text-center text-[12px] text-steel-500 mt-4">{{ t.trust }}</p>
  </div>
</template>
