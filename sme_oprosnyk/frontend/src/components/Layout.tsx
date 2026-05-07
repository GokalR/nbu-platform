import { ReactNode } from 'react'
import { Lang } from '../types'
import { t } from '../i18n'

interface Props {
  children: ReactNode
  lang: Lang
  onLangChange: (l: Lang) => void
  currentStep: number
  totalSteps: number
  stepLabel: string
}

export default function Layout({ children, lang, onLangChange, currentStep, totalSteps, stepLabel }: Props) {
  const progress = Math.round((currentStep / totalSteps) * 100)

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Top header */}
      <header className="bg-white border-b border-border sticky top-0 z-10 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-primary leading-tight">{t(lang, 'appName')}</h1>
            <p className="text-xs text-muted mt-0.5">{t(lang, 'appSubtitle')}</p>
          </div>

          {/* Language switcher */}
          <div className="flex items-center gap-1 bg-gray-100 rounded-btn p-1">
            {(['ru', 'uz'] as Lang[]).map((l) => (
              <button
                key={l}
                onClick={() => onLangChange(l)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-[12px] transition-all duration-200 ${
                  lang === l
                    ? 'bg-white text-accent shadow-sm'
                    : 'text-muted hover:text-accent'
                }`}
              >
                {l === 'ru' ? 'РУС' : 'UZB'}
              </button>
            ))}
          </div>
        </div>

        {/* Progress bar */}
        <div className="max-w-3xl mx-auto px-4 pb-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-medium text-muted">{stepLabel}</span>
            <span className="text-xs font-semibold text-accent">
              {currentStep} / {totalSteps}
            </span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </header>

      {/* Page content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="max-w-3xl mx-auto px-4 py-6 text-center">
        <p className="text-xs text-muted">© 2025 · Бизнес-анкетирование · НБУ</p>
      </footer>
    </div>
  )
}
