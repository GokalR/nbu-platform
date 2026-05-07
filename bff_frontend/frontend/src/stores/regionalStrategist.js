import { defineStore } from 'pinia'
import { DEMO_SEEDS } from '@/data/regionalStrategist/demo-seeds'

const emptyProfile = () => ({
  name: '',
  ageRange: '',
  gender: '',
  hasHigherEducation: '',
  educationField: '',
  maritalStatus: '',
  dependents: '',
  currentStatus: '',
  experienceLevel: '',
  domainExperience: '',
  hasTraining: '',
  hasMentor: '',
  hudud: '',
  mahalla: '',
  viloyat: '',
  urbanRural: '',
  businessAge: '',
  employeeCount: '',
  entityType: '',
  registrationForm: '',
  businessSize: '',
})

const emptyFinance = () => ({
  businessDirection: '',
  hasBusinessPlan: '',
  needsLoan: '',
  hasOwnFunds: '',
  hasCollateral: '',
  collateralType: '',
  ideaDescription: '',
  whyThisBusiness: '',
  targetCustomer: '',
  hasSpace: '',
  hasEquipment: '',
  timeline: '',
  hasRegisteredBusiness: '',
  businessGoal: '',
  mainProblem: '',
  monthlyIncome: '',
  monthlyExpenses: '',
  existingDebt: '',
  loanAmount: '',
})

export const useRegionalStrategistStore = defineStore('regionalStrategist', {
  state: () => ({
    path: null, // 'new' | 'existing' | null
    step: 0, // 0..5
    profile: emptyProfile(),
    finance: emptyFinance(),
    // Backend-linked state. All null when backend is not configured (demo mode).
    submissionId: null,
    uploads: [],           // [{ id, kind, original_filename, size_bytes, parsed }]
    analysis: null,        // latest Claude response { output, model, input_tokens, ... }
    analysisStatus: 'idle', // 'idle' | 'submitting' | 'uploading' | 'analyzing' | 'ready' | 'error'
    analysisError: null,
  }),
  actions: {
    goTo(step) {
      this.step = step
      if (typeof window !== 'undefined') {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    choosePath(path) {
      this.path = path
      if (path === 'existing') {
        this.profile.currentStatus = 'Предприниматель'
      }
      this.goTo(1)
    },
    reset() {
      this.path = null
      this.profile = emptyProfile()
      this.finance = emptyFinance()
      this.submissionId = null
      this.uploads = []
      this.analysis = null
      this.analysisStatus = 'idle'
      this.analysisError = null
      this.goTo(0)
    },
    updateProfile(patch) {
      Object.assign(this.profile, patch)
    },
    updateFinance(patch) {
      Object.assign(this.finance, patch)
    },
    setSubmission(id) {
      this.submissionId = id
    },
    setAnalysis(analysis) {
      this.analysis = analysis
      this.analysisStatus = 'ready'
      this.analysisError = null
    },
    setAnalysisStatus(status, error = null) {
      this.analysisStatus = status
      this.analysisError = error
    },
    addUpload(upload) {
      this.uploads = [...this.uploads.filter((u) => u.kind !== upload.kind), upload]
    },
    seedDemo(key, lang = 'ru') {
      const seed = DEMO_SEEDS[key]
      if (!seed) return
      const variant = seed[lang] || seed.ru
      this.path = 'existing'
      this.profile = { ...emptyProfile(), ...variant.profile }
      this.finance = { ...emptyFinance(), ...variant.finance }
    },
  },
})
