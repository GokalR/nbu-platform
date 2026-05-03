/* global React, Icon, Sparkline, DirectionArrow, PeriodSwitcher, getTone */
// V2 — HIERARCHY. Hero KPIs on top, grouped metric table on the left,
// vs-Узбекистан comparison rail on the right. Match NBU/M3 surface tokens.

const METRIC_DEFS = [
  { key: 'grp',          icon: 'show_chart',     labelRu: 'Валовой региональный продукт',  shortRu: 'ВРП',         group: 'production' },
  { key: 'industry',     icon: 'factory',        labelRu: 'Промышленность',                shortRu: 'Промышленность', group: 'production' },
  { key: 'agriculture',  icon: 'agriculture',    labelRu: 'Сельское, лесное и рыбное хозяйство', shortRu: 'Сельское хоз-во', group: 'production' },
  { key: 'investment',   icon: 'savings',        labelRu: 'Инвестиции в осн. капитал',     shortRu: 'Инвестиции',   group: 'capital' },
  { key: 'construction', icon: 'construction',   labelRu: 'Строительные работы',           shortRu: 'Стройка',      group: 'capital' },
  { key: 'freight',      icon: 'local_shipping', labelRu: 'Грузооборот',                   shortRu: 'Грузооборот',  group: 'trade' },
  { key: 'passenger',    icon: 'directions_bus', labelRu: 'Пассажирооборот',               shortRu: 'Пассажиры',    group: 'trade' },
  { key: 'retail',       icon: 'storefront',     labelRu: 'Розничный товарооборот',        shortRu: 'Розница',      group: 'trade' },
  { key: 'services',     icon: 'handyman',       labelRu: 'Услуги',                        shortRu: 'Услуги',       group: 'trade' },
];

function HeroStat({ label, valueText, sub, tone, icon, big = false, accent = false }) {
  return (
    <div style={{
      padding: big ? '20px 22px' : '18px 20px',
      background: accent ? 'var(--primary)' : 'var(--surface-container-low)',
      color: accent ? 'var(--on-primary)' : 'var(--on-surface)',
      borderRadius: 12,
      display: 'flex', flexDirection: 'column', gap: 8,
      minHeight: big ? 132 : 110,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span className="eyebrow" style={{ color: accent ? 'rgba(255,255,255,0.85)' : 'var(--on-surface-variant)' }}>{label}</span>
        {icon && (
          <span className="icon-chip-sm icon-chip" style={{
            background: accent ? 'rgba(255,255,255,0.15)' : 'var(--primary-fixed)',
            color: accent ? 'var(--on-primary)' : 'var(--primary)',
          }}>
            <Icon name={icon} size={18} filled/>
          </span>
        )}
      </div>
      <div className="tabular" style={{
        fontSize: big ? 44 : 30, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.02em',
      }}>
        {valueText}
      </div>
      {sub && (
        <div style={{
          fontSize: 11, color: accent ? 'rgba(255,255,255,0.85)' : 'var(--on-surface-variant)',
          fontWeight: 500,
        }}>
          {sub}
        </div>
      )}
    </div>
  );
}

function TableRow({ region, metric, period, expanded }) {
  const D = window.RegionData;
  const v = region.raqamlarda[metric.key];
  const delta = D.pctDelta(v);
  const vsNat = D.deltaVsNational(v, metric.key);
  const tone = window.TONE_COLORS[getTone(v)];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '32px 1fr 80px 100px 80px',
      gap: 14, alignItems: 'center',
      padding: '12px 14px',
      borderRadius: 10,
      transition: 'background 0.15s ease',
      cursor: 'pointer',
    }}
    onMouseEnter={e => e.currentTarget.style.background = 'var(--surface-container-low)'}
    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
      <span className="icon-chip-sm icon-chip" style={{ width: 32, height: 32 }}>
        <Icon name={metric.icon} size={16} filled/>
      </span>
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface)', lineHeight: 1.25 }}>{metric.labelRu}</div>
        <div style={{ fontSize: 10, color: 'var(--on-surface-variant)', marginTop: 2 }}>
          {period === '2026Q1' ? 'в % к I кв. 2025' : 'в % к янв.–дек. 2024'}
        </div>
      </div>
      <div className="tabular" style={{
        fontSize: 17, fontWeight: 800, textAlign: 'right',
        color: v == null ? 'var(--on-surface-variant)' : 'var(--on-surface)',
      }}>
        {v != null ? v.toFixed(1) + '%' : '—'}
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 6 }}>
        {delta != null && (
          <span className="tabular" style={{
            fontSize: 10, fontWeight: 700, color: tone.fg, background: tone.bg,
            padding: '3px 8px', borderRadius: 999,
          }}>
            {delta > 0 ? '+' : ''}{delta.toFixed(1)} п.п.
          </span>
        )}
        {vsNat != null && (
          <span className="tabular" style={{
            fontSize: 10, fontWeight: 600,
            color: vsNat >= 0 ? 'var(--tertiary)' : 'var(--error)',
          }}>
            {vsNat >= 0 ? '↑' : '↓'}{Math.abs(vsNat).toFixed(1)}
          </span>
        )}
      </div>
      <div style={{ width: 70, height: 22 }}>
        <Sparkline points={D.sparkSeries(region.shortRu, metric.key, v)} w={70} h={22} color={tone.dot}/>
      </div>
    </div>
  );
}

function GroupBlock({ title, count, metrics, region, period }) {
  return (
    <div style={{ marginBottom: 4 }}>
      <header style={{ padding: '12px 14px 6px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
          color: 'var(--primary)', background: 'var(--primary-fixed)',
          padding: '3px 8px', borderRadius: 999,
        }}>
          {count}
        </span>
        <span className="eyebrow" style={{ color: 'var(--on-surface)' }}>{title}</span>
        <div style={{ flex: 1, height: 1, background: 'var(--outline-variant)', opacity: 0.5 }}/>
      </header>
      {metrics.map(m => <TableRow key={m.key} region={region} metric={m} period={period}/>)}
    </div>
  );
}

function NationalCompareRail({ region }) {
  const D = window.RegionData;
  const r = region.raqamlarda;
  const items = METRIC_DEFS.filter(m => r[m.key] != null && D.NATIONAL.raqamlarda[m.key] != null);

  return (
    <aside style={{
      background: 'var(--primary)',
      color: 'var(--on-primary)',
      borderRadius: 12,
      padding: '20px 22px',
      height: '100%',
      display: 'flex', flexDirection: 'column', gap: 14,
    }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <Icon name="compare_arrows" size={18} filled/>
          <span className="eyebrow" style={{ color: 'rgba(255,255,255,0.9)' }}>Сравнение с национальным</span>
        </div>
        <h4 style={{ margin: 0, fontSize: 16, fontWeight: 800, letterSpacing: '-0.01em' }}>
          Регион vs Узбекистан
        </h4>
        <p style={{ margin: '4px 0 0', fontSize: 11, color: 'rgba(255,255,255,0.8)' }}>
          Отклонение в п.п. от среднего по стране
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {items.map(m => {
          const v = r[m.key];
          const nat = D.NATIONAL.raqamlarda[m.key];
          const diff = v - nat;
          const range = 12;
          const pct = Math.min(Math.abs(diff) / range, 1);
          const positive = diff >= 0;

          return (
            <div key={m.key}>
              <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 5 }}>
                <span style={{ fontSize: 12, fontWeight: 500 }}>{m.shortRu}</span>
                <span className="tabular" style={{
                  fontSize: 11, fontWeight: 700,
                  color: positive ? '#A7E0AB' : '#F2BBB6',
                }}>
                  {positive ? '+' : ''}{diff.toFixed(1)}
                </span>
              </div>
              <div style={{ position: 'relative', height: 4, background: 'rgba(255,255,255,0.15)', borderRadius: 2 }}>
                <div style={{
                  position: 'absolute', left: '50%', top: -2, bottom: -2, width: 1.5,
                  background: 'rgba(255,255,255,0.5)',
                }}/>
                <div style={{
                  position: 'absolute',
                  ...(positive
                    ? { left: '50%', width: `${pct * 50}%` }
                    : { right: '50%', width: `${pct * 50}%` }),
                  top: 0, bottom: 0,
                  background: positive ? '#A7E0AB' : '#F2BBB6',
                  borderRadius: 2,
                }}/>
              </div>
              <div className="tabular" style={{
                display: 'flex', justifyContent: 'space-between',
                fontSize: 9, color: 'rgba(255,255,255,0.65)', marginTop: 3,
              }}>
                <span>Узб. {nat.toFixed(1)}</span>
                <span>Регион {v.toFixed(1)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

function PanelV2({ region, period }) {
  const D = window.RegionData;
  const r = region.raqamlarda;

  // Ranked best/worst (excl GRP)
  const ranked = METRIC_DEFS.filter(m => m.key !== 'grp')
    .map(m => ({ m, v: r[m.key] }))
    .filter(x => x.v != null)
    .sort((a, b) => b.v - a.v);
  const best = ranked[0];

  const groups = [
    { id: 'production', title: 'Производство',          keys: ['grp', 'industry', 'agriculture'] },
    { id: 'capital',    title: 'Капитал и стройка',     keys: ['investment', 'construction'] },
    { id: 'trade',      title: 'Торговля и транспорт',  keys: ['freight', 'passenger', 'retail', 'services'] },
  ];

  return (
    <section className="elev-1" style={{
      background: 'var(--surface-container-lowest)',
      borderRadius: 12,
      overflow: 'hidden',
    }}>
      {/* Title row */}
      <header style={{
        padding: '20px 28px',
        borderBottom: '1px solid var(--outline-variant)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Icon name="location_on" size={22} filled style={{ color: 'var(--primary)' }}/>
          <div>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
              {region.nameRu}
            </h2>
            <p style={{ margin: '2px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
              · Районов: {region.districts}
              {region.cities && <> · Городов: {region.cities}</>}
              · Махаллей: {region.mahallas} · Площадь: {region.area}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className="badge badge-info">
            <Icon name="check_circle" size={11} filled/>
            данные подтверждены
          </span>
          <PeriodSwitcher value={period} onChange={() => {}}/>
        </div>
      </header>

      {/* Hero KPI strip */}
      <div style={{
        padding: '20px 28px 16px',
        display: 'grid',
        gridTemplateColumns: '1.4fr 1fr 1fr 1fr',
        gap: 12,
      }}>
        <HeroStat
          big accent
          label="Валовой региональный продукт"
          icon="show_chart"
          valueText={r.grp != null ? r.grp.toFixed(1) + '%' : '—'}
          sub={r.grp != null
            ? `▲ +${(r.grp - 100).toFixed(1)} п.п. к 2024 · ${(r.grp - D.NATIONAL.raqamlarda.grp >= 0 ? '+' : '')}${(r.grp - D.NATIONAL.raqamlarda.grp).toFixed(1)} над средним по Узб.`
            : 'нет данных'}
        />
        <HeroStat
          label={`Лидер: ${best ? best.m.shortRu : '—'}`}
          icon={best ? best.m.icon : 'star'}
          valueText={best ? best.v.toFixed(1) + '%' : '—'}
          sub={best ? `+${(best.v - 100).toFixed(1)} п.п. к пред. году` : ''}
        />
        <HeroStat
          label="Инвестиции"
          icon="savings"
          valueText={r.investment != null ? r.investment.toFixed(1) + '%' : '—'}
          sub={r.investment != null
            ? `${r.investment >= 100 ? '▲' : '▼'} ${(r.investment - 100 >= 0 ? '+' : '') + (r.investment - 100).toFixed(1)} п.п.`
            : 'нет данных'}
        />
        <HeroStat
          label="Население"
          icon="groups"
          valueText={D.fmtCount(r.populationCount)}
          sub="на 1.01.2026"
        />
      </div>

      {/* Body: table + rail */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1.5fr 1fr',
        padding: '4px 16px 20px 16px',
        gap: 16,
      }}>
        <div style={{ padding: '4px 12px' }}>
          {groups.map(g => (
            <GroupBlock key={g.id}
              title={g.title}
              count={String(g.keys.length).padStart(2, '0')}
              metrics={METRIC_DEFS.filter(m => g.keys.includes(m.key))}
              region={region} period={period}
            />
          ))}
        </div>
        <NationalCompareRail region={region}/>
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
          Сравнение со средним по Узбекистану — stat.uz
        </p>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn"><Icon name="download" size={14}/> Экспорт</button>
          <button className="btn btn-primary"><Icon name="analytics" size={14}/> Анализ районов</button>
        </div>
      </footer>
    </section>
  );
}

window.PanelV2 = PanelV2;
