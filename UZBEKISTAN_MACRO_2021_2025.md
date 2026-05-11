# Uzbekistan Macroeconomic Indicators 2021–2025

Source: official statistics (stat.uz), full-year totals.

All monetary values are in **трлн сум** (trillion soums), nominal.

| Indicator                        | 2021   | 2022    | 2023    | 2024    | 2025    |
|----------------------------------|-------:|--------:|--------:|--------:|--------:|
| GDP                              |  861.2 | 1 041.9 | 1 261.8 | 1 535.4 | 1 849.7 |
| Industrial production            |  451.6 |   551.1 |   655.8 |   885.8 | 1 101.1 |
| Investments in fixed capital     |  236.6 |   266.2 |   356.1 |   507.5 |   591.1 |
| Retail trade turnover            |  220*  |   319.3 |   326.2 |   403.4 |   482.4 |
| Market services                  |  389.4 |   509.6 |   664.8 |   840.1 | 1 050.3 |

## Population (млн чел.)

| 2021   | 2022   | 2023   | 2024*  | 2025   |
|-------:|-------:|-------:|-------:|-------:|
| 33.27  | 36.02  | 36.80  | 37.52  | 38.24  |

Sources: 2021–2023 from stat.uz (33 271 300 / 36 024 900 / 36 799 800).
2025 = 38 236 704, recorded "asof 1.01.2026" in `bff_frontend/backend/data/raqamlarda.json`.

\* **2024 is interpolated** — linear midpoint of 2023 and 2025 values
(36.7998 + 38.2367) / 2 = 37.5183. Replace with the official figure when
sourced; the data file flags it via `interpolatedYears: [2024]` and the
chart shows that point as a faded dot.

## Retail turnover 2021 — estimated

`Retail trade turnover` 2021 is marked with `*` because the official
full-year figure for 2021 is not published in this series. The 220 трлн
value is estimated from two partial-period publications:

| Partial period      | Reported value | Annualised full year |
|---------------------|---------------:|---------------------:|
| Jan – Aug 2021      |   143.4 трлн   |  215 (linear ×12/8)  |
| Q1 2021             |    46.7 трлн   |  222 (Q4-weighted)   |

Midpoint rounded to **220 трлн**. The data file tags it via
`interpolatedYears: [2021]` so it can be flagged in charts. Replace with
the official annual figure once sourced.

## Real growth (% YoY)

| Indicator                        | 2021  | 2022  | 2023   | 2024   | 2025   |
|----------------------------------|------:|------:|-------:|-------:|-------:|
| GDP, real growth                 | +8.2% | +6.1% |  +6.3% |  +6.7% |  +7.7% |
| Investments, real growth         | +2.9% | +0.2% | +23.4% | +31.3% | +10.5% |

## Notes

- "n/a" cells are gaps in the public series; downstream code does not interpolate, the bar chart simply renders a baseline tick.
- **2021 retail turnover, partial:** the only published figure is Jan-Aug 2021 = **143 419,3 млрд сум (143,4 трлн)**. Not used in the chart because the other cells are full-year totals — mixing scopes would distort the trajectory.
- **External trade (товарооборот) 2023:** $62,6 млрд (+23,9% vs 2022). This is a separate USD-denominated indicator, not part of the soum table above. If we want to surface it, it should live in its own series.
- Real growth is reported in constant prices, therefore not derivable from the nominal totals above.
- Other indicators visible in the live macro panel (agriculture, construction, cargo, passenger, retail %YoY) come from the quarterly `RAQAMLARDA` feed (`bff_frontend/backend/data/raqamlarda.json`) and are full-year 2025 % YoY change vs 2024.
