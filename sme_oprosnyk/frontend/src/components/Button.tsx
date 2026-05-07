import { ReactNode, ButtonHTMLAttributes } from 'react'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  children: ReactNode
  fullWidth?: boolean
}

export default function Button({
  variant = 'primary',
  size = 'md',
  children,
  fullWidth = false,
  className = '',
  disabled,
  ...rest
}: Props) {
  const base = 'inline-flex items-center justify-center gap-2 font-semibold rounded-btn transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none'

  const variants = {
    primary:
      'bg-accent text-white hover:bg-blue-600 active:scale-[.98] focus:ring-accent shadow-sm hover:shadow-md',
    secondary:
      'bg-white text-accent border-2 border-accent hover:bg-blue-50 active:scale-[.98] focus:ring-accent',
    ghost:
      'bg-transparent text-muted hover:text-accent hover:bg-gray-100 focus:ring-gray-300',
  }

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-sm',
    lg: 'px-8 py-4 text-base',
  }

  return (
    <button
      disabled={disabled}
      className={`${base} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
      {...rest}
    >
      {children}
    </button>
  )
}
