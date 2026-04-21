// i18n dictionary for RsStep5Results.vue.
//
// Previously held a pile of Margilan-IT-course demo data (SCORE_FACTORS,
// MAHALLA_RANKING, STARTUP_COSTS, MONTHLY_COSTS, REVENUE_FORECAST, courses).
// Those lived alongside FERGANA_KINDERGARTEN_OVERRIDE, which silently swapped
// them for a kindergarten variant — classic demo rot. Both are gone now:
// Section 4 (business plan) was deleted, and the remaining sections render
// dynamic data from the backend + Claude's analysis output.
//
// What stays here: pure UI labels + the two fallback demo blocks still wired
// to the template (SWOT quadrants, ACTION_STEPS roadmap, the NBU product
// cards). These carry a visible "Шаблонный пример / Namunaviy shablon" badge
// so users understand they're illustrative.

export const STEP5_T = {
  ru: {
    /* ScoreCircle label */
    outOf100: 'из 100',

    /* SWOT (fallback — Section 2 shows Claude's strengths/weaknesses when
       present; these are the static safety net until the UI is rewired to
       pull SWOT directly from analysis.output). */
    SWOT: {
      strengths: [
        'ООО с 3–5 летней историей — банк оценит стабильность',
        'Нулевая кредитная нагрузка — нет действующих долгов',
        'Положительная маржа (доход > расходы)',
        'Профильное образование и опыт в отрасли',
      ],
      weaknesses: [
        'Ограниченный собственный капитал для расширения',
        'Зависимость от одного филиала',
        'Нет онлайн-платформы для дистанционного обучения',
        'Сезонные колебания потока клиентов',
      ],
      opportunities: [
        'Гос. программа: подготовить 650 IT-специалистов в Маргилане',
        '10,904 мигранта хотят вернуться — нужна переподготовка',
        'IT-Park: инвестиции 5.0 млрд сум в молодёжный бульвар',
        'Кредит «Бизнес прогресс» — 15% годовых, до 2 млрд',
        '1,604 безработных + 974 женщины — целевая аудитория гос. программ',
      ],
      threats: [
        'Высокая отраслевая конкуренция в регионе',
        'Средняя зарплата 3,974 тыс. сум — ценовое давление',
        'Отток квалифицированных кадров за рубеж',
        'Сезонный спад спроса',
      ],
    },

    /* Credit products (match fallback — Section 5 prefers backend credit_products
       when available, falls back to these cards otherwise). */
    PRIMARY_PRODUCT: {
      name: 'Бизнес прогресс',
      program: 'Келажак тадбиркори',
      badge: 'РЕКОМЕНДУЕМЫЙ',
      rows: [
        ['СТАВКА', '15% годовых'],
        ['СУММА', 'До 2 000 млн сум'],
        ['СРОК', 'До 84 месяцев (7 лет)'],
        ['ЛЬГОТНЫЙ ПЕРИОД', 'До 24 месяцев'],
        ['ЗАЛОГ', 'Ликвидное обеспечение — 125% от суммы кредита'],
        ['НАЗНАЧЕНИЕ', 'Расширение деятельности действующего бизнеса'],
        ['ПОЧЕМУ ПОДХОДИТ', 'Низкая ставка, длительный срок, большой льготный период — оптимально для расширения'],
      ],
    },

    ADDITIONAL_PRODUCTS: [
      {
        name: 'Развивайся',
        subtitle: 'Основные средства',
        rate: '23%',
        amount: 'До 3.5 млрд',
        term: 'До 4 лет',
        purpose: 'Закупка оборудования, компьютеров, мебели',
      },
      {
        name: 'Доступный (Имконият)',
        subtitle: 'Первый кредит',
        rate: '23%',
        amount: 'До 150 млн (первый) / 500 млн (повторный)',
        term: 'До 3 лет',
        purpose: 'Оборотные средства или основные средства',
      },
      {
        name: 'Расширяйся',
        subtitle: 'Оборотные средства',
        rate: '23–25%',
        amount: 'До 3.5 млрд',
        term: 'До 3 лет',
        purpose: 'Пополнение оборотных средств',
      },
    ],

    /* Action plan (fallback — Section 6 prefers analysis.output.nextSteps). */
    ACTION_STEPS: [
      { week: 'Неделя 1–2', title: 'Доработка бизнес-плана', desc: 'Финансовые прогнозы и маркетинговый план', status: 'warning' },
      { week: 'Неделя 3–4', title: 'Подача заявки на кредит', desc: 'Подать в отделение NBU по месту регистрации бизнеса', status: 'negative' },
      { week: 'Месяц 2', title: 'Подготовка помещения', desc: 'Аренда/покупка/ремонт согласно проекту', status: 'neutral' },
      { week: 'Месяц 2–3', title: 'Закупка оборудования', desc: 'Ключевые активы, мебель, техника', status: 'neutral' },
      { week: 'Месяц 3', title: 'Набор персонала', desc: 'Основная команда под выбранное направление', status: 'neutral' },
      { week: 'Месяц 3–4', title: 'Маркетинговая кампания', desc: 'Продвижение в соцсетях и в маҳаллях', status: 'neutral' },
      { week: 'Месяц 4', title: 'Запуск', desc: 'Открытие для первых клиентов', status: 'positive' },
      { week: 'Месяц 6', title: 'Выход на окупаемость', desc: 'Стабильная выручка, покрытие расходов', status: 'positive' },
    ],

    /* UI strings */
    restartBtn: '← Начать заново',
    cityContextTitle: 'Контекст города',
    cityContextHint: 'Реальные данные, использованные в рекомендации',
    demoBadge: 'Шаблонный пример',
    demoBadgeHint: 'Персональная генерация появится в следующей версии',
    section1Title: 'AI Оценка готовности бизнеса',
    section1Sub: 'Ключевые факторы: опыт, финансы, рынок, локация, конкуренция, модель',
    goodPotential: 'Хороший потенциал',
    aiConclusion: 'Вывод AI',
    aiConclusionText:
      'Ваш бизнес имеет хороший потенциал для расширения. Сильные стороны — стабильная история и нулевая кредитная нагрузка. Основной риск — высокая отраслевая конкуренция. Рекомендуем дифференцироваться через стратегические направления, совпадающие с программой развития региона.',
    section2Title: 'SWOT-анализ',
    section2Sub: 'Ваш бизнес в контексте региональных условий',
    swotStrengths: 'Сильные стороны',
    swotWeaknesses: 'Слабые стороны',
    swotOpportunities: 'Возможности',
    swotThreats: 'Угрозы',
    section3Title: 'Карта махаллей (пилот)',
    section3Sub: 'Маргилан · 8 из 50 махаллей нанесено — остальные будут добавлены по мере оцифровки',
    locationInsightTitle: 'AI рекомендация по локации',
    locationInsightText:
      'Лучшие локации для расширения — махалля Бахрин (1,218 новых рабочих мест, центр возвращающихся мигрантов) и З.М. Бобур (молодёжный район, 1,008 рабочих мест). Оба района имеют высокий спрос и совпадают с государственными программами занятости.',
    section5Title: 'Кредитные продукты NBU',
    section5Sub: 'Каталог «Кредиты 2026» · подобраны по вашей сумме, залогу и цели',
    altProductsLabel: 'АЛЬТЕРНАТИВНЫЕ ПРОДУКТЫ',
    rateLabel: 'Ставка:',
    amountLabel: 'Сумма:',
    termLabel: 'Срок:',
    collateralLabel: 'Залог:',
    purposeLabel: 'Цель:',
    matchReasons: 'Почему подходит',
    recommendedBadge: 'РЕКОМЕНДУЕМЫЙ',
    catalogNote: 'Все продукты — из официального каталога NBU «Кредиты 2026». Финальное одобрение — на стороне банка.',
    section6Title: 'План действий',
    section6Sub: 'Пошаговый план на 6 месяцев',
    section7MapTitle: 'Карта учебных центров — Фергана',
    section7MapSub: 'Интерактивная карта существующих учебных центров, конкуренции и рекомендуемых зон',
    ctaTitle: 'Готовы начать?',
    ctaSubtitle: 'Подайте заявку на кредит «Бизнес прогресс» или скачайте полный бизнес-план',
    applyBtn: 'Подать заявку в банк',
    downloadBtn: 'Скачать бизнес-план (PDF)',
    downloadAlert: 'Бизнес-план будет доступен в следующей версии',
    restartCta: 'Или начните тест заново',
  },

  uz: {
    outOf100: '100 dan',

    SWOT: {
      strengths: [
        'MChJ 3–5 yillik tarixga ega — bank barqarorlikni baholaydi',
        'Nol kredit yuki — amaldagi qarzlar yoʻq',
        'Ijobiy marj (daromad > xarajat)',
        'Sohaviy taʻlim va tarmoqdagi tajriba',
      ],
      weaknesses: [
        'Kengaytirish uchun cheklangan oʻz kapitali',
        'Bitta filialga bogʻliqlik',
        'Masofaviy xizmat uchun onlayn platforma yoʻq',
        'Mijozlar oqimida mavsumiy tebranishlar',
      ],
      opportunities: [
        'Davlat dasturi: Margʻilonda 650 nafar IT mutaxassis tayyorlash',
        '10 904 migrant qaytishni istaydi — qayta tayyorlash kerak',
        'IT-Park: yoshlar bulvariga 5.0 mlrd soʻm investitsiya',
        '«Biznes progress» krediti — yiliga 15%, 2 mlrdgacha',
        '1 604 ishsiz + 974 ayol — davlat dasturlarining maqsadli auditoriyasi',
      ],
      threats: [
        'Hududda yuqori raqobat',
        'Oʻrtacha ish haqi 3 974 ming soʻm — narx bosimi',
        'Malakali kadrlarning chet elga ketishi',
        'Mavsumiy talab pasayishi',
      ],
    },

    PRIMARY_PRODUCT: {
      name: 'Biznes progress',
      program: 'Kelajak tadbirkori',
      badge: 'TAVSIYa ETILGAN',
      rows: [
        ['STAVKA', 'yiliga 15%'],
        ['SUMMA', '2 000 mln soʻmgacha'],
        ['MUDDAT', '84 oygacha (7 yil)'],
        ['IMTIYoZLI DAVR', '24 oygacha'],
        ['GAROV', 'Likvid taʻminot — kredit summasining 125%'],
        ['MAQSAD', 'Amaldagi biznes faoliyatini kengaytirish'],
        ['NEGA MOS KELADI', 'Past stavka, uzoq muddat, katta imtiyozli davr — kengaytirish uchun optimal'],
      ],
    },

    ADDITIONAL_PRODUCTS: [
      {
        name: 'Rivojlan',
        subtitle: 'Asosiy vositalar',
        rate: '23%',
        amount: '3.5 mlrdgacha',
        term: '4 yilgacha',
        purpose: 'Jihoz, kompyuter, mebel sotib olish',
      },
      {
        name: 'Imkoniyat (Dostupniy)',
        subtitle: 'Birinchi kredit',
        rate: '23%',
        amount: '150 mlngacha (birinchi) / 500 mln (takroriy)',
        term: '3 yilgacha',
        purpose: 'Aylanma yoki asosiy vositalar',
      },
      {
        name: 'Kengay',
        subtitle: 'Aylanma mablagʻlar',
        rate: '23–25%',
        amount: '3.5 mlrdgacha',
        term: '3 yilgacha',
        purpose: 'Aylanma mablagʻlarni toʻldirish',
      },
    ],

    ACTION_STEPS: [
      { week: '1–2 hafta', title: 'Biznes-planni yakunlash', desc: 'Moliyaviy prognoz va marketing rejasini takomillashtirish', status: 'warning' },
      { week: '3–4 hafta', title: 'Kreditga ariza berish', desc: 'Roʻyxatdan oʻtgan tumandagi NBU boʻlimiga ariza topshirish', status: 'negative' },
      { week: '2 oy', title: 'Binoni tayyorlash', desc: 'Ijara/sotib olish/taʻmir loyiha boʻyicha', status: 'neutral' },
      { week: '2–3 oy', title: 'Jihozlarni sotib olish', desc: 'Asosiy aktivlar, mebel, texnika', status: 'neutral' },
      { week: '3 oy', title: 'Xodimlarni yollash', desc: 'Tanlangan yoʻnalish boʻyicha asosiy jamoa', status: 'neutral' },
      { week: '3–4 oy', title: 'Marketing kampaniyasi', desc: 'Ijtimoiy tarmoqlar va mahallalardagi reklama', status: 'neutral' },
      { week: '4 oy', title: 'Ochilish', desc: 'Birinchi mijozlar uchun ishga tushirish', status: 'positive' },
      { week: '6 oy', title: 'Zararsizlik nuqtasi', desc: 'Barqaror daromad, xarajatlarni qoplash', status: 'positive' },
    ],

    restartBtn: '← Qaytadan boshlash',
    cityContextTitle: 'Shahar konteksti',
    cityContextHint: 'Tavsiyada ishlatilgan haqiqiy maʻlumotlar',
    demoBadge: 'Namunaviy shablon',
    demoBadgeHint: 'Shaxsiy generatsiya keyingi versiyada paydo boʻladi',
    section1Title: 'AI Biznes tayyorligini baholash',
    section1Sub: 'Asosiy omillar: tajriba, moliya, bozor, joylashuv, raqobat, model',
    goodPotential: 'Yaxshi potentsial',
    aiConclusion: 'AI xulosasi',
    aiConclusionText:
      'Biznesingiz kengaytirish uchun yaxshi potentsialga ega. Kuchli tomonlari — barqaror tarix va nol kredit yuki. Asosiy xavf — yuqori sohaviy raqobat. Mintaqa rivojlanish dasturiga mos keluvchi strategik yoʻnalishlar orqali differentsiatsiya qilishni tavsiya etamiz.',
    section2Title: 'SWOT-tahlil',
    section2Sub: 'Biznesingiz mintaqaviy sharoitlar kontekstida',
    swotStrengths: 'Kuchli tomonlar',
    swotWeaknesses: 'Zaif tomonlar',
    swotOpportunities: 'Imkoniyatlar',
    swotThreats: 'Tahdidlar',
    section3Title: 'Mahallalar xaritasi (pilot)',
    section3Sub: 'Margʻilon · 50 ta mahalladan 8 tasi xaritaga tushirilgan',
    locationInsightTitle: 'AI joylashuv tavsiyasi',
    locationInsightText:
      'Kengaytirish uchun eng yaxshi joylashuvlar — Bahrin mahallasi (1 218 ta yangi ish oʻrni, qaytayotgan migrantlar markazi) va Z.M. Bobur (yoshlar tumani, 1 008 ta ish oʻrni). Har ikkala tumanda yuqori talab mavjud va davlat dasturlariga mos keladi.',
    section5Title: 'NBU kredit mahsulotlari',
    section5Sub: '«Kreditlar 2026» katalogi · sizning summa, garov va maqsad boʻyicha tanlandi',
    altProductsLabel: 'MUQOBIL MAHSULOTLAR',
    rateLabel: 'Stavka:',
    amountLabel: 'Summa:',
    termLabel: 'Muddat:',
    collateralLabel: 'Garov:',
    purposeLabel: 'Maqsad:',
    matchReasons: 'Nega mos keladi',
    recommendedBadge: 'TAVSIYa ETILGAN',
    catalogNote: 'Barcha mahsulotlar — NBU «Kreditlar 2026» rasmiy katalogidan. Yakuniy tasdiq — bank tomonidan.',
    section6Title: 'Harakat rejasi',
    section6Sub: '6 oyga bosqichma-bosqich reja',
    section7MapTitle: 'Oʻquv markazlari xaritasi — Fargʻona',
    section7MapSub: 'Mavjud oʻquv markazlari, raqobat va yangi biznes ochish uchun tavsiya etiladigan hududlarning interaktiv xaritasi',
    ctaTitle: 'Boshlashga tayyormisiz?',
    ctaSubtitle: '«Biznes progress» kreditiga ariza bering yoki toʻliq biznes-planni yuklab oling',
    applyBtn: 'Bankka ariza berish',
    downloadBtn: 'Biznes-planni yuklab olish (PDF)',
    downloadAlert: 'Biznes-plan keyingi versiyada mavjud boʻladi',
    restartCta: 'Yoki testni qaytadan boshlang',
  },
}
