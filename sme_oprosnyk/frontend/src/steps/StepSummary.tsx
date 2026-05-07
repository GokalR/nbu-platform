import { FileText, AlertCircle } from 'lucide-react'
import { Lang, SphereData, ClientInfo } from '../types'
import { t } from '../i18n'
import Card from '../components/Card'
import Button from '../components/Button'

interface Props {
  lang: Lang
  pinflInn: string
  clientInfo: ClientInfo | null
  sphereCount: number
  spheres: SphereData[]
  onBack: () => void
  onSubmit: () => void
  submitting: boolean
  submitError: string | null
}

function Row({ label, value }: { label: string; value: string | number | undefined }) {
  if (!value && value !== 0) return null
  return (
    <div className="py-2.5 grid grid-cols-2 gap-4 border-b border-border last:border-0">
      <p className="text-xs text-muted font-medium leading-relaxed">{label}</p>
      <p className="text-sm text-gray-900 font-semibold break-words">{String(value)}</p>
    </div>
  )
}

export default function StepSummary({
  lang, pinflInn, clientInfo: ci, sphereCount, spheres, onBack, onSubmit, submitting, submitError
}: Props) {
  const ru = lang === 'ru'

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-50 rounded-2xl">
          <FileText size={28} className="text-accent" />
        </div>
        <h2 className="text-2xl font-bold text-primary">{t(lang, 'summary_title')}</h2>
        <p className="text-sm text-muted">{t(lang, 'summary_subtitle')}</p>
      </div>

      {/* General info from Руйхат-2 */}
      <Card padding="md">
        <p className="text-xs font-bold text-accent uppercase tracking-wide mb-3">
          {ru ? 'Общая информация' : 'Umumiy ma\'lumot'}
        </p>
        <Row label={ru ? 'ПИНФЛ / ИНН' : 'PINFL / INN'} value={pinflInn} />
        {ci && <>
          <Row label={ru ? 'Наименование организации' : 'Tashkilot nomi'} value={ci.company_name} />
          <Row label={ru ? 'Директор' : 'Direktor'} value={ci.director} />
          <Row label={ru ? 'Главный бухгалтер' : 'Bosh buxgalter'} value={ci.accountant} />
          <Row label={ru ? 'Юридический адрес' : 'Yuridik manzil'} value={ci.reg_address} />
          <Row label={ru ? 'Телефон' : 'Telefon'} value={ci.phone} />
          <Row label={ru ? 'Вид деятельности' : 'Faoliyat turi'} value={ci.activity_type} />
        </>}
        <Row label={ru ? 'Количество сфер' : 'Soha soni'} value={sphereCount} />
      </Card>

      {/* Financial indicators — always shown when clientInfo exists */}
      {ci && (
        <Card padding="md">
          <p className="text-xs font-bold text-accent uppercase tracking-wide mb-3">
            {ru ? 'Финансовые показатели' : 'Moliyaviy ko\'rsatkichlar'}
          </p>
          <Row label={ru ? 'Общий оборот (сум)' : 'Jami aylanma (so\'m)'} value={ci.turnover_all || '—'} />
          <Row label={ru ? 'Дебет (сум)' : 'Debet (so\'m)'} value={ci.turnover_debit || '—'} />
          <Row label={ru ? 'Кредит (сум)' : 'Kredit (so\'m)'} value={ci.turnover_credit || '—'} />
          <Row label={ru ? 'Фонд оплаты труда' : 'Ish haqi jamg\'armasi'} value={ci.sal_sum || '—'} />
          <Row label={ru ? 'Кол-во акционеров' : 'Aksiyadorlar soni'} value={ci.shareholders_count || '—'} />
        </Card>
      )}

      {/* Sphere answers */}
      {spheres.map((sphere, si) => (
        <Card key={si} padding="md">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-xs font-bold text-white bg-accent px-3 py-1 rounded-full">
              {ru ? 'Сфера' : 'Soha'} {sphere.sphere_number}
            </span>
            <span className="text-sm font-semibold text-gray-800">
              {ru ? sphere.category_name_ru : sphere.category_name_uz}
            </span>
          </div>
          <div className="divide-y divide-border">
            {sphere.answers.map(ans => (
              <div key={ans.question_id} className="py-2.5 grid grid-cols-2 gap-4">
                <p className="text-xs text-muted font-medium">{ru ? ans.question_text_ru : ans.question_text_uz}</p>
                <p className="text-sm text-gray-900 font-semibold break-words">
                  {ans.answer || <span className="text-gray-300 italic">—</span>}
                </p>
              </div>
            ))}
          </div>
        </Card>
      ))}

      {submitError && (
        <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-card p-4">
          <AlertCircle size={18} className="text-error mt-0.5 shrink-0" />
          <p className="text-sm text-error">{submitError}</p>
        </div>
      )}

      <div className="flex gap-3">
        <Button variant="secondary" onClick={onBack} className="flex-1" disabled={submitting}>
          {t(lang, 'back')}
        </Button>
        <Button variant="primary" onClick={onSubmit} className="flex-1" disabled={submitting}>
          {submitting ? t(lang, 'submitting') : t(lang, 'submit')}
        </Button>
      </div>
    </div>
  )
}
