/**
 * Golden Mart data — Qoʻqon shahri.
 *
 * Keys match goldenMart/citySchema.js positional keys (s{section}_{index}).
 * Filled values come from verified rows in fergana/-folder PDFs (farstat.uz,
 * Jan-Dec 2025 preliminary). null = no source yet — detail view shows
 * "Нет данных" for those.
 *
 * Population, age, vital stats and sector totals are at 1 yanvar 2025 /
 * Jan-Dec 2025 unless noted.
 */

export const QOQON_GM = {
  // ── 1. Базовая информация (30 fields) ────────────────────────────
  s1_1:  'Qoʻqon',                  // Название
  s1_2:  'Город',                   // Тип объекта
  s1_3:  'Нет',                     // Админ. центр области
  s1_4:  60,                        // Площадь, км²
  s1_5:  56,                        // Махаллей
  s1_6:  313_597,                   // Население постоянное (1 янв 2025)
  s1_7:  null,                      // Мужчин — gender split not in fergana/
  s1_8:  null,                      // Женщин
  s1_9:  96_880,                    // 0–14 (sum of brackets 0-2 + 3-5 + 6-7 + 8-15)
  s1_10: 204_617,                   // 15–64 (sum 16-17 + 18-19 + ... + 60-69)
  s1_11: 12_100,                    // 65+ (sum 70-74 + 75-79 + 80-84 + 85+)
  s1_12: 22_968,                    // 0–2
  s1_13: 19_575,                    // 3–5
  s1_14: 10_777,                    // 6–7
  s1_15: 43_560,                    // 8–15
  s1_16: 10_769,                    // 16–17
  s1_17:  9_845,                    // 18–19
  s1_18: 21_293,                    // 20–24
  s1_19: 22_670,                    // 25–29
  s1_20: 26_460,                    // 30–34
  s1_21: 24_048,                    // 35–39
  s1_22: 39_225,                    // 40–49
  s1_23: 27_839,                    // 50–59
  s1_24: 22_468,                    // 60–69
  s1_25:  6_323,                    // 70–74
  s1_26:  3_533,                    // 75–79
  s1_27:  1_361,                    // 80–84
  s1_28:    883,                    // 85+
  s1_29: null,                      // Семей
  s1_30: null,                      // Домохозяйств

  // ── 2. Экономика – объёмы (7 fields, mlrd soʻm) ──────────────────
  s2_1: null,                       // ВТП (city-level GRP not published as a single line)
  s2_2: 9_410.4,                    // Промышленность
  s2_3: 6_371.1,                    // Услуги
  s2_4: 6_589.0,                    // Розничная торговля
  s2_5: 1_075.1,                    // Строительство
  s2_6:   382.1,                    // Сельское хозяйство
  s2_7: 4_111.2,                    // Инвестиции в основной капитал

  // ── 11. Здравоохранение ──────────────────────────────────────────
  // Indices below depend on schema; section 11 has 8 fields after extension.
  s11_7: 6_923,                     // Рождений (всего) 2025
  s11_8: 1_513,                     // Смертей (всего) 2025

  // ── 9. Бедность и социальная сфера — same vital figures duplicated here ──
  s9_5: 6_923,                      // Родившихся за год
  s9_6: 1_513,                      // Умерших за год

  // (every other key defaults to null — explicit `undefined` is treated
  // identically by the detail view's "Нет данных" check)
}
