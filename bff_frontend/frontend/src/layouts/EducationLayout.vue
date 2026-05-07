<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { setLocale, supportedLocales } from '@/i18n'

const router = useRouter()
const { locale } = useI18n()

const labels = { uz: "O'z", ru: 'Ру' }
</script>

<template>
  <div class="edu-layout">
    <header class="edu-layout__header">
      <button class="edu-layout__back" @click="router.back()">
        <span class="material-symbols-outlined">arrow_back</span>
      </button>
      <div class="edu-layout__brand">
        <span class="edu-layout__logo">NBU</span>
        <span class="edu-layout__title">{{ $t('education.headerTitle') }}</span>
      </div>
      <div class="edu-layout__actions">
        <div class="edu-layout__lang" role="group" aria-label="Language switcher">
          <button
            v-for="code in supportedLocales"
            :key="code"
            type="button"
            class="edu-layout__lang-btn"
            :class="{ 'edu-layout__lang-btn--active': locale === code }"
            :aria-pressed="locale === code"
            @click="setLocale(code)"
          >
            {{ labels[code] }}
          </button>
        </div>
        <router-link to="/education" class="edu-layout__home">
          <span class="material-symbols-outlined">home</span>
        </router-link>
      </div>
    </header>
    <main class="edu-layout__content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.edu-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #f7f9fb);
}

.edu-layout__header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  background: var(--bg-card, #fff);
  border-bottom: 1px solid var(--edu-border, #dde3ee);
  height: 56px;
  box-shadow: 0 1px 3px rgba(0, 20, 60, 0.04);
}

.edu-layout__back,
.edu-layout__home {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--text-secondary, #424751);
  cursor: pointer;
  transition: all 0.15s;
}
.edu-layout__back:hover,
.edu-layout__home:hover {
  background: var(--edu-accent-light, #d6e3ff);
  color: var(--edu-accent, #003d7c);
}

.edu-layout__brand {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}
.edu-layout__logo {
  font-family: 'Manrope', sans-serif;
  font-weight: 800;
  font-size: 17px;
  color: var(--edu-accent, #003d7c);
  letter-spacing: -0.02em;
}
.edu-layout__title {
  font-family: 'Manrope', sans-serif;
  font-weight: 500;
  font-size: 15px;
  color: var(--text-secondary, #424751);
}

.edu-layout__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edu-layout__lang {
  display: inline-flex;
  align-items: center;
  background: var(--edu-bg, #f7f9fb);
  border-radius: 20px;
  padding: 2px;
}
.edu-layout__lang-btn {
  padding: 5px 12px;
  border-radius: 18px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 700;
  color: var(--edu-text-muted, #727783);
  cursor: pointer;
  transition: all 0.15s;
}
.edu-layout__lang-btn:hover {
  color: var(--edu-accent, #003d7c);
}
.edu-layout__lang-btn--active {
  background: var(--edu-accent, #003d7c);
  color: white;
  box-shadow: 0 1px 3px rgba(0, 20, 60, 0.15);
}

.edu-layout__content {
  flex: 1;
  overflow: auto;
}
</style>
