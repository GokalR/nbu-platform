import { ReactNode } from 'react'

interface Props {
  children: ReactNode
  className?: string
  padding?: 'sm' | 'md' | 'lg'
}

export default function Card({ children, className = '', padding = 'lg' }: Props) {
  const pad = { sm: 'p-4', md: 'p-6', lg: 'p-8' }[padding]
  return (
    <div className={`bg-white rounded-card shadow-card border border-border ${pad} ${className}`}>
      {children}
    </div>
  )
}
