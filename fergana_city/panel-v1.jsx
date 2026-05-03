/* global React, Icon, Sparkline, DirectionArrow, getTone */
// V1 — Fergana CITY full-sector dashboard.
// Renders every verified data point we currently have for Farg'ona shahri,
// laid out as a single comprehensive panel. This is the BASELINE — feed
// this + data-adapter.js to Claude to generate alternative designs.

function PanelV1() {
  const D = window.FerganaCityData;
  const c = D.CITY;

  return (
    <section className="elev-1" style={{
      background: 'var(--surface-container-lowest)',
      borderRadius: 12,
      padding: '24px 28px',
    }}>
      {/* ── Identity strip ─────────────────────────────────────────────── */}
      <header style={{
        display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
        gap: 16, marginBottom: 20, flexWrap: 'wrap',
      }}>
        <div>
          <p style={{
            margin: 0, fontSize: 11, fontWeight: 800, letterSpacing: '0.15em',
            textTransform: 'uppercase', color: 'var(--primary)',
          }}>
            Региональный хаб · {c.region}
          </p>
          <h2 style={{
            margin: '6px 0 0', fontSize: 32, fontWeight: 900, letterSpacing: '-0.02em',
            color: 'var(--on-surface)',
          }}>
            {c.nameRu}
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--on-surface-variant)' }}>
            {D.fmtNum(c.population)} жителей · {c.area} км² · {c.density.toLocaleString('ru-RU')}/км² · {c.mahallas} махалли
          </p>
        </div>
        <span style={{
          background: 'var(--primary-fixed)', color: 'var(--primary)',
          fontSize: 10, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase',
          padding: '5px 11px', borderRadius: 999,
        }}>
          Источник: {c.source} · {c.period}
        </span>
      </header>

      {/* ── 6 SECTOR TILES ─────────────────────────────────────────────── */}
      <h3 style={sectionTitleStyle}>Экономическая активность · 2025</h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 14, marginBottom: 24,
      }}>
        {D.SECTORS.map(s => {
          const t = window.TONE_COLORS[D.tone(s.nominalYoY)];
          const delta = D.deltaYoY(s.nominalYoY);
          return (
            <article key={s.key} style={tileStyle}>
              <span className="icon-chip"><Icon name={s.icon} size={22} filled/></span>
              <p style={tileLabelStyle}>{s.labelRu}</p>
              <p className="tabular" style={tileValueStyle}>
                {D.fmtNum(Math.round(s.total2025))}
                <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--on-surface-variant)', marginLeft: 6 }}>
                  млрд сум
                </span>
              </p>
              {/* Two growth chips: city nominal vs region real */}
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
                <span className="tabular" style={{
                  fontSize: 11, fontWeight: 700, color: t.fg, background: t.bg,
                  padding: '3px 9px', borderRadius: 999,
                }}>
                  {(delta >= 0 ? '+' : '') + delta.toFixed(1)}% YoY
                </span>
                {s.regionRealYoY != null && (
                  <span style={{
                    fontSize: 10, fontWeight: 700, color: '#475569', background: '#F1F5F9',
                    padding: '3px 8px', borderRadius: 6, border: '1px solid #E2E8F0',
                  }}>
                    Область: {(s.regionRealYoY - 100 >= 0 ? '+' : '') + (s.regionRealYoY - 100).toFixed(1)}%
                  </span>
                )}
              </div>
              {/* 5-year sparkline */}
              <div style={{ width: '100%', height: 28, marginTop: 6 }}>
                <Sparkline points={s.history} w={200} h={28} color={t.dot} baseline={s.history[0]}/>
              </div>
              <p style={{ margin: 0, fontSize: 9, color: 'var(--on-surface-variant)', letterSpacing: '0.08em' }}>
                2021 → 2025 · ×{(s.total2025 / s.history[0]).toFixed(1)}
              </p>
            </article>
          );
        })}
      </div>

      {/* ── Population history + age structure ─────────────────────────── */}
      <h3 style={sectionTitleStyle}>Население · история и структура</h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 14, marginBottom: 24,
      }}>
        {/* Population history */}
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Численность населения</h4>
          <p style={cardSubStyle}>На 1 января, тыс. человек</p>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height: 120, marginTop: 10 }}>
            {D.POPULATION.history.map((v, i) => {
              const max = Math.max(...D.POPULATION.history);
              const min = Math.min(...D.POPULATION.history) * 0.95;
              const h = ((v - min) / (max - min)) * 100;
              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div className="tabular" style={{ fontSize: 9, fontWeight: 700, color: 'var(--on-surface)' }}>
                    {(v / 1000).toFixed(0)}k
                  </div>
                  <div style={{
                    width: '100%', height: `${h}%`, minHeight: 8,
                    background: 'linear-gradient(180deg, var(--primary), var(--primary-fixed))',
                    borderRadius: '4px 4px 0 0',
                  }}/>
                  <div className="tabular" style={{ fontSize: 9, color: 'var(--on-surface-variant)' }}>
                    {D.POPULATION.historyLabels[i]}
                  </div>
                </div>
              );
            })}
          </div>
          <p style={{ margin: '8px 0 0', fontSize: 10, color: 'var(--on-surface-variant)' }}>
            +{(((D.POPULATION.current - D.POPULATION.history[0]) / D.POPULATION.history[0]) * 100).toFixed(1)}% за 7 лет · 100% городское
          </p>
        </article>

        {/* Age structure */}
        <article style={{ ...cardStyle, gridColumn: 'span 2' }}>
          <h4 style={cardTitleStyle}>Возрастная структура · 2025</h4>
          <p style={cardSubStyle}>На 1 января, человек</p>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 120, marginTop: 10 }}>
            {Object.entries(D.AGE_GROUPS_2025).map(([label, count]) => {
              const max = Math.max(...Object.values(D.AGE_GROUPS_2025));
              const h = (count / max) * 100;
              return (
                <div key={label} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                  <div style={{
                    width: '100%', height: `${h}%`, minHeight: 6,
                    background: 'rgba(0, 84, 166, 0.85)',
                    borderRadius: '3px 3px 0 0',
                  }}/>
                  <div style={{ fontSize: 8, color: 'var(--on-surface-variant)', writingMode: 'horizontal-tb' }}>
                    {label}
                  </div>
                </div>
              );
            })}
          </div>
        </article>
      </div>

      {/* ── Vital stats + housing ──────────────────────────────────────── */}
      <h3 style={sectionTitleStyle}>Демография и жилая среда</h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: 14, marginBottom: 24,
      }}>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Рождаемость 2025</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: '#047857' }}>
            {D.fmtNum(D.VITAL_STATS.births2025)}
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
            ♂ {D.fmtNum(D.VITAL_STATS.birthsBoys2025)} · ♀ {D.fmtNum(D.VITAL_STATS.birthsGirls2025)}
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Смертность 2025</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: '#B91C1C' }}>
            {D.fmtNum(D.VITAL_STATS.deaths2025)}
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Естественный прирост 2025</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: 'var(--primary)' }}>
            +{D.fmtNum(D.VITAL_STATS.naturalIncrease2025)}
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Жилая площадь · 2024</h4>
          <p className="tabular" style={cardBigNumberStyle}>
            {D.HOUSING_SUPPLY.current2024} <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--on-surface-variant)' }}>м²/чел.</span>
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
            +{(D.HOUSING_SUPPLY.current2024 - D.HOUSING_SUPPLY.history[0]).toFixed(1)} м² за 5 лет
          </p>
        </article>
      </div>

      {/* ── Region context (foreign trade + transport) ────────────────── */}
      <h3 style={sectionTitleStyle}>
        Контекст области · {c.region}
        <span style={{
          marginLeft: 10, fontSize: 10, fontWeight: 800, letterSpacing: '0.08em',
          textTransform: 'uppercase', padding: '4px 9px', borderRadius: 999,
          background: '#FEF3C7', color: '#92400E', border: '1px solid #FCD34D',
        }}>
          Уровень области
        </span>
      </h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 14, marginBottom: 16,
      }}>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Экспорт</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: '#047857' }}>
            {D.fmtNum(D.REGION_FERGANA.foreignTrade2025.exportMlnUsd)} <span style={cardUnitStyle}>млн $</span>
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: '#047857', fontWeight: 700 }}>
            +{(D.REGION_FERGANA.foreignTrade2025.growthYoY.exportYoY - 100).toFixed(1)}% YoY
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Импорт</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: 'var(--on-surface)' }}>
            {D.fmtNum(D.REGION_FERGANA.foreignTrade2025.importMlnUsd)} <span style={cardUnitStyle}>млн $</span>
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)', fontWeight: 700 }}>
            +{(D.REGION_FERGANA.foreignTrade2025.growthYoY.importYoY - 100).toFixed(1)}% YoY
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Сальдо</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: '#B91C1C' }}>
            {D.fmtNum(D.REGION_FERGANA.foreignTrade2025.balanceMlnUsd)} <span style={cardUnitStyle}>млн $</span>
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>ВРП области · реальный рост</h4>
          <p className="tabular" style={{ ...cardBigNumberStyle, color: '#047857' }}>
            +{(D.REGION_FERGANA.realGrowth2025.grp - 100).toFixed(1)}%
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
            постоянные цены · YoY
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Пассажиры · авто</h4>
          <p className="tabular" style={cardBigNumberStyle}>
            {(D.REGION_FERGANA.autoTransport2025.passengersThs / 1000).toFixed(1)} <span style={cardUnitStyle}>млн</span>
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
            пасс. оборот {D.fmtNum(Math.round(D.REGION_FERGANA.autoTransport2025.passengerMlnPKm))} млн пасс-км
          </p>
        </article>
        <article style={cardStyle}>
          <h4 style={cardTitleStyle}>Грузы · авто</h4>
          <p className="tabular" style={cardBigNumberStyle}>
            {(D.REGION_FERGANA.autoTransport2025.cargoThsT / 1000).toFixed(1)} <span style={cardUnitStyle}>млн т</span>
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--on-surface-variant)' }}>
            грузооборот {D.fmtNum(Math.round(D.REGION_FERGANA.autoTransport2025.cargoMlnTKm))} млн т-км
          </p>
        </article>
      </div>

      {/* ── Source attribution ─────────────────────────────────────────── */}
      <p style={{
        margin: '20px 0 0', fontSize: 10, fontStyle: 'italic',
        color: 'var(--on-surface-variant)', textAlign: 'right',
      }}>
        Все значения подтверждены PDF-публикациями farstat.uz из локальной папки fergana/.
      </p>
    </section>
  );
}

// ── Inline style helpers ─────────────────────────────────────────────────
const sectionTitleStyle = {
  margin: '0 0 12px', fontSize: 12, fontWeight: 800, letterSpacing: '0.12em',
  textTransform: 'uppercase', color: 'var(--on-surface-variant)',
  display: 'flex', alignItems: 'center',
};
const tileStyle = {
  padding: '16px 16px',
  background: 'var(--surface-container-low)',
  borderRadius: 12,
  display: 'flex', flexDirection: 'column', gap: 6,
  position: 'relative',
};
const tileLabelStyle = {
  margin: 0, fontSize: 10, fontWeight: 800, lineHeight: 1.2,
  letterSpacing: '0.08em', textTransform: 'uppercase',
  color: 'var(--on-surface-variant)',
};
const tileValueStyle = {
  margin: 0, fontSize: 28, fontWeight: 900, lineHeight: 1, letterSpacing: '-0.02em',
  color: 'var(--on-surface)',
  display: 'inline-flex', alignItems: 'baseline',
};
const cardStyle = {
  padding: '16px 18px',
  background: 'var(--surface-container-low)',
  borderRadius: 12,
  display: 'flex', flexDirection: 'column',
};
const cardTitleStyle = {
  margin: 0, fontSize: 11, fontWeight: 800, letterSpacing: '0.08em',
  textTransform: 'uppercase', color: 'var(--on-surface-variant)',
};
const cardSubStyle = {
  margin: '2px 0 0', fontSize: 10, color: 'var(--on-surface-variant)',
};
const cardBigNumberStyle = {
  margin: '8px 0 0', fontSize: 26, fontWeight: 900, lineHeight: 1, letterSpacing: '-0.02em',
  color: 'var(--on-surface)',
};
const cardUnitStyle = {
  fontSize: 13, fontWeight: 700, color: 'var(--on-surface-variant)', marginLeft: 4,
};

window.PanelV1 = PanelV1;
