import { useState } from 'react'
import { LayoutGrid } from 'lucide-react'
import { Lang } from '../types'
import { t } from '../i18n'
import Card from '../components/Card'
import Button from '../components/Button'

interface Props {
  lang: Lang
  initialValue: number
  onNext: (count: number) => void
  onBack: () => void
}

export default function StepSpheres({ lang, initialValue, onNext, onBack }: Props) {
  const [value, setValue] = useState(initialValue)
  const [error, setError] = useState('')

  const handleNext = () => {
    if (value < 1 || value > 10 || !Number.isInteger(value)) {
      setError(t(lang, 'error_range'))
      return
    }
    onNext(value)
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-3">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-2xl">
          <LayoutGrid size={32} className="text-accent" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-primary">{t(lang, 'spheres_title')}</h2>
          <p className="text-sm text-muted mt-1">{t(lang, 'spheres_hint')}</p>
        </div>
      </div>

      <Card>
        <div className="space-y-4">
          <label className="block text-sm font-semibold text-gray-700">
            {t(lang, 'spheres_label')}
          </label>
          <input
            type="number"
            min={1}
            max={10}
            value={value}
            onChange={(e) => { setValue(parseInt(e.target.value) || 1); setError('') }}
            onKeyDown={(e) => e.key === 'Enter' && handleNext()}
            className={`w-full px-4 py-3.5 border rounded-input text-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-colors ${
              error ? 'border-error bg-red-50' : 'border-border'
            }`}
          />
          {error && <p className="text-xs text-error font-medium">{error}</p>}

          {/* Quick select bubbles */}
          <div className="flex flex-wrap gap-2 pt-1">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                onClick={() => { setValue(n); setError('') }}
                className={`w-10 h-10 rounded-full text-sm font-semibold border-2 transition-all ${
                  value === n
                    ? 'bg-primary text-white border-primary'
                    : 'bg-white text-gray-600 border-border hover:border-accent hover:text-accent'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
      </Card>

      <div className="flex gap-3">
        <Button variant="secondary" onClick={onBack} className="flex-1">
          {t(lang, 'back')}
        </Button>
        <Button variant="primary" onClick={handleNext} className="flex-1">
          {t(lang, 'next')}
        </Button>
      </div>
    </div>
  )
}
