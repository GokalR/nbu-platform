import { useState } from 'react'
import { ClipboardList } from 'lucide-react'
import { Lang, Category, AnswerItem } from '../types'
import { t } from '../i18n'
import Card from '../components/Card'
import Button from '../components/Button'
import AddressCascade from '../components/AddressCascade'

interface Props {
  lang: Lang
  category: Category
  sphereIdx: number
  sphereCount: number
  initialAnswers: AnswerItem[]
  onNext: (answers: AnswerItem[]) => void
  onBack: () => void
}

export default function StepQuestions({
  lang, category, sphereIdx, sphereCount, initialAnswers, onNext, onBack
}: Props) {
  const initMap: Record<string, string> = {}
  initialAnswers.forEach(a => { initMap[a.question_id] = a.answer })

  const [answers, setAnswers] = useState<Record<string, string>>(initMap)

  const setAnswer = (id: string, val: string) => setAnswers(p => ({ ...p, [id]: val }))

  const toggleCheckbox = (id: string, opt: string) => {
    const current = (answers[id] ?? '').split(',').filter(Boolean)
    const next = current.includes(opt) ? current.filter(v => v !== opt) : [...current, opt]
    setAnswer(id, next.join(','))
  }

  const handleNext = () => {
    const baseAnswers: AnswerItem[] = category.questions.map(q => ({
      question_id: q.id,
      question_text_ru: q.text.ru,
      question_text_uz: q.text.uz,
      answer: answers[q.id] ?? '',
    }))

    // Append dynamic related company INN answers if count > 0
    const count = parseInt(answers['related_companies_count'] ?? '0', 10) || 0
    const dynamicAnswers: AnswerItem[] = []
    for (let i = 0; i < count; i++) {
      const key = `related_company_inn_${i}`
      const val = answers[key] ?? ''
      dynamicAnswers.push({
        question_id: key,
        question_text_ru: `Связанная компания ${i + 1} — ИНН`,
        question_text_uz: `Bog'liq kompaniya ${i + 1} — INN`,
        answer: val,
      })
    }

    onNext([...baseAnswers, ...dynamicAnswers])
  }

  const subtitle = t(lang, 'questions_sphere')
    .replace('{n}', String(sphereIdx + 1))
    .replace('{total}', String(sphereCount))
    .replace('{category}', category.name[lang])

  const isLast = sphereIdx === sphereCount - 1
  const ru = lang === 'ru'

  const inputCls = 'w-full px-4 py-3 border border-border rounded-input text-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-colors'
  const optionCls = 'flex items-center gap-3 cursor-pointer group p-2 rounded-lg hover:bg-blue-50 transition-colors'

  // How many related company INN fields to show
  const relatedCount = Math.max(0, Math.min(20, parseInt(answers['related_companies_count'] ?? '0', 10) || 0))

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-50 rounded-2xl">
          <ClipboardList size={28} className="text-accent" />
        </div>
        <h2 className="text-2xl font-bold text-primary">{t(lang, 'questions_title')}</h2>
        <p className="text-sm text-muted">{subtitle}</p>
      </div>

      <Card>
        <div className="space-y-7">
          {category.questions.map((q, idx) => {
            const text = q.text[lang]
            const opts = q.options[lang]
            const val  = answers[q.id] ?? ''

            return (
              <div key={q.id} className="space-y-2">
                <label className="block text-sm font-semibold text-gray-800">
                  <span className="text-accent mr-1.5">{idx + 1}.</span>
                  {text}
                </label>

                {q.type === 'text' && (
                  <input type="text" value={val} onChange={e => setAnswer(q.id, e.target.value)}
                    placeholder={text} className={inputCls} />
                )}

                {q.type === 'number' && (
                  <input type="number" value={val} min={0}
                    onChange={e => setAnswer(q.id, e.target.value)} className={inputCls} />
                )}

                {q.type === 'textarea' && (
                  <textarea value={val} rows={3} placeholder={text}
                    onChange={e => setAnswer(q.id, e.target.value)}
                    className={inputCls + ' resize-y'} />
                )}

                {q.type === 'select' && (
                  <select value={val} onChange={e => setAnswer(q.id, e.target.value)}
                    className={inputCls + ' bg-white appearance-none cursor-pointer'}>
                    <option value="">{t(lang, 'select_placeholder')}</option>
                    {opts.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                )}

                {q.type === 'radio' && (
                  <div className="space-y-1 pt-1">
                    {opts.map(o => (
                      <label key={o} className={optionCls}>
                        <input type="radio" name={`${q.id}_s${sphereIdx}`} value={o}
                          checked={val === o} onChange={() => setAnswer(q.id, o)}
                          className="w-4 h-4 accent-accent" />
                        <span className="text-sm text-gray-700 group-hover:text-gray-900">{o}</span>
                      </label>
                    ))}
                  </div>
                )}

                {q.type === 'checkbox' && (
                  <div className="space-y-1 pt-1">
                    {opts.map(o => {
                      const checked = (val ?? '').split(',').filter(Boolean).includes(o)
                      return (
                        <label key={o} className={optionCls}>
                          <input type="checkbox" checked={checked}
                            onChange={() => toggleCheckbox(q.id, o)}
                            className="w-4 h-4 accent-accent rounded" />
                          <span className="text-sm text-gray-700 group-hover:text-gray-900">{o}</span>
                        </label>
                      )
                    })}
                  </div>
                )}

                {q.type === 'address_cascade' && (
                  <AddressCascade lang={lang} value={val} onChange={v => setAnswer(q.id, v)} />
                )}

                {/* Dynamic INN fields after related_companies_count */}
                {q.id === 'related_companies_count' && relatedCount > 0 && (
                  <div className="mt-3 space-y-2 pl-1">
                    {Array.from({ length: relatedCount }, (_, i) => (
                      <div key={i}>
                        <label className="block text-xs font-semibold text-muted mb-1">
                          {ru ? `Компания ${i + 1} — ИНН` : `Kompaniya ${i + 1} — INN`}
                        </label>
                        <input
                          type="text"
                          value={answers[`related_company_inn_${i}`] ?? ''}
                          onChange={e => setAnswer(`related_company_inn_${i}`, e.target.value)}
                          placeholder={ru ? `ИНН компании ${i + 1}` : `Kompaniya ${i + 1} INN`}
                          className={inputCls}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </Card>

      <div className="flex gap-3">
        <Button variant="secondary" onClick={onBack} className="flex-1">
          {t(lang, 'back')}
        </Button>
        <Button variant="primary" onClick={handleNext} className="flex-1">
          {isLast ? t(lang, 'step_summary') : t(lang, 'next')}
        </Button>
      </div>
    </div>
  )
}
