/* global React */
// Shared atoms — NBU Material Design 3 style.

// AppIcon — uses Material Icons font (matches HomeView's AppIcon component).
function Icon({ name, size = 18, filled = false, style, className = '' }) {
  return (
    <span
      className={'material-icons ' + className}
      style={{
        fontSize: size,
        verticalAlign: 'middle',
        ...style,
      }}
    >{name}</span>
  );
}

// Sparkline — simple line + area, with last-point dot
function Sparkline({ points, w = 80, h = 28, color = '#0046AD', area = true, baseline = 100 }) {
  if (!points || !points.length) return null;
  const min = Math.min(...points, baseline) - 1;
  const max = Math.max(...points, baseline) + 1;
  const sx = (i) => (i / (points.length - 1)) * w;
  const sy = (v) => h - ((v - min) / (max - min)) * h;
  const d = points.map((v, i) => `${i === 0 ? 'M' : 'L'} ${sx(i).toFixed(1)} ${sy(v).toFixed(1)}`).join(' ');
  const ad = `${d} L ${w} ${h} L 0 ${h} Z`;
  const lastX = sx(points.length - 1);
  const lastY = sy(points[points.length - 1]);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width={w} height={h} preserveAspectRatio="none" style={{ display: 'block' }}>
      <line x1="0" y1={sy(baseline)} x2={w} y2={sy(baseline)}
            stroke={color} strokeWidth="0.5" strokeDasharray="2 2" opacity="0.3"/>
      {area && <path d={ad} fill={color} opacity="0.10"/>}
      <path d={d} fill="none" stroke={color} strokeWidth="1.4" strokeLinejoin="round" strokeLinecap="round"/>
      <circle cx={lastX} cy={lastY} r="2" fill={color}/>
    </svg>
  );
}

// Tone semantics — green for growth, red for negative, neutral for ~100
const TONE_COLORS = {
  'pos-strong': { fg: '#1B5E20', bg: '#C7E7C9', dot: '#2E7D32', soft: '#E8F5E9' },
  'pos':        { fg: '#2E7D32', bg: '#DCEDC8', dot: '#558B2F', soft: '#F1F8E9' },
  'neu':        { fg: '#44464F', bg: '#E8EAF0', dot: '#74777F', soft: '#F4F5F9' },
  'neg':        { fg: '#B3261E', bg: '#F9DEDC', dot: '#B3261E', soft: '#FCE9E7' },
  'na':         { fg: '#74777F', bg: '#EEEFF4', dot: '#A8AAB1', soft: '#F4F5F9' },
};

// Direction arrow (Material drop arrows)
function DirectionArrow({ direction, size = 20 }) {
  if (direction === 'up')   return <Icon name="arrow_drop_up"   size={size} style={{ color: 'var(--tertiary)' }}/>;
  if (direction === 'down') return <Icon name="arrow_drop_down" size={size} style={{ color: 'var(--error)' }}/>;
  return null;
}

// Period switcher — pill style matching HomeView's bg-surface-container rounded-full
function PeriodSwitcher({ value, onChange }) {
  const options = [
    { id: '2025',   label: 'Янв–Дек 2025' },
    { id: '2026Q1', label: 'I кв. 2026' },
  ];
  return (
    <div style={{
      display: 'inline-flex', padding: 3, borderRadius: 999,
      background: 'var(--surface-container)',
      fontSize: 11, fontWeight: 700,
    }}>
      {options.map(o => {
        const active = value === o.id;
        return (
          <button key={o.id}
            onClick={() => onChange && onChange(o.id)}
            style={{
              border: 0, padding: '6px 14px', borderRadius: 999, cursor: 'pointer',
              background: active ? 'var(--primary)' : 'transparent',
              color: active ? 'var(--on-primary)' : 'var(--on-surface-variant)',
              fontFamily: 'inherit', fontSize: 11, fontWeight: 700,
              letterSpacing: '0.02em',
              transition: 'all 0.15s ease',
            }}>
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

// Tone helper, period labels reused across panels
function getTone(v) {
  if (v == null) return 'na';
  if (v >= 110)  return 'pos-strong';
  if (v >= 102)  return 'pos';
  if (v >= 99)   return 'neu';
  return 'neg';
}

Object.assign(window, {
  Icon, Sparkline, TONE_COLORS, DirectionArrow, PeriodSwitcher, getTone,
});
