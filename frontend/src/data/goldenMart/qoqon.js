/**
 * Golden Mart data — Qoʻqon shahri.
 *
 * Keys match goldenMart/citySchema.js. `null` means we don't have a
 * verified value yet — the detail view shows "Нет данных" for those.
 *
 * Verified values come from farstat.uz district-breakdown PDFs in the
 * fergana/ folder (Jan-Dec 2025 preliminary, Qoʻqon shahri rows).
 * Fields without an obvious source are left null on purpose — fill
 * once a city-level publication lands.
 */

export const QOQON_GM = {
  // 1. Базовая информация
  name: 'Qoʻqon',
  type: 'Город',
  isAdminCenter: 'Нет',                  // Fergana shahri is the viloyat center
  area: 60,
  mahallas: 56,
  population: 319_600,                   // 1 yanvar 2026
  populationMen: null,
  populationWomen: null,
  pop0_14:  96_649,                      // 0-2 + 3-5 + 6-7 + 8-15
  pop15_64: 174_004,                     // 16-17 + 18-19 + 20-24 + ... + 60-69 (approx)
  pop65plus: 12_100,                     // 70-74 + 75-79 + 80-84 + 85+
  families: null,
  households: null,

  // 2. Экономика – объёмы (2025, mlrd soʻm)
  grp:          null,                    // city-level GRP not published as a single line
  industry:     9_410.4,
  services:     6_371.1,
  trade:        6_589.0,
  construction: 1_075.1,
  agriculture:    382.1,
  investments:  4_111.2,

  // 3. Бюджет — city-level not in fergana/ folder
  budgetRevenue: null, budgetTax: null, budgetNonTax: null,
  budgetTransfers: null, budgetExpense: null, budgetSocial: null,
  budgetInfra: null, budgetAdmin: null, budgetBalance: null,

  // 4. Внешняя торговля — only viloyat-level published
  foreignTurnover: null, foreignExport: null, foreignImport: null, foreignBalance: null,

  // 5. Торговые партнёры — viloyat-level only
  exportCountry1: null, exportCountry1Volume: null,
  exportCountry2: null, exportCountry2Volume: null,
  exportCountry3: null, exportCountry3Volume: null,
  importCountry1: null, importCountry1Volume: null,
  importCountry2: null, importCountry2Volume: null,
  importCountry3: null, importCountry3Volume: null,

  // 6. Инвестиции по источникам — city-level breakdown not published
  invSrcEnterprise: null, invSrcForeign: null, invSrcGov: null,
  invSrcBank: null, invSrcPopulation: null, invSrcReconstruction: null,

  // 7. Предпринимательство — city-level not in fergana/ folder
  enterprisesActive: null, enterprisesOoo: null, enterprisesIp: null,
  enterprisesFarm: null, enterprisesOpened: null, enterprisesClosed: null,
  selfEmployed: null,

  // 8. Рынок труда — city-level not in fergana/ folder
  laborActive: null, laborEmployed: null, laborFormal: null,
  laborInformal: null, laborAbroad: null, laborUnemployed: null,
  unemploymentRate: null, avgSalary: null,

  // 9. Бедность и социальная сфера
  socRegistryFamilies: null, socRegistryPct: null,
  socBeneficiaries: null, povertyRate: null,

  // 10. Образование
  schools: null, pupils: null, teachers: null,
  kindergartens: null, preschoolCoverage: null,
  colleges: null, universities: null,

  // 11. Здравоохранение — derive rates from population + verified vital stats
  hospitals: null, clinics: null, hospitalBeds: null,
  doctors: null, nurses: null,
  // Births 6923 / pop 319600 × 1000 = 21.66 ‰
  birthRate:        21.7,
  deathRate:         4.7,                // 1513 / 319600 × 1000
  naturalIncrease: 5_410,                // 6923 − 1513

  // 12. Банковский сектор — city-level not in fergana/ folder
  creditTotal: null, creditSmb: null, creditRetail: null,
  deposits: null, nplRate: null, bankCards: null, posTerminals: null,

  // 13. Туризм — city-level not in fergana/ folder
  tourists: null, touristsForeign: null, hotels: null, heritageSites: null,

  // 14. Жильё — city-level housing supply not in fergana/ for Qoqon (only Fergana)
  housingStock: null, housingPerPerson: null,
  housingNew: null, housingQueue: null,

  // 15. Инфраструктура – подключения и сети — not verified at city level
  infraWater: null, infraSewage: null, infraGas: null,
  infraElectricity: null, infraHeating: null,

  // 16. Дороги — city-level not in fergana/ folder
  roadsTotal: null, roadsAsphalt: null, roadsGravel: null, roadsEarth: null,

  // 17. Транспорт — viloyat-level only
  transportPassengers: null, transportCargo: null,
  busRoutes: null, vehicleFleet: null,

  // 18. Экология — not in fergana/ folder
  emissions: null, greenAreas: null, parks: null,

  // 19. Цифровизация — not in fergana/ folder
  internetCoverage: null, coverage4G: null,
  eGovServices: null, cashlessShare: null,

  // 20. Топ-5 махаллей — city-level credit-activity data not published
  topMahalla1: null, topMahalla1Loans: null,
  topMahalla2: null, topMahalla2Loans: null,
  topMahalla3: null, topMahalla3Loans: null,
  topMahalla4: null, topMahalla4Loans: null,
  topMahalla5: null, topMahalla5Loans: null,

  // 21. Критические проблемы — not in fergana/ folder
  problem1: null, problem1Cost: null, problem1Priority: null,
  problem2: null, problem2Cost: null, problem2Priority: null,
  problem3: null, problem3Cost: null, problem3Priority: null,
}
