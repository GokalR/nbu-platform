/* global React, Icon, Sparkline, DirectionArrow, PeriodSwitcher, getTone */
// V1 — REFINED. Same 10-tile MD3 grid as HomeView, but with sharper hierarchy:
// hero GRP tile, tone-coded chips, sparklines, NBU palette.

const FIGURE_METRICS = [
  { key: 'grp',          icon: 'show_chart',     labelRu: 'Валовой региональный продукт' },
  { key: 'industry',     icon: 'factory',        labelRu: 'Промышленность' },
  { key: 'agriculture',  icon: 'agriculture',    labelRu: 'Сельское, лесное и рыбное хозяйство' },
  { key: 'investment',   icon: 'savings',        labelRu: 'Инвестиции в основной капитал' },
  { key: 'construction', icon: 'construction',   labelRu: 'Строительные работы' },
  { key: 'freight',      icon: 'local_shipping', labelRu: 'Грузооборот' },
  { key: 'passenger',    icon: 'directions_bus', labelRu: 'Пассажирооборот' },
  { key: 'retail',       icon: 'storefront',     labelRu: 'Розничный товарооборот' },
  { key: 'services',     icon: 'handyman',       labelRu: 'Услуги' },
  { key: 'population',   icon: 'groups',         labelRu: 'Численность постоянного населения' },
];

function PanelV1({ region, period }) {
  const D = window.RegionData;
  const r = region.raqamlarda;

  const sparkSeries = (key, end) => D.sparkSeries(region.shortRu, key, end);

  const tiles = FIGURE_METRICS.map(m => {
    if (m.key === 'population') {
      return {
        ...m, value: D.fmtCount(r.populationCount), isPercent: false,
        footnote: r.populationDate ? 'По состоянию на 1.01.2026' : 'на текущую дату',
        hasData: r.populationCount != null,
      };
    }
    // Tashkent city: replace agriculture with foreign trade
    if (m.key === 'agriculture' && r.agriculture == null && r.tashqi_savdo != null) {
      const v = r.tashqi_savdo;
      return {
        key: 'tashqi_savdo', icon: 'currency_exchange',
        labelRu: 'Внешнеторговый оборот',
        value: v.toFixed(1) + '%', raw: v, isPercent: true, hasData: true,
        direction: v > 100 ? 'up' : v < 100 ? 'down' : 'flat',
        footnote: 'в % к январю — декабрю 2024 г.',
      };
    }
    const v = r[m.key];
    return {
      ...m,
      value: v != null ? v.toFixed(1) + '%' : 'нет данных',
      raw: v, isPercent: true, hasData: v != null,
      direction: v == null ? 'flat' : v > 100 ? 'up' : v < 100 ? 'down' : 'flat',
      footnote: v != null ? (period === '2026Q1'
        ? 'в % к январю — марту 2025 г.'
        : 'в % к январю — декабрю 2024 г.') : '',
    };
  });

  return (
    <section className="elev-1" style={{
      background: 'var(--surface-container-lowest)',
      borderRadius: 12,
      padding: '24px 28px',
    }}>
      {/* Header */}
      <header style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        gap: 6, marginBottom: 22, position: 'relative',
      }}>
        <h2 style={{
          margin: 0, fontSize: 22, fontWeight: 800, letterSpacing: '-0.01em',
          textTransform: 'uppercase', color: 'var(--on-surface)',
          textAlign: 'center',
        }}>
          {region.nameRu} в цифрах
        </h2>
        <p style={{ margin: 0, fontSize: 13, color: 'var(--on-surface-variant)' }}>
          (по состоянию за {period === '2026Q1' ? 'январь — март 2026' : 'январь — декабрь 2025'} г.)
        </p>
        <div style={{ position: 'absolute', right: 0, top: 0 }}>
          <PeriodSwitcher value={period} onChange={() => {}}/>
        </div>
      </header>

      {/* Grid 5×2 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: 16,
      }}>
        {tiles.map(t => {
          const tone = window.TONE_COLORS[getTone(t.raw)];
          return (
            <article key={t.key} style={{
              padding: '18px 16px',
              background: 'var(--surface-container-low)',
              borderRadius: 12,
              display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 8,
              transition: 'all 0.15s ease', cursor: 'pointer',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--surface-container)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--surface-container-low)'; }}
            >
              <span className="icon-chip">
                <Icon name={t.icon} size={24} filled/>
              </span>
              <p style={{
                margin: 0, fontSize: 11, fontWeight: 700, lineHeight: 1.25,
                letterSpacing: '0.06em', textTransform: 'uppercase',
                color: 'var(--on-surface-variant)',
                minHeight: 28,
                display: 'flex', alignItems: 'center',
              }}>
                {t.labelRu}
              </p>
              <p className="tabular" style={{
                margin: 0, fontSize: 26, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.01em',
                color: t.hasData ? 'var(--on-surface)' : 'var(--on-surface-variant)',
                display: 'inline-flex', alignItems: 'baseline', gap: 1,
              }}>
                <span>{t.value}</span>
                <DirectionArrow direction={t.direction} size={20}/>
              </p>
              <p style={{
                margin: 0, fontSize: 10, lineHeight: 1.3,
                color: 'var(--on-surface-variant)',
                minHeight: 14,
              }}>
                {t.footnote}
              </p>

              {t.isPercent && t.hasData && (
                <div style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6, marginTop: 2 }}>
                  <span className="tabular" style={{
                    fontSize: 10, fontWeight: 700, color: tone.fg, background: tone.bg,
                    padding: '2px 6px', borderRadius: 999,
                  }}>
                    {(t.raw - 100 >= 0 ? '+' : '') + (t.raw - 100).toFixed(1)} п.п.
                  </span>
                  <div style={{ width: 50, height: 16 }}>
                    <Sparkline points={sparkSeries(t.key, t.raw)} w={50} h={16} color={tone.dot}/>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>

      {/* Source attribution */}
      <p style={{
        margin: '18px 0 0', fontSize: 11, fontStyle: 'italic',
        color: 'var(--on-surface-variant)', textAlign: 'right',
      }}>
        Источник: {region.source} (январь — декабрь 2025 г.)
      </p>
    </section>
  );
}

window.PanelV1 = PanelV1;
