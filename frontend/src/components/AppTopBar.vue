<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEduAuthStore } from '@/stores/eduAuth'
import AppIcon from './AppIcon.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'

const router = useRouter()
const auth = useEduAuthStore()
const showMenu = ref(false)

function logout() {
  auth.logout()
  showMenu.value = false
  router.push('/login')
}
</script>

<template>
  <header
    class="sticky top-0 z-50 flex justify-between items-center w-full px-8 py-4 bg-white/80 backdrop-blur-xl shadow-sm"
  >
    <div class="flex items-center gap-4">
      <h1 class="text-xl font-bold tracking-tight text-blue-900">
        {{ $t('app.title') }}
      </h1>
    </div>

    <div class="flex items-center gap-6">
      <LanguageSwitcher />

      <div class="flex items-center gap-3">
        <button
          type="button"
          class="p-2 text-slate-500 hover:text-blue-800 transition-colors active:scale-95 duration-200"
          aria-label="notifications"
        >
          <AppIcon name="notifications" />
        </button>
        <button
          type="button"
          class="p-2 text-slate-500 hover:text-blue-800 transition-colors active:scale-95 duration-200"
          aria-label="settings"
        >
          <AppIcon name="settings" />
        </button>
      </div>

      <!-- User menu -->
      <div class="relative">
        <button
          @click="showMenu = !showMenu"
          class="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-slate-100 transition"
        >
          <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
            {{ auth.user?.full_name?.charAt(0)?.toUpperCase() || '?' }}
          </div>
          <span class="hidden md:block text-sm font-medium text-slate-700 max-w-[120px] truncate">
            {{ auth.user?.full_name || auth.user?.email || '' }}
          </span>
        </button>

        <!-- Dropdown -->
        <div v-if="showMenu"
             class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-200 py-2 z-50">
          <div class="px-4 py-2 border-b border-slate-100">
            <div class="text-sm font-medium text-slate-800 truncate">{{ auth.user?.full_name }}</div>
            <div class="text-xs text-slate-500 truncate">{{ auth.user?.email }}</div>
          </div>
          <button @click="logout"
                  class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition">
            Logout
          </button>
        </div>

        <!-- Click-outside overlay -->
        <div v-if="showMenu" class="fixed inset-0 z-40" @click="showMenu = false" />
      </div>
    </div>
  </header>
</template>
