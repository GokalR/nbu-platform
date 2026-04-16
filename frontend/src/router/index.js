import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { titleKey: 'nav.home' },
  },
  {
    path: '/districts',
    name: 'districts',
    component: () => import('@/views/DistrictAnalyticsView.vue'),
    meta: { titleKey: 'nav.districts' },
  },
  {
    path: '/ai',
    name: 'ai',
    component: () => import('@/views/AiAdvisorView.vue'),
    meta: { titleKey: 'nav.ai' },
  },
  {
    path: '/tools',
    name: 'tools',
    component: () => import('@/views/BusinessToolsView.vue'),
    meta: { titleKey: 'nav.tools' },
  },
  {
    path: '/education',
    name: 'education',
    component: () => import('@/views/education/EduCoursesView.vue'),
    meta: { layout: 'education', titleKey: 'nav.education' },
  },
  {
    path: '/education/courses/:id',
    name: 'edu-course-detail',
    component: () => import('@/views/education/EduCourseDetailView.vue'),
    meta: { layout: 'education', titleKey: 'nav.education' },
  },
  {
    path: '/education/courses/:courseId/learn/:videoId',
    name: 'edu-learn',
    component: () => import('@/views/education/EduLearningView.vue'),
    meta: { layout: 'education', titleKey: 'nav.education' },
  },
  {
    path: '/tools/fincontrol',
    name: 'fincontrol-onboarding',
    component: () => import('@/views/fincontrol/FinControlOnboardingView.vue'),
    meta: { layout: 'blank' },
  },
  {
    path: '/tools/fincontrol/dashboard',
    name: 'fincontrol-dashboard',
    component: () => import('@/views/fincontrol/FinControlDashboardView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/accounts',
    name: 'fincontrol-accounts',
    component: () => import('@/views/fincontrol/FinControlAccountsView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/cashflow',
    name: 'fincontrol-cashflow',
    component: () => import('@/views/fincontrol/FinControlCashflowView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/income-expense',
    name: 'fincontrol-income-expense',
    component: () => import('@/views/fincontrol/FinControlIncomeExpenseView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/pnl',
    name: 'fincontrol-pnl',
    component: () => import('@/views/fincontrol/FinControlPnlView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/counterparties',
    name: 'fincontrol-counterparties',
    component: () => import('@/views/fincontrol/FinControlCounterpartiesView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/planning',
    name: 'fincontrol-planning',
    component: () => import('@/views/fincontrol/FinControlPlanningView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/import',
    name: 'fincontrol-import',
    component: () => import('@/views/fincontrol/FinControlImportView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/fincontrol/ai',
    name: 'fincontrol-ai',
    component: () => import('@/views/fincontrol/FinControlAiView.vue'),
    meta: { layout: 'fincontrol' },
  },
  {
    path: '/tools/regional-strategist',
    name: 'regional-strategist',
    component: () => import('@/views/regionalStrategist/RsHomeView.vue'),
    meta: { layout: 'regionalStrategist', titleKey: 'nav.regionalStrategist' },
  },
  {
    path: '/tools/regional-strategist/test',
    name: 'regional-strategist-test',
    component: () => import('@/views/regionalStrategist/RsBusinessTestView.vue'),
    meta: { layout: 'regionalStrategist', titleKey: 'nav.regionalStrategist' },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
