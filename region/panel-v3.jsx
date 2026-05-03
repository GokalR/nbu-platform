/* global React, Icon, Sparkline, DirectionArrow, PeriodSwitcher, getTone */
// V3 — DASHBOARD. Bold editorial layout with primary masthead, large GRP hero,
// rank cards, full deviation chart. NBU/M3 surface tokens throughout.

const V3_METRICS = [
  { key: 'grp',          icon: 'show_chart',     labelRu: 'ВРП',                shortRu: 'ВРП' },
  { key: 'industry',     icon: 'factory',        labelRu: 'Промышленность',     shortRu: 'Промышленность' },
  { key: 'agriculture',  icon: 'agriculture',    labelRu: 'Сельское хоз-во',    shortRu: 'Сельское хоз-во' },
  { key: 'investment',   icon: 'savings',        labelRu: 'Инвестиции',         shortRu: 'Инвестиции' },
  { key: 'construction', icon: 'construction',   labelRu: 'Стройка',            shortRu: 'Стройка' },
  { key: 'freight',      icon: 'local_shipping', labelRu: 'Грузооборот',        shortRu: 'Грузооборот' },
  { key: 'passenger',    icon: 'directions_bus', labelRu: 'Пассажирооборот',    shortRu: 'Пассажиры' },
  { key: 'retail',       icon: 'storefront',     labelRu: 'Розница',            shortRu: 'Розница' },
  { key: 'services',     icon: 'handyman',       labelRu: 'Услуги',             shortRu: 'Услуги' },
];

function MetricBar({ region, metric, max }) {
  const D = window.RegionData;
  const v = region.raqamlarda[metric.key];
  const tone = window.TONE_COLORS[getTone(v)];
  const nat = D.NATIONAL.raqamlarda[metric.key];

  if (v == null) {
    return (
      <div style={{
        display: 'grid', gridTemplateColumns: '180px 1fr 110px',
        gap: 14, alignItems: 'center', padding: '10px 0',
        borderBottom: '1px dashed var(--outline-variant)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="icon-chip-sm icon-chip" style={{ width: 28, height: 28, opacity: 0.5 }}>
            <Icon name={metric.icon} size={14} filled/>
          </span>
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface-variant)' }}>{metric.shortRu}</span>
        </div>
        <div style={{ height: 6, background: 'var(--surface-container)', borderRadius: 999 }}/>
        <span style={{ fontSize: 11, color: 'var(--on-surface-variant)', textAlign: 'right' }}>нет данных</span>
      </div>
    );
  }

  const delta = v - 100;
  const pct = Math.min(Math.abs(delta) / max, 1);
  // Bars all show positive deltas to right of zero anchor at 12% from left
  const ZERO_LEFT = 12;
  const barWidthPct = pct * (100 - ZERO_LEFT - 2);

  // National tick position
  let natTickLeft = null;
  if (nat != null) {
    const natDelta = nat - 100;
    const natPct = Math.min(Math.abs(natDelta) / max, 1);
    natTickLeft = natDelta >= 0
      ? ZERO_LEFT + natPct * (100 - ZERO_LEFT - 2)
      : ZERO_LEFT - natPct * (ZERO_LEFT - 2);
  }

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '180px 1fr 110px',
      gap: 14, alignItems: 'center', padding: '11px 0',
      borderBottom: '1px solid var(--outline-variant)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span className="icon-chip-sm icon-chip" style={{ width: 28, height: 28 }}>
          <Icon name={metric.icon} size={14} filled/>
        </span>
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface)' }}>{metric.shortRu}</span>
      </div>

      <div style={{ position: 'relative', height: 24 }}>
        {/* baseline */}
        <div style={{
          position: 'absolute', left: 0, right: 0, top: '50%', height: 1,
          background: 'var(--outline-variant)',
        }}/>
        {/* zero anchor */}
        <div style={{
          position: 'absolute', left: `${ZERO_LEFT}%`, top: 0, bottom: 0, width: 2,
          background: 'var(--on-surface-variant)',
        }}/>
        {/* bar */}
        <div style={{
          position: 'absolute',
          ...(delta >= 0
            ? { left: `${ZERO_LEFT}%`, width: `${barWidthPct}%` }
            : { right: `${100 - ZERO_LEFT}%`, width: `${pct * (ZERO_LEFT - 2)}%` }),
          top: 5, bottom: 5,
          background: tone.dot,
          borderRadius: 4,
        }}/>
        {/* national tick */}
        {natTickLeft != null && (
          <div style={{
            position: 'absolute', left: `${natTickLeft}%`,
            top: -2, bottom: -2, width: 2,
            background: 'var(--primary)',
            boxShadow: '0 0 0 2px var(--surface-container-lowest)',
          }} title={`Узбекистан: ${nat.toFixed(1)}%`}/>
        )}
      </div>

      <div className="tabular" style={{ textAlign: 'right' }}>
        <span style={{ fontSize: 16, fontWeight: 800, color: tone.fg }}>
          {(delta >= 0 ? '+' : '') + delta.toFixed(1)}
        </span>
        <span style={{ fontSize: 10, color: 'var(--on-surface-variant)', marginLeft: 4 }}>
          п.п.
        </span>
      </div>
    </div>
  );
}

function RankCard({ label, region, metric, isBottom }) {
  const D = window.RegionData;
  const v = region.raqamlarda[metric.key];
  const delta = D.pctDelta(v);
  const tone = window.TONE_COLORS[getTone(v)];

  return (
    <div style={{
      padding: '14px 16px',
      background: isBottom ? 'var(--error-container)' : 'var(--tertiary-container)',
      borderRadius: 12,
      display: 'flex', alignItems: 'center', gap: 12,
    }}>
      <span className="icon-chip-sm" style={{
        width: 38, height: 38, borderRadius: 999,
        background: isBottom ? 'rgba(179, 38, 30, 0.15)' : 'rgba(46, 125, 50, 0.15)',
        color: isBottom ? 'var(--error)' : 'var(--tertiary)',
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <Icon name={metric.icon} size={18} filled/>
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase',
          color: isBottom ? 'var(--on-error-container)' : 'var(--on-tertiary-container)',
          marginBottom: 2, opacity: 0.75,
        }}>
          {label}
        </div>
        <div style={{
          fontSize: 13, fontWeight: 600, lineHeight: 1.2, marginBottom: 2,
          color: isBottom ? 'var(--on-error-container)' : 'var(--on-tertiary-container)',
        }}>
          {metric.labelRu}
        </div>
        <div className="tabular" style={{
          fontSize: 18, fontWeight: 800,
          color: isBottom ? 'var(--on-error-container)' : 'var(--on-tertiary-container)',
        }}>
          {delta > 0 ? '+' : ''}{delta.toFixed(1)} п.п.
          <span style={{ fontSize: 11, fontWeight: 500, opacity: 0.7, marginLeft: 6 }}>
            ({v.toFixed(1)}%)
          </span>
        </div>
      </div>
    </div>
  );
}

function PanelV3({ region, period }) {
  const D = window.RegionData;
  const r = region.raqamlarda;

  const ranked = V3_METRICS.filter(m => m.key !== 'grp')
    .map(m => ({ m, v: r[m.key] }))
    .filter(x => x.v != null)
    .sort((a, b) => b.v - a.v);
  const tops = ranked.slice(0, 2);
  const bottoms = ranked.slice(-2).reverse();

  const bars = V3_METRICS.filter(m => m.key !== 'grp' && r[m.key] != null);
  const maxAbs = Math.max(...bars.map(m => Math.abs(r[m.key] - 100)), 5);

  const grpDelta = D.pctDelta(r.grp);
  const grpVsNat = D.deltaVsNational(r.grp, 'grp');
  const grpTone = window.TONE_COLORS[getTone(r.grp)];

  return (
    <section className="elev-2" style={{
      background: 'var(--surface-container-lowest)',
      borderRadius: 12,
      overflow: 'hidden',
    }}>
      {/* Masthead — primary blue */}
      <header style={{
        background: 'var(--primary)',
        color: 'var(--on-primary)',
        padding: '20px 28px',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
          gap: 16, flexWrap: 'wrap',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <Icon name="location_on" size={16} filled/>
              <span className="eyebrow" style={{ color: 'rgba(255,255,255,0.85)' }}>
                Аналитика по регионам · {region.source}
              </span>
            </div>
            <h1 style={{
              margin: 0, fontSize: 28, fontWeight: 800, letterSpacing: '-0.02em',
              color: 'var(--on-primary)', textTransform: 'uppercase',
            }}>
              {region.nameRu}
            </h1>
            <p style={{ margin: '4px 0 0', fontSize: 12, color: 'rgba(255,255,255,0.85)' }}>
              · Районов: {region.districts}
              {region.cities && <> · Городов: {region.cities}</>}
              · Махаллей: {region.mahallas}
              · Площадь: {region.area}
            </p>
          </div>
          <PeriodSwitcher value={period} onChange={() => {}}/>
        </div>
      </header>

      {/* Hero KPI band */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
        borderBottom: '1px solid var(--outline-variant)',
      }}>
        {/* GRP hero */}
        <div style={{
          padding: '24px 28px',
          borderRight: '1px solid var(--outline-variant)',
          background: 'var(--surface-container-low)',
        }}>
          <div className="eyebrow" style={{ marginBottom: 8 }}>Валовой региональный продукт</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 12 }}>
            <span className="tabular" style={{
              fontSize: 64, fontWeight: 800, lineHeight: 0.95, letterSpacing: '-0.03em',
              color: 'var(--on-surface)',
            }}>
              {r.grp != null ? r.grp.toFixed(1) : '—'}
            </span>
            {r.grp != null && (
              <span className="tabular" style={{ fontSize: 22, color: 'var(--on-surface-variant)', fontWeight: 600 }}>%</span>
            )}
          </div>
          {grpDelta != null && (
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 10 }}>
              <span className="tabular" style={{
                fontSize: 11, fontWeight: 700,
                background: grpTone.bg, color: grpTone.fg,
                padding: '4px 10px', borderRadius: 999,
              }}>
                {grpDelta > 0 ? '▲' : '▼'} {(grpDelta >= 0 ? '+' : '') + grpDelta.toFixed(1)} п.п. к 2024 г.
              </span>
              {grpVsNat != null && (
                <span className="tabular" style={{
                  fontSize: 11, fontWeight: 700,
                  color: grpVsNat >= 0 ? 'var(--tertiary)' : 'var(--error)',
                }}>
                  {grpVsNat >= 0 ? '↑' : '↓'} {Math.abs(grpVsNat).toFixed(1)} п.п. над средним по Узбекистану
                </span>
              )}
            </div>
          )}
          {r.grp != null && (
            <div style={{ marginTop: 18, height: 36 }}>
              <Sparkline points={D.sparkSeries(region.shortRu, 'grp', r.grp)}
                w={300} h={36} color={grpTone.dot}/>
            </div>
          )}
        </div>

        <div style={{ padding: '20px 22px', borderRight: '1px solid var(--outline-variant)' }}>
          <div className="eyebrow" style={{ marginBottom: 8 }}>Население</div>
          <div className="tabular" style={{ fontSize: 26, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.02em' }}>
            {D.fmtCount(r.populationCount)}
          </div>
          <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 6 }}>
            На 1.01.2026
          </div>
          <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 14, lineHeight: 1.5 }}>
            {region.districts} районов{region.cities && ` · ${region.cities} городов`}<br/>
            {region.mahallas} махаллей · {region.area}
          </div>
        </div>

        <div style={{ padding: '20px 22px', borderRight: '1px solid var(--outline-variant)' }}>
          <div className="eyebrow" style={{ marginBottom: 8, color: 'var(--tertiary)' }}>
            <Icon name="trending_up" size={12} filled style={{ marginRight: 4 }}/>
            Лидер роста
          </div>
          {tops[0] && (
            <>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--on-surface)' }}>
                {tops[0].m.shortRu}
              </div>
              <div className="tabular" style={{
                fontSize: 26, fontWeight: 800, lineHeight: 1, color: 'var(--tertiary)',
              }}>
                +{(tops[0].v - 100).toFixed(1)}
                <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontWeight: 500, marginLeft: 4 }}>
                  п.п.
                </span>
              </div>
              <div style={{ fontSize: 10, color: 'var(--on-surface-variant)', marginTop: 6 }}>
                к 2024 г. ({tops[0].v.toFixed(1)}%)
              </div>
            </>
          )}
        </div>

        <div style={{ padding: '20px 22px' }}>
          <div className="eyebrow" style={{ marginBottom: 8, color: bottoms[0]?.v >= 100 ? 'var(--on-surface-variant)' : 'var(--error)' }}>
            <Icon name="trending_down" size={12} filled style={{ marginRight: 4 }}/>
            Слабая динамика
          </div>
          {bottoms[0] && (
            <>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--on-surface)' }}>
                {bottoms[0].m.shortRu}
              </div>
              <div className="tabular" style={{
                fontSize: 26, fontWeight: 800, lineHeight: 1,
                color: bottoms[0].v >= 100 ? 'var(--on-surface-variant)' : 'var(--error)',
              }}>
                {(bottoms[0].v - 100 >= 0 ? '+' : '') + (bottoms[0].v - 100).toFixed(1)}
                <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontWeight: 500, marginLeft: 4 }}>
                  п.п.
                </span>
              </div>
              <div style={{ fontSize: 10, color: 'var(--on-surface-variant)', marginTop: 6 }}>
                к 2024 г. ({bottoms[0].v.toFixed(1)}%)
              </div>
            </>
          )}
        </div>
      </div>

      {/* Deviation chart */}
      <div style={{ padding: '22px 28px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
              Все показатели — отклонение от 2024 г.
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
              {period === '2026Q1' ? 'в % к январю — марту 2025 г.' : 'в % к январю — декабрю 2024 г.'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 18, alignItems: 'center', fontSize: 11 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--on-surface-variant)' }}>
              <span style={{ width: 12, height: 8, background: 'var(--tertiary)', borderRadius: 2 }}/>
              регион
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--on-surface-variant)' }}>
              <span style={{ width: 2, height: 14, background: 'var(--primary)' }}/>
              среднее по Узбекистану
            </div>
          </div>
        </div>

        <div>
          {bars.map(m => <MetricBar key={m.key} region={region} metric={m} max={maxAbs}/>)}
        </div>
      </div>

      {/* Rank cards */}
      <div style={{
        padding: '0 28px 22px',
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12,
      }}>
        {tops.map((x, i) => (
          <RankCard key={x.m.key} label={`№${i + 1} рост`} region={region} metric={x.m}/>
        ))}
        {bottoms.map((x, i) => (
          <RankCard key={x.m.key} label={`№${i + 1} замедление`} region={region} metric={x.m} isBottom/>
        ))}
      </div>

      {/* Footer */}
      <footer style={{
        padding: '14px 28px',
        background: 'var(--surface-container-low)',
        borderTop: '1px solid var(--outline-variant)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap',
      }}>
        <p style={{ margin: 0, fontSize: 11, color: 'var(--on-surface-variant)', fontStyle: 'italic' }}>
          Источник: <span style={{ color: 'var(--on-surface)', fontStyle: 'normal', fontWeight: 600 }}>{region.source}</span>
          <span style={{ margin: '0 8px' }}>·</span>
          Сравнение: stat.uz
        </p>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn"><Icon name="download" size={14}/> Экспорт</button>
          <button className="btn"><Icon name="share" size={14}/> Поделиться</button>
          <button className="btn btn-primary">
            <Icon name="analytics" size={14}/> Анализ районов
            <Icon name="arrow_forward" size={14}/>
          </button>
        </div>
      </footer>
    </section>
  );
}

window.PanelV3 = PanelV3;
