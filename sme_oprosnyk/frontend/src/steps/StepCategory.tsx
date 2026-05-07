import {
  ShoppingBag, Stethoscope, ShoppingCart, Briefcase,
  Utensils, HardHat, Wheat, Truck, Building2, Layers, Star
} from 'lucide-react'
import { Lang, Category } from '../types'
import { t } from '../i18n'
import Card from '../components/Card'
import Button from '../components/Button'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ICON_MAP: Record<string, React.ComponentType<any>> = {
  ShoppingBag,
  Stethoscope,
  ShoppingCart,
  Briefcase,
  Utensils,
  HardHat,
  Wheat,
  Truck,
  Building2,
  Layers,
  Star,
}

interface Props {
  lang: Lang
  categories: Category[]
  sphereIdx: number
  sphereCount: number
  selectedId: string
  onNext: (id: string, nameRu: string, nameUz: string) => void
  onBack: () => void
}

export default function StepCategory({ lang, categories, sphereIdx, sphereCount, selectedId, onNext, onBack }: Props) {
  const label = t(lang, 'category_sphere')
    .replace('{n}', String(sphereIdx + 1))
    .replace('{total}', String(sphereCount))

  const handleSelect = (cat: Category) => {
    onNext(cat.id, cat.name.ru, cat.name.uz)
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <p className="inline-block text-xs font-semibold text-accent bg-blue-50 px-3 py-1 rounded-full">
          {label}
        </p>
        <h2 className="text-2xl font-bold text-primary">{t(lang, 'category_title')}</h2>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {categories.map((cat) => {
          const Icon = ICON_MAP[cat.icon] ?? Briefcase
          const isSelected = cat.id === selectedId
          return (
            <button
              key={cat.id}
              onClick={() => handleSelect(cat)}
              className={`group flex flex-col items-center gap-3 p-5 rounded-card border-2 transition-all duration-200 text-center ${
                isSelected
                  ? 'border-accent bg-blue-50 shadow-md'
                  : 'border-border bg-white hover:border-accent/50 hover:shadow-card-hover hover:bg-blue-50/40'
              }`}
            >
              <div
                className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-colors ${
                  isSelected ? 'bg-accent' : 'bg-blue-50 group-hover:bg-accent/10'
                }`}
              >
                <Icon
                  size={24}
                  className={isSelected ? 'text-white' : 'text-accent'}
                />
              </div>
              <span
                className={`text-sm font-semibold leading-tight ${
                  isSelected ? 'text-accent' : 'text-gray-800'
                }`}
              >
                {cat.name[lang]}
              </span>
            </button>
          )
        })}
      </div>

      <Button variant="secondary" onClick={onBack} fullWidth>
        {t(lang, 'back')}
      </Button>
    </div>
  )
}
