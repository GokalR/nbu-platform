import { useState, useEffect } from 'react'
import { Lang, Category, SphereData, ClientInfo } from './types'
import { fetchQuestions, submitAnswers } from './api'
import { t } from './i18n'
import Layout from './components/Layout'
import StepPinfl from './steps/StepPinfl'
import StepCategory from './steps/StepCategory'
import StepQuestions from './steps/StepQuestions'
import StepSummary from './steps/StepSummary'
import StepSuccess from './steps/StepSuccess'

type AppStep = 'pinfl' | 'category' | 'questions' | 'summary' | 'success'

export default function App() {
  const [lang, setLang]                         = useState<Lang>('ru')
  const [step, setStep]                         = useState<AppStep>('pinfl')
  const [pinflInn, setPinflInn]                 = useState('')
  const [clientInfo, setClientInfo]             = useState<ClientInfo | null>(null)
  const [sphereCount, setSphereCount]           = useState(1)
  const [currentSphereIdx, setCurrentSphereIdx] = useState(0)
  const [spheres, setSpheres]                   = useState<SphereData[]>([])
  const [categories, setCategories]             = useState<Category[]>([])
  const [loading, setLoading]                   = useState(true)
  const [fetchError, setFetchError]             = useState<string | null>(null)
  const [submitting, setSubmitting]             = useState(false)
  const [submitError, setSubmitError]           = useState<string | null>(null)

  useEffect(() => {
    fetchQuestions()
      .then(d => { setCategories(d.categories); setLoading(false) })
      .catch(() => { setFetchError(t(lang, 'error_backend')); setLoading(false) })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ── Handlers ─────────────────────────────────────────────────────────────

  const handlePinflNext = (val: string, info: ClientInfo | null, count: number) => {
    setPinflInn(val)
    setClientInfo(info)
    setSphereCount(count)
    setSpheres([])
    setCurrentSphereIdx(0)
    setStep('category')
  }

  const handleCategoryNext = (id: string, nameRu: string, nameUz: string) => {
    const updated = [...spheres]
    updated[currentSphereIdx] = {
      sphere_number: currentSphereIdx + 1,
      category_id: id,
      category_name_ru: nameRu,
      category_name_uz: nameUz,
      answers: updated[currentSphereIdx]?.answers ?? [],
    }
    setSpheres(updated); setStep('questions')
  }

  const handleQuestionsNext = (answers: SphereData['answers']) => {
    const updated = [...spheres]
    updated[currentSphereIdx] = { ...updated[currentSphereIdx], answers }
    setSpheres(updated)
    if (currentSphereIdx < sphereCount - 1) {
      setCurrentSphereIdx(i => i + 1); setStep('category')
    } else {
      setStep('summary')
    }
  }

  const handleBack = () => {
    if (step === 'category') {
      if (currentSphereIdx === 0) { setStep('pinfl'); return }
      setCurrentSphereIdx(i => i - 1); setStep('questions'); return
    }
    if (step === 'questions') { setStep('category'); return }
    if (step === 'summary') { setCurrentSphereIdx(sphereCount - 1); setStep('questions') }
  }

  const handleSubmit = async () => {
    setSubmitting(true); setSubmitError(null)
    try {
      await submitAnswers({
        pinfl_or_inn: pinflInn,
        sphere_count: sphereCount,
        spheres,
        client_info: clientInfo ?? undefined,
      })
      setStep('success')
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : t(lang, 'error_backend'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleRestart = () => {
    setPinflInn(''); setClientInfo(null)
    setSphereCount(1); setCurrentSphereIdx(0); setSpheres([]); setStep('pinfl')
  }

  // ── Progress ──────────────────────────────────────────────────────────────

  const totalSteps = 1 + sphereCount * 2 + 1   // pinfl + N*(cat+q) + summary

  const currentStepNum = (() => {
    if (step === 'pinfl')     return 1
    if (step === 'category')  return 2 + currentSphereIdx * 2
    if (step === 'questions') return 3 + currentSphereIdx * 2
    return totalSteps
  })()

  const stepLabel = (() => {
    if (step === 'pinfl')     return t(lang, 'step_pinfl')
    if (step === 'category')  return `${t(lang, 'step_category')} ${currentSphereIdx + 1}/${sphereCount}`
    if (step === 'questions') return `${t(lang, 'step_questions')} ${currentSphereIdx + 1}/${sphereCount}`
    if (step === 'summary')   return t(lang, 'step_summary')
    return t(lang, 'step_success')
  })()

  const currentCategory = spheres[currentSphereIdx]
    ? categories.find(c => c.id === spheres[currentSphereIdx].category_id) ?? null
    : null

  return (
    <Layout lang={lang} onLangChange={setLang}
      currentStep={step === 'success' ? totalSteps : currentStepNum}
      totalSteps={totalSteps} stepLabel={stepLabel}>

      {loading && (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted">{t(lang, 'loading')}</p>
        </div>
      )}
      {!loading && fetchError && (
        <div className="bg-red-50 border border-red-200 rounded-card p-8 text-center">
          <p className="text-base font-semibold text-error">{fetchError}</p>
          <p className="text-sm text-muted mt-1">http://localhost:8001</p>
        </div>
      )}
      {!loading && !fetchError && (
        <>
          {step === 'pinfl' && (
            <StepPinfl lang={lang} initialValue={pinflInn} initialClientInfo={clientInfo}
              initialSphereCount={sphereCount} onNext={handlePinflNext} />
          )}
          {step === 'category' && (
            <StepCategory lang={lang} categories={categories}
              sphereIdx={currentSphereIdx} sphereCount={sphereCount}
              selectedId={spheres[currentSphereIdx]?.category_id ?? ''}
              onNext={handleCategoryNext} onBack={handleBack} />
          )}
          {step === 'questions' && currentCategory && (
            <StepQuestions lang={lang} category={currentCategory}
              sphereIdx={currentSphereIdx} sphereCount={sphereCount}
              initialAnswers={spheres[currentSphereIdx]?.answers ?? []}
              onNext={handleQuestionsNext} onBack={handleBack} />
          )}
          {step === 'summary' && (
            <StepSummary lang={lang} pinflInn={pinflInn} clientInfo={clientInfo}
              sphereCount={sphereCount} spheres={spheres}
              onBack={handleBack} onSubmit={handleSubmit}
              submitting={submitting} submitError={submitError} />
          )}
          {step === 'success' && (
            <StepSuccess lang={lang} pinflInn={pinflInn} clientInfo={clientInfo}
              sphereCount={sphereCount} spheres={spheres}
              onRestart={handleRestart} />
          )}
        </>
      )}
    </Layout>
  )
}
