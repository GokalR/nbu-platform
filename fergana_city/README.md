# Fergana city — design canvas

Self-contained design canvas showing **all verified data** for г. Фергана
(Farg'ona shahri) sourced from the local `fergana/` PDF folder.

Drop this folder into Claude or any frontend designer to generate alternative
layouts of the same data — every value is verified and cited inside the data
adapter.

## Files

| File | Purpose |
|---|---|
| `Fergana City Panel.html` | Shell — open this in a browser |
| `data-adapter.js` | All verified data + helpers (read this to see what's available) |
| `panel-v1.jsx` | Baseline panel rendering every data point in one screen |
| `shared.jsx` | Atoms (Icon, Sparkline, DirectionArrow, getTone, TONE_COLORS) |
| `design-canvas.jsx` | Canvas chrome (DCSection, DCArtboard) |
| `tweaks-panel.jsx` | Tweaks UI (not used by V1, available for new variants) |
| `styles.css` | M3 design tokens (--primary, --surface-container-*, etc.) |

## What's in `data-adapter.js`

All values are sourced from PDFs in `../fergana/`:

- **CITY** — identity (335,100 people, 110 km², 74 mahalla)
- **SECTORS** — 6 sectors × {2025 total, 5y history 2021–2025, nominal YoY, region real YoY}
  - Industry, Services, Investments, Trade, Construction, Agriculture
- **POPULATION** — history 2019–2026 (8 years), 100% urban
- **AGE_GROUPS_2025** — 17 age brackets
- **VITAL_STATS** — births / deaths / natural increase 2021–2025
- **HOUSING_SUPPLY** — m²/resident 2020–2024 (25.4 in 2024)
- **REGION_FERGANA** — viloyat-level context (foreign trade, real growth, transport)

## Usage

1. Open `Fergana City Panel.html` in a browser to see the baseline.
2. To create alternative designs, copy `panel-v1.jsx` to `panel-v2.jsx` and
   re-arrange the same `window.FerganaCityData` fields differently.
3. Add a new `<DCArtboard>` in the HTML to view side-by-side.

## Source attribution

Each sector entry in `data-adapter.js` carries a `sourcePdf` field pointing
to the exact PDF in `fergana/` it was extracted from. Period: Jan-Dec 2025
preliminary (current prices for nominal totals; constant prices for
region real growth).
