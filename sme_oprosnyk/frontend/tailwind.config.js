/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1F3A5F',
        accent:  '#3B82F6',
        success: '#16A34A',
        error:   '#DC2626',
        muted:   '#6B7280',
        border:  '#E5E7EB',
      },
      borderRadius: {
        card:  '24px',
        btn:   '16px',
        input: '14px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0,0,0,.06), 0 4px 16px 0 rgba(0,0,0,.04)',
        'card-hover': '0 4px 12px 0 rgba(0,0,0,.1)',
      },
    },
  },
  plugins: [],
}
