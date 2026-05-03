<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { useEduAuthStore } from '@/stores/eduAuth'

// Auth store auto-fetches /me on init when a token is present, so by the
// time the sidebar mounts the role is already known. No explicit call
// needed here — just read user.role reactively.
const auth = useEduAuthStore()
const isAdmin = computed(() => auth.user?.role === 'admin')

const baseNavItems = [
  { to: '/', icon: 'dashboard', labelKey: 'nav.home' },
  { to: '/districts', icon: 'analytics', labelKey: 'nav.districts' },
  { to: '/ai', icon: 'psychology', labelKey: 'nav.ai', disabled: true },
  { to: '/tools', icon: 'precision_manufacturing', labelKey: 'nav.tools' },
  { to: '/education', icon: 'school', labelKey: 'nav.education' },
]

const adminNavItem = {
  to: '/admin/golden-mart',
  icon: 'admin_panel_settings',
  labelKey: 'nav.admin',
  adminOnly: true,
}

const navItems = computed(() =>
  isAdmin.value ? [...baseNavItems, adminNavItem] : baseNavItems,
)
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
      <template v-for="item in navItems" :key="item.to">
        <!-- Disabled nav item: rendered as a non-interactive div -->
        <div
          v-if="item.disabled"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 cursor-not-allowed select-none"
          aria-disabled="true"
        >
          <AppIcon :name="item.icon" />
          <span class="text-sm font-semibold">{{ $t(item.labelKey) }}</span>
          <span class="ml-auto text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-200 px-1.5 py-0.5 rounded">
            {{ $t('nav.soon') }}
          </span>
        </div>
        <RouterLink
          v-else
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
          <span
            v-if="item.adminOnly"
            class="ml-auto text-[10px] font-black tracking-widest bg-amber-500 text-white px-1.5 py-0.5 rounded"
          >
            {{ $t('nav.adminBadge') }}
          </span>
        </RouterLink>
      </template>
    </nav>

  </aside>
</template>
