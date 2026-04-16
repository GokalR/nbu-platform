<script setup>
import { RouterLink } from 'vue-router'
import AppIcon from './AppIcon.vue'

const navItems = [
  { to: '/', icon: 'dashboard', labelKey: 'nav.home' },
  { to: '/districts', icon: 'analytics', labelKey: 'nav.districts' },
  { to: '/ai', icon: 'psychology', labelKey: 'nav.ai' },
  { to: '/tools', icon: 'precision_manufacturing', labelKey: 'nav.tools' },
  { to: '/education', icon: 'school', labelKey: 'nav.education' },
]
</script>

<template>
  <aside
    class="hidden md:flex h-screen w-64 fixed left-0 top-0 flex-col p-4 gap-2 bg-slate-50/70 backdrop-blur-2xl z-[60] border-r border-outline-variant/20"
  >
    <RouterLink to="/" class="mb-8 px-2 flex items-center gap-3">
      <img src="/nbu_logo.png" alt="NBU" class="h-11 w-auto" />
      <div>
        <div class="text-lg font-black text-blue-900 leading-tight">{{ $t('app.brand') }}</div>
        <div class="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
          {{ $t('app.brandSub') }}
        </div>
      </div>
    </RouterLink>

    <nav class="flex-1 flex flex-col gap-1" :aria-label="$t('app.brand')">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group"
        active-class="bg-white text-blue-900 shadow-sm font-bold"
        :class="
          $route.path === item.to
            ? ''
            : 'text-slate-600 hover:bg-slate-100 hover:translate-x-1'
        "
      >
        <AppIcon :name="item.icon" />
        <span class="text-sm font-semibold">{{ $t(item.labelKey) }}</span>
      </RouterLink>
    </nav>

    <div class="mt-auto border-t border-outline-variant/20 pt-4 flex flex-col gap-1">
      <a
        href="#"
        class="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-100 transition-colors rounded-lg"
      >
        <AppIcon name="contact_support" />
        <span class="text-sm font-semibold">{{ $t('nav.support') }}</span>
      </a>
    </div>
  </aside>
</template>
