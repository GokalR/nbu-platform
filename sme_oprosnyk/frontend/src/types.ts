export type Lang = 'ru' | 'uz'

export interface BilingualText {
  ru: string
  uz: string
}

export interface Question {
  id: string
  text: BilingualText
  type: 'text' | 'number' | 'select' | 'textarea' | 'radio' | 'checkbox' | 'address_cascade'
  options: { ru: string[]; uz: string[] }
}

export interface Category {
  id: string
  name: BilingualText
  icon: string
  questions: Question[]
}

export interface QuestionsResponse {
  categories: Category[]
}

/** Fields auto-populated from Руйхат-2 lookup */
export interface ClientInfo {
  company_name: string
  director: string
  reg_address: string
  phone: string
  turnover_debit: string
  turnover_credit: string
  turnover_all: string
  shareholders_count: string
  accountant: string
  activity_type: string
  sal_sum: string
}

export interface AnswerItem {
  question_id: string
  question_text_ru: string
  question_text_uz: string
  answer: string
}

export interface SphereData {
  sphere_number: number
  category_id: string
  category_name_ru: string
  category_name_uz: string
  answers: AnswerItem[]
}

export interface SubmissionPayload {
  pinfl_or_inn: string
  sphere_count: number
  spheres: SphereData[]
  client_info?: ClientInfo
}
