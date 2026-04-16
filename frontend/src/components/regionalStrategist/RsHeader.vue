<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRsLang } from '@/composables/useRsLang'

const props = defineProps({
  activeNav: { type: String, default: 'home' },
})

const { locale } = useI18n()
const { lang } = useRsLang()

const T = {
  ru: { home: 'Главная', businessTest: 'Бизнес-тест', about: 'О платформе', logoAlt: 'NBU — Национальный банк Узбекистана', backToHub: 'В NBU AI Hub' },
  uz: { home: 'Бош саҳифа', businessTest: 'Бизнес-тест', about: 'Платформа ҳақида', logoAlt: 'NBU — Ўзбекистон Миллий банки', backToHub: 'NBU AI Hub-га' },
}
const t = computed(() => T[lang.value])

const scrolled = ref(false)
const onScroll = () => { scrolled.value = window.scrollY > 10 }
onMounted(() => { onScroll(); window.addEventListener('scroll', onScroll) })
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const setLang = (v) => { locale.value = v; try { localStorage.setItem('nbu.locale', v) } catch (e) {} }

const nav = computed(() => ([
  { key: 'home', href: '/tools/regional-strategist' },
  { key: 'businessTest', href: '/tools/regional-strategist/test' },
  { key: 'about', href: '#about' },
]))
</script>

<template>
  <header
    class="sticky top-0 z-50 bg-white border-b border-rs-border h-16 transition-shadow duration-200"
    :class="{ 'shadow-[0_1px_3px_rgba(0,0,0,0.06)]': scrolled }"
  >
    <div class="max-w-[1440px] mx-auto h-full px-6 md:px-10 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <router-link to="/" class="inline-flex items-center gap-2 text-steel-500 hover:text-navy-900 text-[12px] font-semibold">
          ← {{ t.backToHub }}
        </router-link>
        <div class="w-px h-6 bg-rs-border hidden md:block" />
        <router-link to="/tools/regional-strategist" class="flex items-center gap-3">
          <img src="/logos/nbu-mark.png" :alt="t.logoAlt" class="h-8 w-auto" />
        </router-link>
      </div>

      <nav class="hidden md:flex items-center gap-8 h-full">
        <template v-for="(item, i) in nav" :key="item.key">
          <router-link
            v-if="item.href.startsWith('/')"
            :to="item.href"
            class="relative h-full inline-flex items-center text-[14px] transition-colors duration-200"
            :class="activeNav === item.key ? 'text-navy-900 font-semibold' : 'text-steel-500 font-medium hover:text-navy-900'"
          >
            {{ t[item.key] }}
            <span v-if="activeNav === item.key" class="absolute left-0 right-0 bottom-0 h-[2.5px] bg-gold-500" />
          </router-link>
          <a
            v-else
            :href="item.href"
            class="relative h-full inline-flex items-center text-[14px] transition-colors duration-200"
            :class="activeNav === item.key ? 'text-navy-900 font-semibold' : 'text-steel-500 font-medium hover:text-navy-900'"
          >
            {{ t[item.key] }}
            <span v-if="activeNav === item.key" class="absolute left-0 right-0 bottom-0 h-[2.5px] bg-gold-500" />
          </a>
        </template>
      </nav>

      <div class="flex items-center gap-3">
        <div class="inline-flex items-center bg-[#F1F2F7] rounded-full p-[2px]">
          <button
            v-for="l in ['RU', 'UZ']"
            :key="l"
            @click="setLang(l.toLowerCase())"
            class="text-[12px] font-semibold py-[5px] px-3 rounded-full transition-colors duration-200"
            :class="lang === l.toLowerCase() ? 'bg-navy-900 text-white' : 'bg-transparent text-steel-500 hover:text-navy-900'"
          >
            {{ l }}
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
