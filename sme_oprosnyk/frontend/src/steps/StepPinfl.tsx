import { useState } from 'react'
import { UserCheck, Search, Building2, User, Phone, MapPin, AlertCircle } from 'lucide-react'
import { Lang, ClientInfo } from '../types'
import { t } from '../i18n'
import { lookupClient } from '../api'
import Card from '../components/Card'
import Button from '../components/Button'

interface Props {
  lang: Lang
  initialValue: string
  initialClientInfo: ClientInfo | null
  initialSphereCount: number
  onNext: (val: string, clientInfo: ClientInfo | null, sphereCount: number) => void
}

export default function StepPinfl({ lang, initialValue, initialClientInfo, initialSphereCount, onNext }: Props) {
  const [value, setValue]           = useState(initialValue)
  const [error, setError]           = useState('')
  const [searching, setSearching]   = useState(false)
  const [clientInfo, setClientInfo] = useState<ClientInfo | null>(initialClientInfo)
  const [notFound, setNotFound]     = useState(false)
  const [sphereCount, setSphereCount] = useState(initialSphereCount)
  const [searched, setSearched] = useState(!!initialClientInfo)

  const ru = lang === 'ru'

  const handleSearch = async () => {
    if (!value.trim()) { setError(t(lang, 'error_empty')); return }
    setSearching(true); setError(''); setNotFound(false); setClientInfo(null); setSearched(false)
    try {
      const res = await lookupClient(value.trim())
      if (res.found) {
        setClientInfo({
          company_name:      res.company_name,
          director:          res.director,
          reg_address:       res.reg_address,
          phone:             res.phone,
          turnover_debit:    res.turnover_debit,
          turnover_credit:   res.turnover_credit,
          turnover_all:      res.turnover_all,
          shareholders_count: res.shareholders_count,
          accountant:        res.accountant,
          activity_type:     res.activity_type,
          sal_sum:           res.sal_sum,
        })
      } else {
        setNotFound(true)
        setSearched(true)
      }
    } catch {
      setError(t(lang, 'error_backend'))
    } finally {
      setSearching(false)
      setSearched(true)
    }
  }

  const handleNext = () => {
    if (!value.trim()) { setError(t(lang, 'error_empty')); return }
    onNext(value.trim(), clientInfo, sphereCount)
  }

  const infoRows: Array<{ icon: React.ReactNode; label: string; val: string }> = clientInfo
    ? [
        { icon: <Building2 size={15} className="text-accent" />, label: ru ? 'Организация' : 'Tashkilot',  val: clientInfo.company_name },
        { icon: <User      size={15} className="text-accent" />, label: ru ? 'Директор'    : 'Direktor',   val: clientInfo.director },
        { icon: <MapPin    size={15} className="text-accent" />, label: ru ? 'Адрес'       : 'Manzil',     val: clientInfo.reg_address },
        { icon: <Phone     size={15} className="text-accent" />, label: ru ? 'Телефон'     : 'Telefon',    val: clientInfo.phone },
      ].filter(r => r.val)
    : []

  return (
    <div className="space-y-6">
      <div className="text-center space-y-3">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-2xl">
          <UserCheck size={32} className="text-accent" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-primary">{t(lang, 'pinfl_title')}</h2>
          <p className="text-sm text-muted mt-1">{t(lang, 'pinfl_hint')}</p>
        </div>
      </div>

      <Card>
        <div className="space-y-4">
          <label className="block text-sm font-semibold text-gray-700">{t(lang, 'pinfl_label')}</label>

          <div className="flex gap-2">
            <input
              type="text"
              value={value}
              onChange={e => { setValue(e.target.value); setError(''); setClientInfo(null); setNotFound(false) }}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder={t(lang, 'pinfl_placeholder')}
              className={`flex-1 px-4 py-3.5 border rounded-input text-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-colors ${error ? 'border-error bg-red-50' : 'border-border'}`}
              autoFocus
            />
            <button
              onClick={handleSearch}
              disabled={searching || !value.trim()}
              className="px-4 py-3.5 bg-accent text-white rounded-input text-sm font-semibold hover:bg-blue-600 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0"
            >
              {searching
                ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                : <Search size={16} />}
              {ru ? 'Поиск' : 'Qidirish'}
            </button>
          </div>

          {error && <p className="text-xs text-error font-medium">{error}</p>}

          {notFound && !clientInfo && (
            <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-input px-4 py-3">
              <AlertCircle size={16} className="text-amber-500 shrink-0" />
              <p className="text-xs text-amber-700">
                {ru ? 'Запись не найдена в базе данных. Вы всё равно можете продолжить.' : 'Ma\'lumotlar bazasida topilmadi. Davom etishingiz mumkin.'}
              </p>
            </div>
          )}

          {clientInfo && infoRows.length > 0 && (
            <div className="bg-blue-50 border border-blue-100 rounded-[16px] p-4 space-y-2.5">
              <p className="text-xs font-bold text-accent uppercase tracking-wide mb-3">
                {ru ? '✓ Данные найдены' : '✓ Ma\'lumot topildi'}
              </p>
              {infoRows.map(r => (
                <div key={r.label} className="flex items-start gap-2.5">
                  <span className="mt-0.5 shrink-0">{r.icon}</span>
                  <div>
                    <span className="text-xs text-muted">{r.label}: </span>
                    <span className="text-sm font-semibold text-gray-900">{r.val}</span>
                  </div>
                </div>
              ))}
              {(clientInfo.turnover_all || clientInfo.turnover_debit || clientInfo.accountant) && (
                <div className="mt-2 pt-2 border-t border-blue-200 space-y-1.5">
                  {clientInfo.accountant && (
                    <div className="flex justify-between gap-2">
                      <span className="text-xs text-muted">{ru ? 'Бош бухгалтер' : 'Bosh buxgalter'}:</span>
                      <span className="text-xs font-semibold text-gray-900 text-right">{clientInfo.accountant}</span>
                    </div>
                  )}
                  {clientInfo.turnover_all && (
                    <div className="flex justify-between gap-2">
                      <span className="text-xs text-muted">{ru ? 'Оборот (итого)' : 'Aylanma (jami)'}:</span>
                      <span className="text-xs font-semibold text-gray-900">{clientInfo.turnover_all}</span>
                    </div>
                  )}
                  {clientInfo.turnover_debit && (
                    <div className="flex justify-between gap-2">
                      <span className="text-xs text-muted">{ru ? 'Дебет' : 'Debet'}:</span>
                      <span className="text-xs font-semibold text-gray-900">{clientInfo.turnover_debit}</span>
                    </div>
                  )}
                  {clientInfo.turnover_credit && (
                    <div className="flex justify-between gap-2">
                      <span className="text-xs text-muted">{ru ? 'Кредит' : 'Kredit'}:</span>
                      <span className="text-xs font-semibold text-gray-900">{clientInfo.turnover_credit}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Sphere count selector */}
      <Card padding="md">
        <p className="text-sm font-semibold text-gray-700 mb-3">
          {ru ? 'Количество сфер деятельности' : 'Faoliyat sohalari soni'}
        </p>
        <div className="flex flex-wrap gap-2">
          {[1, 2, 3, 4, 5].map(n => (
            <button
              key={n}
              onClick={() => setSphereCount(n)}
              className={`w-11 h-11 rounded-xl text-sm font-bold border-2 transition-all ${
                sphereCount === n
                  ? 'bg-accent text-white border-accent shadow-md'
                  : 'bg-white text-gray-600 border-border hover:border-accent hover:text-accent'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
        <p className="text-xs text-muted mt-2">
          {ru ? `Выбрано: ${sphereCount} ${sphereCount === 1 ? 'сфера' : sphereCount < 5 ? 'сферы' : 'сфер'}` : `Tanlandi: ${sphereCount} soha`}
        </p>
      </Card>

      {!searched && (
        <p className="text-xs text-center text-muted">
          {ru ? 'Введите ПИНФЛ / ИНН и нажмите «Поиск» перед продолжением' : 'PINFL / INN kiriting va «Qidirish» tugmasini bosing'}
        </p>
      )}
      <Button variant="primary" fullWidth size="lg" onClick={handleNext} disabled={!searched}>
        {t(lang, 'next')}
      </Button>
    </div>
  )
}
