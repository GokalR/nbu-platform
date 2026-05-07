import { useState, useEffect } from 'react'
import { MapPin, ChevronDown } from 'lucide-react'
import { Lang } from '../types'
import { fetchViloyats, fetchTumans, fetchMfy } from '../api'

interface Props {
  lang: Lang
  value: string
  onChange: (val: string) => void
}

const LABELS = {
  viloyat: { ru: 'Область', uz: 'Вилоят' },
  tuman:   { ru: 'Район', uz: 'Туман' },
  mfy:     { ru: 'МФЙ / Квартал', uz: 'МФЙ / Маҳалла' },
  select:  { ru: '— Выберите —', uz: '— Танланг —' },
  loading: { ru: 'Загрузка...', uz: 'Юкланмоқда...' },
  nodata:  { ru: 'Данные не найдены', uz: 'Маълумот топилмади' },
}

function l(key: keyof typeof LABELS, lang: Lang): string {
  return LABELS[key][lang]
}

// Parse stored value "Viloyat | Tuman | MFY" back to parts
function parseParts(val: string): [string, string, string] {
  const parts = val.split(' | ')
  return [parts[0] ?? '', parts[1] ?? '', parts[2] ?? '']
}

function combine(v: string, t: string, m: string): string {
  if (!v) return ''
  if (!t) return v
  if (!m) return `${v} | ${t}`
  return `${v} | ${t} | ${m}`
}

export default function AddressCascade({ lang, value, onChange }: Props) {
  const [initV, initT, initM] = parseParts(value)

  const [viloyats, setViloyats] = useState<string[]>([])
  const [tumans,   setTumans]   = useState<string[]>([])
  const [mfyList,  setMfyList]  = useState<string[]>([])

  const [selV, setSelV] = useState(initV)
  const [selT, setSelT] = useState(initT)
  const [selM, setSelM] = useState(initM)

  const [loadingV, setLoadingV] = useState(true)
  const [loadingT, setLoadingT] = useState(false)
  const [loadingM, setLoadingM] = useState(false)
  const [noSource, setNoSource] = useState(false)

  // Load viloyats on mount
  useEffect(() => {
    fetchViloyats()
      .then((data) => {
        setViloyats(data.viloyats)
        setNoSource(!data.source_found || data.viloyats.length === 0)
      })
      .catch(() => setNoSource(true))
      .finally(() => setLoadingV(false))
  }, [])

  // Load tumans when viloyat changes
  useEffect(() => {
    if (!selV) { setTumans([]); setSelT(''); setMfyList([]); setSelM(''); return }
    setLoadingT(true)
    setSelT('')
    setMfyList([])
    setSelM('')
    fetchTumans(selV)
      .then((d) => setTumans(d.tumans))
      .catch(() => setTumans([]))
      .finally(() => setLoadingT(false))
  }, [selV])

  // Load MFY when tuman changes
  useEffect(() => {
    if (!selV || !selT) { setMfyList([]); setSelM(''); return }
    setLoadingM(true)
    setSelM('')
    fetchMfy(selV, selT)
      .then((d) => setMfyList(d.mfy))
      .catch(() => setMfyList([]))
      .finally(() => setLoadingM(false))
  }, [selV, selT])

  // Propagate combined value up on any change
  useEffect(() => {
    onChange(combine(selV, selT, selM))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selV, selT, selM])

  if (noSource) {
    // Fallback to text input when Excel file not found
    return (
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={l('viloyat', lang) + ', ' + l('tuman', lang) + ', ' + l('mfy', lang)}
        className="w-full px-4 py-3 border border-border rounded-input text-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-colors"
      />
    )
  }

  const selectCls = 'w-full px-4 py-3 border border-border rounded-input text-sm bg-white focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-colors appearance-none cursor-pointer disabled:bg-gray-50 disabled:text-muted disabled:cursor-not-allowed'

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-muted font-medium mb-1">
        <MapPin size={14} className="text-accent" />
        <span>{l('viloyat', lang)} → {l('tuman', lang)} → {l('mfy', lang)}</span>
      </div>

      {/* Viloyat */}
      <div className="relative">
        <select
          value={selV}
          disabled={loadingV}
          onChange={(e) => setSelV(e.target.value)}
          className={selectCls}
        >
          <option value="">{loadingV ? l('loading', lang) : l('select', lang) + ' ' + l('viloyat', lang)}</option>
          {viloyats.map((v) => <option key={v} value={v}>{v}</option>)}
        </select>
        <ChevronDown size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-muted" />
      </div>

      {/* Tuman */}
      <div className="relative">
        <select
          value={selT}
          disabled={!selV || loadingT}
          onChange={(e) => setSelT(e.target.value)}
          className={selectCls}
        >
          <option value="">{loadingT ? l('loading', lang) : l('select', lang) + ' ' + l('tuman', lang)}</option>
          {tumans.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <ChevronDown size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-muted" />
      </div>

      {/* MFY */}
      <div className="relative">
        <select
          value={selM}
          disabled={!selT || loadingM}
          onChange={(e) => setSelM(e.target.value)}
          className={selectCls}
        >
          <option value="">{loadingM ? l('loading', lang) : l('select', lang) + ' ' + l('mfy', lang)}</option>
          {mfyList.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
        <ChevronDown size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-muted" />
      </div>
    </div>
  )
}
