/**
 * Golden Mart — City/Tuman schema (21 sections).
 *
 * Mirrors goldenmarts/GM_city.md (sourced from
 * goldenmarts/golden_mart_city.xlsx, sheet "Города и туманы").
 * The MD is the human-readable spec; this file is the JS form the
 * detail view consumes. Keep them in sync — when admins edit the
 * Excel, regenerate the MD via goldenmarts/_to_md.py and update
 * this file's structure to match.
 *
 * Each attribute is { label, unit, key }. `key` is the field name in
 * the per-city data object (see goldenMart/qoqon.js).
 */

export const CITY_SECTIONS = [
  {
    n: 1, title: 'Базовая информация', icon: 'badge',
    attrs: [
      { label: 'Название',                       unit: 'текст',  key: 'name' },
      { label: 'Тип объекта (город / туман)',    unit: 'текст',  key: 'type' },
      { label: 'Админ. центр области',           unit: 'да/нет', key: 'isAdminCenter' },
      { label: 'Площадь',                        unit: 'км²',    key: 'area' },
      { label: 'Махаллей',                       unit: 'шт.',    key: 'mahallas' },
      { label: 'Население постоянное',           unit: 'чел.',   key: 'population' },
      { label: 'Мужчин',                         unit: 'чел.',   key: 'populationMen' },
      { label: 'Женщин',                         unit: 'чел.',   key: 'populationWomen' },
      { label: 'Население 0–14 лет',             unit: 'чел.',   key: 'pop0_14' },
      { label: 'Население 15–64 лет',            unit: 'чел.',   key: 'pop15_64' },
      { label: 'Население 65+ лет',              unit: 'чел.',   key: 'pop65plus' },
      { label: 'Семей',                          unit: 'тыс.',   key: 'families' },
      { label: 'Домохозяйств',                   unit: 'тыс.',   key: 'households' },
    ],
  },
  {
    n: 2, title: 'Экономика – объёмы', icon: 'finance',
    attrs: [
      { label: 'ВТП (валовой территориальный продукт)', unit: 'млрд сум', key: 'grp' },
      { label: 'Промышленность – объём',                unit: 'млрд сум', key: 'industry' },
      { label: 'Услуги – объём',                        unit: 'млрд сум', key: 'services' },
      { label: 'Розничная торговля – объём',            unit: 'млрд сум', key: 'trade' },
      { label: 'Строительство – объём',                 unit: 'млрд сум', key: 'construction' },
      { label: 'Сельское хозяйство – объём',            unit: 'млрд сум', key: 'agriculture' },
      { label: 'Инвестиции в основной капитал',         unit: 'млрд сум', key: 'investments' },
    ],
  },
  {
    n: 3, title: 'Бюджет', icon: 'account_balance',
    attrs: [
      { label: 'Доходы бюджета – всего',                unit: 'млрд сум', key: 'budgetRevenue' },
      { label: 'Налоговые поступления',                 unit: 'млрд сум', key: 'budgetTax' },
      { label: 'Неналоговые доходы',                    unit: 'млрд сум', key: 'budgetNonTax' },
      { label: 'Трансферты из вышестоящ. бюджета',      unit: 'млрд сум', key: 'budgetTransfers' },
      { label: 'Расходы бюджета – всего',               unit: 'млрд сум', key: 'budgetExpense' },
      { label: 'Социальная сфера',                      unit: 'млрд сум', key: 'budgetSocial' },
      { label: 'Инфраструктура и экономика',            unit: 'млрд сум', key: 'budgetInfra' },
      { label: 'Управление и прочее',                   unit: 'млрд сум', key: 'budgetAdmin' },
      { label: 'Дефицит / Профицит',                    unit: 'млрд сум', key: 'budgetBalance' },
    ],
  },
  {
    n: 4, title: 'Внешняя торговля', icon: 'public',
    attrs: [
      { label: 'Товарооборот',           unit: 'млрд сум', key: 'foreignTurnover' },
      { label: 'Экспорт',                unit: 'млрд сум', key: 'foreignExport' },
      { label: 'Импорт',                 unit: 'млрд сум', key: 'foreignImport' },
      { label: 'Сальдо торговли',        unit: 'млрд сум', key: 'foreignBalance' },
    ],
  },
  {
    n: 5, title: 'Основные торговые партнёры', icon: 'flag',
    attrs: [
      { label: 'Экспорт – страна 1: название', unit: 'текст',     key: 'exportCountry1' },
      { label: 'Экспорт – страна 1: объём',    unit: 'млрд сум',  key: 'exportCountry1Volume' },
      { label: 'Экспорт – страна 2: название', unit: 'текст',     key: 'exportCountry2' },
      { label: 'Экспорт – страна 2: объём',    unit: 'млрд сум',  key: 'exportCountry2Volume' },
      { label: 'Экспорт – страна 3: название', unit: 'текст',     key: 'exportCountry3' },
      { label: 'Экспорт – страна 3: объём',    unit: 'млрд сум',  key: 'exportCountry3Volume' },
      { label: 'Импорт – страна 1: название',  unit: 'текст',     key: 'importCountry1' },
      { label: 'Импорт – страна 1: объём',     unit: 'млрд сум',  key: 'importCountry1Volume' },
      { label: 'Импорт – страна 2: название',  unit: 'текст',     key: 'importCountry2' },
      { label: 'Импорт – страна 2: объём',     unit: 'млрд сум',  key: 'importCountry2Volume' },
      { label: 'Импорт – страна 3: название',  unit: 'текст',     key: 'importCountry3' },
      { label: 'Импорт – страна 3: объём',     unit: 'млрд сум',  key: 'importCountry3Volume' },
    ],
  },
  {
    n: 6, title: 'Инвестиции по источникам', icon: 'savings',
    attrs: [
      { label: 'Собственные средства предприятий', unit: 'млрд сум', key: 'invSrcEnterprise' },
      { label: 'Иностранные инвестиции',           unit: 'млрд сум', key: 'invSrcForeign' },
      { label: 'Госбюджет',                        unit: 'млрд сум', key: 'invSrcGov' },
      { label: 'Банковские кредиты',               unit: 'млрд сум', key: 'invSrcBank' },
      { label: 'Средства населения',               unit: 'млрд сум', key: 'invSrcPopulation' },
      { label: 'Фонд реконструкции',               unit: 'млрд сум', key: 'invSrcReconstruction' },
    ],
  },
  {
    n: 7, title: 'Предпринимательство', icon: 'storefront',
    attrs: [
      { label: 'Активных субъектов – всего', unit: 'шт.', key: 'enterprisesActive' },
      { label: 'ООО',                        unit: 'шт.', key: 'enterprisesOoo' },
      { label: 'ИП (ЯТТ)',                   unit: 'шт.', key: 'enterprisesIp' },
      { label: 'Фермерские хозяйства',       unit: 'шт.', key: 'enterprisesFarm' },
      { label: 'Открыто за год',             unit: 'шт.', key: 'enterprisesOpened' },
      { label: 'Закрыто за год',             unit: 'шт.', key: 'enterprisesClosed' },
      { label: 'Самозанятые',                unit: 'тыс.', key: 'selfEmployed' },
    ],
  },
  {
    n: 8, title: 'Рынок труда', icon: 'work',
    attrs: [
      { label: 'Экономически активное население', unit: 'тыс. чел.', key: 'laborActive' },
      { label: 'Занятые – всего',                 unit: 'тыс. чел.', key: 'laborEmployed' },
      { label: 'Формальный сектор',               unit: 'тыс. чел.', key: 'laborFormal' },
      { label: 'Неформальный сектор',             unit: 'тыс. чел.', key: 'laborInformal' },
      { label: 'Трудовая миграция за рубежом',    unit: 'тыс. чел.', key: 'laborAbroad' },
      { label: 'Безработные',                     unit: 'тыс. чел.', key: 'laborUnemployed' },
      { label: 'Уровень безработицы',             unit: '%',         key: 'unemploymentRate' },
      { label: 'Средняя зарплата',                unit: 'тыс. сум',  key: 'avgSalary' },
    ],
  },
  {
    n: 9, title: 'Бедность и социальная сфера', icon: 'volunteer_activism',
    attrs: [
      { label: 'Семей в социальном реестре',  unit: 'шт.',  key: 'socRegistryFamilies' },
      { label: 'Доля семей в реестре',        unit: '%',    key: 'socRegistryPct' },
      { label: 'Получателей пособий',         unit: 'тыс.', key: 'socBeneficiaries' },
      { label: 'Уровень бедности',            unit: '%',    key: 'povertyRate' },
    ],
  },
  {
    n: 10, title: 'Образование', icon: 'school',
    attrs: [
      { label: 'Школ',                       unit: 'шт.', key: 'schools' },
      { label: 'Учеников',                   unit: 'тыс.', key: 'pupils' },
      { label: 'Учителей',                   unit: 'тыс.', key: 'teachers' },
      { label: 'Детских садов',              unit: 'шт.', key: 'kindergartens' },
      { label: 'Охват дошкольным',           unit: '%',   key: 'preschoolCoverage' },
      { label: 'Колледжей и техникумов',     unit: 'шт.', key: 'colleges' },
      { label: 'Высших учебных заведений',   unit: 'шт.', key: 'universities' },
    ],
  },
  {
    n: 11, title: 'Здравоохранение', icon: 'local_hospital',
    attrs: [
      { label: 'Больниц',                    unit: 'шт.',  key: 'hospitals' },
      { label: 'Поликлиник / СВП',           unit: 'шт.',  key: 'clinics' },
      { label: 'Коек',                       unit: 'шт.',  key: 'hospitalBeds' },
      { label: 'Врачей',                     unit: 'тыс.', key: 'doctors' },
      { label: 'Среднего медперсонала',      unit: 'тыс.', key: 'nurses' },
      { label: 'Рождаемость',                unit: 'на 1000', key: 'birthRate' },
      { label: 'Смертность',                 unit: 'на 1000', key: 'deathRate' },
      { label: 'Естественный прирост',       unit: 'чел.', key: 'naturalIncrease' },
    ],
  },
  {
    n: 12, title: 'Банковский сектор', icon: 'account_balance_wallet',
    attrs: [
      { label: 'Кредитный портфель – всего', unit: 'млрд сум', key: 'creditTotal' },
      { label: 'Кредиты МСБ',                unit: 'млрд сум', key: 'creditSmb' },
      { label: 'Розничные кредиты',          unit: 'млрд сум', key: 'creditRetail' },
      { label: 'Депозиты',                   unit: 'млрд сум', key: 'deposits' },
      { label: 'Уровень NPL',                unit: '%',        key: 'nplRate' },
      { label: 'Банковские карты',           unit: 'тыс.',     key: 'bankCards' },
      { label: 'POS-терминалов',             unit: 'шт.',      key: 'posTerminals' },
    ],
  },
  {
    n: 13, title: 'Туризм', icon: 'travel_explore',
    attrs: [
      { label: 'Туристов – всего',           unit: 'тыс.', key: 'tourists' },
      { label: 'Иностранных туристов',       unit: 'тыс.', key: 'touristsForeign' },
      { label: 'Гостиниц',                   unit: 'шт.',  key: 'hotels' },
      { label: 'Объектов наследия',          unit: 'шт.',  key: 'heritageSites' },
    ],
  },
  {
    n: 14, title: 'Жильё', icon: 'home',
    attrs: [
      { label: 'Жилищный фонд',              unit: 'тыс. м²', key: 'housingStock' },
      { label: 'На 1 жителя',                unit: 'м²',      key: 'housingPerPerson' },
      { label: 'Введено в эксплуатацию',     unit: 'тыс. м²', key: 'housingNew' },
      { label: 'Очередь на жильё',           unit: 'семей',   key: 'housingQueue' },
    ],
  },
  {
    n: 15, title: 'Инфраструктура – подключения и сети', icon: 'hub',
    attrs: [
      { label: 'Покрытие водопроводом',      unit: '%', key: 'infraWater' },
      { label: 'Покрытие канализацией',      unit: '%', key: 'infraSewage' },
      { label: 'Покрытие газом',             unit: '%', key: 'infraGas' },
      { label: 'Электрификация',             unit: '%', key: 'infraElectricity' },
      { label: 'Централизованное теплоснабжение', unit: '%', key: 'infraHeating' },
    ],
  },
  {
    n: 16, title: 'Дороги', icon: 'route',
    attrs: [
      { label: 'Общая протяжённость',        unit: 'км', key: 'roadsTotal' },
      { label: 'С твёрдым покрытием',        unit: 'км', key: 'roadsAsphalt' },
      { label: 'Гравийных',                  unit: 'км', key: 'roadsGravel' },
      { label: 'Грунтовых',                  unit: 'км', key: 'roadsEarth' },
    ],
  },
  {
    n: 17, title: 'Транспорт', icon: 'directions_bus',
    attrs: [
      { label: 'Перевезено пассажиров',      unit: 'млн', key: 'transportPassengers' },
      { label: 'Перевезено грузов',          unit: 'тыс. т', key: 'transportCargo' },
      { label: 'Автобусных маршрутов',       unit: 'шт.', key: 'busRoutes' },
      { label: 'Парк автотранспорта',        unit: 'тыс.', key: 'vehicleFleet' },
    ],
  },
  {
    n: 18, title: 'Экология', icon: 'park',
    attrs: [
      { label: 'Выбросы в атмосферу',        unit: 'тыс. т', key: 'emissions' },
      { label: 'Зелёных насаждений',         unit: 'га',     key: 'greenAreas' },
      { label: 'Площадь парков',             unit: 'га',     key: 'parks' },
    ],
  },
  {
    n: 19, title: 'Цифровизация', icon: 'devices',
    attrs: [
      { label: 'Покрытие интернетом',        unit: '%',   key: 'internetCoverage' },
      { label: 'Покрытие 4G',                unit: '%',   key: 'coverage4G' },
      { label: 'Цифровых госуслуг',          unit: 'шт.', key: 'eGovServices' },
      { label: 'Доля безналичных платежей',  unit: '%',   key: 'cashlessShare' },
    ],
  },
  {
    n: 20, title: 'Топ-5 махаллей по кредитной активности', icon: 'leaderboard',
    isList: true,
    attrs: [
      { label: 'Махалля 1: название', unit: 'текст',    key: 'topMahalla1' },
      { label: 'Махалля 1: кредиты',  unit: 'млн сум',  key: 'topMahalla1Loans' },
      { label: 'Махалля 2: название', unit: 'текст',    key: 'topMahalla2' },
      { label: 'Махалля 2: кредиты',  unit: 'млн сум',  key: 'topMahalla2Loans' },
      { label: 'Махалля 3: название', unit: 'текст',    key: 'topMahalla3' },
      { label: 'Махалля 3: кредиты',  unit: 'млн сум',  key: 'topMahalla3Loans' },
      { label: 'Махалля 4: название', unit: 'текст',    key: 'topMahalla4' },
      { label: 'Махалля 4: кредиты',  unit: 'млн сум',  key: 'topMahalla4Loans' },
      { label: 'Махалля 5: название', unit: 'текст',    key: 'topMahalla5' },
      { label: 'Махалля 5: кредиты',  unit: 'млн сум',  key: 'topMahalla5Loans' },
    ],
  },
  {
    n: 21, title: 'Критические проблемы инфраструктуры', icon: 'warning',
    attrs: [
      { label: 'Проблема 1: описание',     unit: 'текст',    key: 'problem1' },
      { label: 'Проблема 1: оценка',       unit: 'млрд сум', key: 'problem1Cost' },
      { label: 'Проблема 1: приоритет',    unit: 'высокий/средний/низкий', key: 'problem1Priority' },
      { label: 'Проблема 2: описание',     unit: 'текст',    key: 'problem2' },
      { label: 'Проблема 2: оценка',       unit: 'млрд сум', key: 'problem2Cost' },
      { label: 'Проблема 2: приоритет',    unit: 'высокий/средний/низкий', key: 'problem2Priority' },
      { label: 'Проблема 3: описание',     unit: 'текст',    key: 'problem3' },
      { label: 'Проблема 3: оценка',       unit: 'млрд сум', key: 'problem3Cost' },
      { label: 'Проблема 3: приоритет',    unit: 'высокий/средний/низкий', key: 'problem3Priority' },
    ],
  },
]

/** Total field count across all sections — useful for coverage calc. */
export const CITY_TOTAL_FIELDS = CITY_SECTIONS.reduce((n, s) => n + s.attrs.length, 0)
