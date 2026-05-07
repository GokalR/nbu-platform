import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import KpiCard from '../KpiCard.vue'

const i18n = createI18n({
  legacy: false,
  locale: 'uz',
  messages: { uz: {}, ru: {} },
  missing: (_, key) => key,
})

function mountKpiCard(props = {}) {
  return mount(KpiCard, {
    props: {
      icon: 'analytics',
      value: '1,234',
      label: 'Total Users',
      ...props,
    },
    global: {
      plugins: [i18n],
    },
  })
}

describe('KpiCard', () => {
  it('renders with required props', () => {
    const wrapper = mountKpiCard()
    expect(wrapper.find('article').exists()).toBe(true)
  })

  it('displays the value', () => {
    const wrapper = mountKpiCard({ value: '5,678' })
    expect(wrapper.text()).toContain('5,678')
  })

  it('displays the label', () => {
    const wrapper = mountKpiCard({ label: 'Active Sessions' })
    expect(wrapper.text()).toContain('Active Sessions')
  })

  it('displays the icon name in the icon span', () => {
    const wrapper = mountKpiCard({ icon: 'trending_up' })
    expect(wrapper.find('.material-symbols-outlined').text()).toBe('trending_up')
  })

  it('shows delta when provided', () => {
    const wrapper = mountKpiCard({ delta: '+12%' })
    expect(wrapper.text()).toContain('+12%')
  })

  it('does not render delta span when delta is empty', () => {
    const wrapper = mountKpiCard({ delta: '' })
    // The v-if="delta" should prevent the delta span from rendering
    const spans = wrapper.findAll('span')
    const deltaSpans = spans.filter((s) => s.classes().some((c) => c.startsWith('text-')))
    // The only span with a text- class should be the icon, not a delta
    for (const s of deltaSpans) {
      // icon span has material-symbols-outlined class
      if (!s.classes().includes('material-symbols-outlined')) {
        // This would be a delta span, which shouldn't exist
        expect(true).toBe(false)
      }
    }
  })

  it('applies correct tone class for negative tone', () => {
    const wrapper = mountKpiCard({ delta: '-5%', tone: 'negative' })
    const deltaSpan = wrapper.findAll('span').find(
      (s) => s.text() === '-5%',
    )
    expect(deltaSpan).toBeDefined()
    expect(deltaSpan.classes()).toContain('text-error')
  })
})
