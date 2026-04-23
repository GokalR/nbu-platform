<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import RsHeader from '@/components/regionalStrategist/RsHeader.vue'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'
import { useRsLang } from '@/composables/useRsLang'
import { CREDIT_TOTAL } from '@/data/regionalStrategist/credit-products'
import { CITY_LIST } from '@/data/regionalStrategist/cities'

const { lang } = useRsLang()
const router = useRouter()

const T = {
  ru: {
    badge: 'NATIONAL BANK OF UZBEKISTAN',
    heroTitle: 'AI Бизнес-советник',
    heroLine2: 'для МСБ',
    heroSub: 'Заполните анкету, загрузите финансы и получите персональный план: какой бизнес подходит именно вам в вашем городе + подходящий кредит NBU из каталога «Кредиты 2026»',
    cta: 'Начать анализ',
    trust: 'Банковское шифрование',
    stat1n: String(CREDIT_TOTAL), stat1l: 'реальных продуктов NBU',
    stat2n: String(CITY_LIST.length), stat2l: 'пилотных города',
    stat3n: '2010–2025', stat3l: 'данных farstat.uz',
    stat4n: '5', stat4l: 'минут на заполнение',
    howBadge: 'КАК ЭТО РАБОТАЕТ',
    howHeading: 'От анкеты — к бизнес-плану',
    howSub: 'Расскажите о себе и бизнес-идее. Платформа совместит ваши данные со статистикой города и каталогом NBU — и предложит, что и где запускать.',
    stepLabel: 'ШАГ',
    steps: [
      { title: 'Профиль', desc: 'ЮЛ или ИП, опыт, образование, команда' },
      { title: 'Финансы', desc: 'Загрузите финансовые данные вашего бизнеса' },
      { title: 'Анализ', desc: 'AI анализирует ваши данные × статистику города × каталог NBU' },
      { title: 'Результаты, план', desc: 'Рекомендация + лучший кредитный продукт NBU' },
    ],
    ctaTitle: 'Готовы начать?',
    ctaSub: 'Получите персональный AI-анализ бизнес-возможностей за 5 минут',
    ctaTrust: 'Данные шифруются на серверах банка',
    footer: '© 2026 NBU — Национальный банк Узбекистана',
    privacy: 'Конфиденциальность',
    footerDesc: 'AI Бизнес-советник',
    cardScore: 'AI Оценка', cardSwot: 'SWOT-анализ', cardCredit: 'Кредит NBU', cardMonths: 'мес',
  },
  uz: {
    badge: 'OʻZBEKISTON MILLIY BANKI',
    heroTitle: 'AI Biznes-maslahatchi',
    heroLine2: 'MSB uchun',
    heroSub: 'Anketani toʻldiring, moliya maʻlumotlaringizni yuklang va shaxsiy reja oling: sizga qaysi biznes mos va qaysi NBU krediti «Kreditlar 2026» katalogidan toʻgʻri keladi',
    cta: 'Tahlilni boshlash',
    trust: 'Bank shifrlashi',
    stat1n: String(CREDIT_TOTAL), stat1l: 'haqiqiy NBU mahsuloti',
    stat2n: String(CITY_LIST.length), stat2l: 'pilot shahar',
    stat3n: '2010–2025', stat3l: 'farstat.uz maʻlumotlari',
    stat4n: '5', stat4l: 'daqiqa toʻldirish uchun',
    howBadge: 'BU QANDAY IShLAYDI',
    howHeading: 'Anketadan — biznes-rejaga',
    howSub: 'Oʻzingiz va gʻoyangiz haqida ayting. Platforma maʻlumotlaringizni shahar statistikasi va NBU katalogi bilan birlashtirib, eng mos yoʻnalishni tavsiya qiladi.',
    stepLabel: 'QADAM',
    steps: [
      { title: 'Profil', desc: 'YuL yoki YaTT, tajriba, taʻlim, jamoa' },
      { title: 'Moliya', desc: 'Biznesingizning moliyaviy maʻlumotlarini yuklang' },
      { title: 'Tahlil', desc: 'AI maʻlumotlaringizni × shahar statistikasi × NBU katalogini tahlil qiladi' },
      { title: 'Natijalar, reja', desc: 'Tavsiya + eng mos NBU krediti' },
    ],
    ctaTitle: 'Boshlashga tayyormisiz?',
    ctaSub: '5 daqiqada biznes imkoniyatlarining shaxsiy AI-tahlilini oling',
    ctaTrust: 'Maʻlumotlar bank serverlarida shifrlanadi',
    footer: '© 2026 NBU — Oʻzbekiston Milliy banki',
    privacy: 'Maxfiylik',
    footerDesc: 'AI Biznes-maslahatchi',
    cardScore: 'AI Baho', cardSwot: 'SWOT-tahlil', cardCredit: 'NBU Kredit', cardMonths: 'oy',
  },
}
const t = computed(() => T[lang.value])
const stats = computed(() => [
  { n: t.value.stat1n, l: t.value.stat1l },
  { n: t.value.stat2n, l: t.value.stat2l },
  { n: t.value.stat3n, l: t.value.stat3l },
  { n: t.value.stat4n, l: t.value.stat4l },
])
const STEP_ICONS = ['user', 'landmark', 'brain', 'file-check']  // profile, finance, analysis, results

const goTest = () => router.push('/tools/regional-strategist/test')
</script>

<template>
  <div class="min-h-screen bg-white">
    <RsHeader active-nav="home" />

    <!-- HERO -->
    <section
      class="relative overflow-hidden"
      style="background: linear-gradient(145deg, #091B35 0%, #12305C 40%, #193F72 70%, #1E4F82 100%);"
    >
      <div
        class="absolute inset-0 opacity-[0.025]"
        style="background-image: repeating-linear-gradient(0deg,transparent,transparent 60px,rgba(255,255,255,.5) 60px,rgba(255,255,255,.5) 61px),repeating-linear-gradient(90deg,transparent,transparent 60px,rgba(255,255,255,.5) 60px,rgba(255,255,255,.5) 61px);"
      />
      <div
        class="absolute -top-[200px] -right-[200px] w-[800px] h-[800px] pointer-events-none"
        style="background: radial-gradient(circle, rgba(215,181,109,0.07) 0%, transparent 55%);"
      />

      <div class="relative max-w-[1200px] mx-auto px-6 md:px-10 pt-16 md:pt-24 pb-24 md:pb-32">
        <div class="flex flex-col xl:flex-row items-start xl:items-center gap-10 xl:gap-20">
          <div class="flex-1 max-w-[580px]">
            <div class="inline-flex items-center gap-2 bg-white/[0.06] border border-white/[0.1] rounded-full py-[6px] px-4">
              <img src="/logos/nbu-mark.png" alt="NBU" class="h-5 w-auto opacity-80" />
              <span class="text-[11px] font-bold uppercase tracking-[1.5px] text-white/70">
                {{ t.badge }}
              </span>
            </div>

            <h1 class="mt-8">
              <span class="block font-serif font-normal text-white leading-[1.1] tracking-[-0.5px]" style="font-size:clamp(2rem,4vw,3rem)">
                {{ t.heroTitle }}
              </span>
              <span class="block font-serif font-normal text-gold-500 leading-[1.1] tracking-[-0.5px]" style="font-size:clamp(2rem,4vw,3rem)">
                {{ t.heroLine2 }}
              </span>
            </h1>

            <p class="text-[16px] md:text-[17px] text-white/55 leading-[1.7] mt-6 max-w-[480px]">
              {{ t.heroSub }}
            </p>

            <div class="flex items-center gap-5 mt-10">
              <button
                @click="goTest"
                class="group inline-flex items-center gap-2 text-[15px] font-bold text-navy-900 bg-gold-500 hover:bg-gold-400 rounded-btn py-[16px] px-8 shadow-rs-gold transition-all duration-200"
              >
                {{ t.cta }}
                <RsIcon name="arrow-right" :size="18" :stroke-width="2.5"
                        class="transition-transform duration-200 group-hover:translate-x-[3px]" />
              </button>
              <div class="flex items-center gap-[6px]">
                <RsIcon name="shield" :size="14" class="text-white/25" />
                <span class="text-[13px] font-medium text-white/25">{{ t.trust }}</span>
              </div>
            </div>
          </div>

          <!-- floating preview cards -->
          <div class="relative w-[380px] h-[420px] shrink-0 hidden xl:block">
            <div class="absolute top-0 right-0 w-[210px] animate-rs-float-1 bg-white/[0.07] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-5 shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
              <div class="text-[10px] font-bold uppercase tracking-[1.5px] text-gold-500">{{ t.cardScore }}</div>
              <div class="flex items-baseline gap-1 mt-3">
                <span class="font-mono text-[44px] font-bold text-white leading-none">74</span>
                <span class="font-mono text-[16px] text-white/35">/100</span>
              </div>
              <div class="h-[4px] bg-white/[0.08] rounded-full mt-4 overflow-hidden">
                <div class="h-full w-[74%] rounded-full" style="background: linear-gradient(90deg, #193F72, #D7B56D);" />
              </div>
            </div>

            <div class="absolute top-[170px] -left-6 w-[230px] animate-rs-float-2 bg-white/[0.07] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-5 shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
              <div class="text-[10px] font-bold uppercase tracking-[1.5px] text-white/45">{{ t.cardSwot }}</div>
              <div class="grid grid-cols-2 gap-[6px] mt-3">
                <div class="bg-emerald-500/15 rounded-lg py-[6px] px-2 text-[10px] font-bold text-emerald-400 text-center">S</div>
                <div class="bg-red-500/15 rounded-lg py-[6px] px-2 text-[10px] font-bold text-red-400 text-center">W</div>
                <div class="bg-blue-500/15 rounded-lg py-[6px] px-2 text-[10px] font-bold text-blue-400 text-center">O</div>
                <div class="bg-amber-500/15 rounded-lg py-[6px] px-2 text-[10px] font-bold text-amber-400 text-center">T</div>
              </div>
            </div>

            <div class="absolute bottom-[10px] right-[20px] w-[200px] animate-rs-float-3 bg-white/[0.07] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-5 shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
              <div class="text-[10px] font-bold uppercase tracking-[1.5px] text-gold-500">{{ t.cardCredit }}</div>
              <div class="font-mono text-[28px] font-bold text-white leading-none mt-2">23%</div>
              <span class="text-[12px] text-white/35">48 {{ t.cardMonths }} · 3,5 mlrd UZS</span>
            </div>
          </div>
        </div>
      </div>

      <div class="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 48" fill="none" class="w-full h-auto block">
          <path d="M0 48h1440V24C1320 6 1140 0 960 0S600 12 480 24 120 42 0 36v12z" fill="white" />
        </svg>
      </div>
    </section>

    <!-- STATS -->
    <section class="bg-white pt-6 pb-12">
      <div class="max-w-[820px] mx-auto flex flex-wrap justify-between gap-6 px-6 md:px-10">
        <div v-for="s in stats" :key="s.l" class="text-center min-w-[120px]">
          <div class="font-mono text-[32px] font-bold text-navy-900 leading-none">{{ s.n }}</div>
          <div class="text-[13px] text-steel-500 mt-1">{{ s.l }}</div>
        </div>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section class="bg-[#F8F9FB] py-20 px-6 md:px-10">
      <div class="max-w-[960px] mx-auto">
        <div class="text-center mb-14">
          <span class="inline-flex text-[11px] font-bold uppercase tracking-[2px] text-gold-500">{{ t.howBadge }}</span>
          <h2 class="font-serif text-[30px] md:text-[36px] font-normal text-carbon mt-3 leading-[1.2]">{{ t.howHeading }}</h2>
          <p class="text-[15px] text-[#898989] mt-2 max-w-[460px] mx-auto leading-[1.6]">{{ t.howSub }}</p>
        </div>

        <div class="relative">
          <div
            class="hidden md:block absolute top-[28px] left-[12%] right-[12%] h-[2px]"
            style="background: linear-gradient(90deg, #D9DADA, #D7B56D 40%, #D7B56D 60%, #D9DADA);"
          />

          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div v-for="(step, i) in t.steps" :key="i" class="flex flex-col items-center text-center">
              <div class="relative z-10 w-14 h-14 rounded-full bg-white border-2 border-gold-500 flex items-center justify-center shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
                <RsIcon :name="STEP_ICONS[i]" :size="22" class="text-navy-900" />
              </div>
              <span class="font-mono text-[10px] font-bold uppercase tracking-[1.5px] text-gold-500 mt-4">
                {{ t.stepLabel }} {{ String(i + 1).padStart(2, '0') }}
              </span>
              <h3 class="text-[15px] font-semibold text-carbon mt-2">{{ step.title }}</h3>
              <p class="text-[13px] text-[#898989] mt-1 leading-[1.5] max-w-[180px]">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-white py-20 px-6 md:px-10">
      <div class="max-w-[700px] mx-auto text-center">
        <div class="relative bg-white border border-rs-border rounded-[20px] py-14 px-6 md:px-10 shadow-[0_4px_20px_rgba(25,63,114,0.04)] overflow-hidden">
          <div class="absolute top-0 left-0 right-0 h-[3px]"
               style="background: linear-gradient(90deg, #193F72, #D7B56D, #193F72);" />
          <h2 class="font-serif text-[28px] md:text-[32px] font-normal text-carbon">{{ t.ctaTitle }}</h2>
          <p class="text-[15px] text-[#898989] mt-2 max-w-[440px] mx-auto leading-[1.6]">{{ t.ctaSub }}</p>
          <div class="mt-8">
            <button
              @click="goTest"
              class="group inline-flex items-center gap-2 text-[15px] font-bold text-white bg-navy-900 hover:bg-navy-700 rounded-btn py-[16px] px-10 transition-colors duration-200"
            >
              {{ t.cta }}
              <RsIcon name="arrow-right" :size="18" :stroke-width="2.5"
                      class="transition-transform duration-200 group-hover:translate-x-[3px]" />
            </button>
          </div>
          <div class="flex items-center justify-center gap-[6px] mt-4">
            <RsIcon name="shield" :size="13" class="text-steel-500/50" />
            <span class="text-[12px] text-steel-500/50">{{ t.ctaTrust }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="bg-[#0F2847] py-10 px-6 md:px-10">
      <div class="max-w-[1200px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <img src="/logos/nbu-mark.png" alt="NBU" class="h-6 w-auto opacity-60" />
          <div>
            <span class="text-[13px] font-semibold text-white/70">NBU</span>
            <span class="text-[13px] text-white/30 ml-2">{{ t.footerDesc }}</span>
          </div>
        </div>
        <div class="flex items-center gap-6">
          <a href="#privacy" class="text-[13px] text-white/30 hover:text-white/60 transition-colors duration-200">{{ t.privacy }}</a>
          <span class="text-[13px] text-white/20">{{ t.footer }}</span>
        </div>
      </div>
    </footer>
  </div>
</template>
