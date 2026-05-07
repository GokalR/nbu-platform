/**
 * Golden Mart — city schema.
 *
 * AUTO-GENERATED from goldenmarts/GM_city.md (which itself is
 * generated from goldenmarts/golden_mart_city.xlsx via _to_md.py).
 * Do not hand-edit. To change: edit the Excel, run _to_md.py, then
 * goldenmarts/_md_to_schema_js.py. Bilingual labels come from
 * goldenmarts/_translations_uz.json — missing keys fall back to RU.
 *
 * Per-entity data files reference fields by `key` (positional s{section}_{index}).
 */

export const CITY_SECTIONS = [
  {
    n: 1, title: 'Базовая информация', titleUz: 'Asosiy maʼlumotlar', icon: 'badge',
    attrs: [
      { key: 's1_1', label: 'Название', labelUz: 'Nomi', unit: 'текст' },
      { key: 's1_2', label: 'Тип объекта (город / туман)', labelUz: 'Obyekt turi (shahar / tuman)', unit: 'текст' },
      { key: 's1_3', label: 'Админ. центр области (да/нет)', labelUz: 'Viloyat markazi (ha/yoʻq)', unit: 'да/нет' },
      { key: 's1_4', label: 'Площадь', labelUz: 'Maydon', unit: 'км²' },
      { key: 's1_5', label: 'Махаллей', labelUz: 'Mahallalar', unit: 'шт.' },
      { key: 's1_6', label: 'Население постоянное', labelUz: 'Doimiy aholi', unit: 'чел.' },
      { key: 's1_7', label: 'Мужчин', labelUz: 'Erkaklar', unit: 'чел.' },
      { key: 's1_8', label: 'Женщин', labelUz: 'Ayollar', unit: 'чел.' },
      { key: 's1_9', label: 'Население 0–14 лет', labelUz: '0–14 yosh aholisi', unit: 'чел.' },
      { key: 's1_10', label: 'Население 15–64 лет', labelUz: '15–64 yosh aholisi', unit: 'чел.' },
      { key: 's1_11', label: 'Население 65+ лет', labelUz: '65+ yosh aholisi', unit: 'чел.' },
      { key: 's1_12', label: 'Население 0–2 лет', labelUz: '0–2 yosh aholisi', unit: 'чел.' },
      { key: 's1_13', label: 'Население 3–5 лет', labelUz: '3–5 yosh aholisi', unit: 'чел.' },
      { key: 's1_14', label: 'Население 6–7 лет', labelUz: '6–7 yosh aholisi', unit: 'чел.' },
      { key: 's1_15', label: 'Население 8–15 лет', labelUz: '8–15 yosh aholisi', unit: 'чел.' },
      { key: 's1_16', label: 'Население 16–17 лет', labelUz: '16–17 yosh aholisi', unit: 'чел.' },
      { key: 's1_17', label: 'Население 18–19 лет', labelUz: '18–19 yosh aholisi', unit: 'чел.' },
      { key: 's1_18', label: 'Население 20–24 лет', labelUz: '20–24 yosh aholisi', unit: 'чел.' },
      { key: 's1_19', label: 'Население 25–29 лет', labelUz: '25–29 yosh aholisi', unit: 'чел.' },
      { key: 's1_20', label: 'Население 30–34 лет', labelUz: '30–34 yosh aholisi', unit: 'чел.' },
      { key: 's1_21', label: 'Население 35–39 лет', labelUz: '35–39 yosh aholisi', unit: 'чел.' },
      { key: 's1_22', label: 'Население 40–49 лет', labelUz: '40–49 yosh aholisi', unit: 'чел.' },
      { key: 's1_23', label: 'Население 50–59 лет', labelUz: '50–59 yosh aholisi', unit: 'чел.' },
      { key: 's1_24', label: 'Население 60–69 лет', labelUz: '60–69 yosh aholisi', unit: 'чел.' },
      { key: 's1_25', label: 'Население 70–74 лет', labelUz: '70–74 yosh aholisi', unit: 'чел.' },
      { key: 's1_26', label: 'Население 75–79 лет', labelUz: '75–79 yosh aholisi', unit: 'чел.' },
      { key: 's1_27', label: 'Население 80–84 лет', labelUz: '80–84 yosh aholisi', unit: 'чел.' },
      { key: 's1_28', label: 'Население 85+ лет', labelUz: '85+ yosh aholisi', unit: 'чел.' },
      { key: 's1_29', label: 'Семей', labelUz: 'Oilalar', unit: 'тыс.' },
      { key: 's1_30', label: 'Домохозяйств', labelUz: 'Xonadonlar', unit: 'тыс.' },
    ],
  },
  {
    n: 2, title: 'Экономика – объёмы', titleUz: 'Iqtisodiyot – hajmlar', icon: 'finance',
    attrs: [
      { key: 's2_1', label: 'ВТП (валовой территориальный продукт)', labelUz: 'YaHM (yalpi hududiy mahsulot)', unit: 'млрд сум' },
      { key: 's2_2', label: 'Промышленность – объём', labelUz: 'Sanoat – hajmi', unit: 'млрд сум' },
      { key: 's2_3', label: 'Услуги – объём', labelUz: 'Xizmatlar – hajmi', unit: 'млрд сум' },
      { key: 's2_4', label: 'Розничная торговля – объём', labelUz: 'Chakana savdo – hajmi', unit: 'млрд сум' },
      { key: 's2_5', label: 'Строительство – объём', labelUz: 'Qurilish – hajmi', unit: 'млрд сум' },
      { key: 's2_6', label: 'Сельское хозяйство – объём', labelUz: 'Qishloq xoʻjaligi – hajmi', unit: 'млрд сум' },
      { key: 's2_7', label: 'Инвестиции в основной капитал', labelUz: 'Asosiy kapitalga investitsiyalar', unit: 'млрд сум' },
    ],
  },
  {
    n: 3, title: 'Бюджет', titleUz: 'Byudjet', icon: 'account_balance',
    attrs: [
      { key: 's3_1', label: 'Доходы бюджета – всего', labelUz: 'Byudjet daromadlari – jami', unit: 'млрд сум' },
      { key: 's3_2', label: 'Налоговые поступления', labelUz: 'Soliq tushumlari', unit: 'млрд сум' },
      { key: 's3_3', label: 'Неналоговые доходы', labelUz: 'Nosoliq daromadlar', unit: 'млрд сум' },
      { key: 's3_4', label: 'Трансферты из вышестоящ. бюджета', labelUz: 'Yuqori byudjetdan transfertlar', unit: 'млрд сум' },
      { key: 's3_5', label: 'Расходы бюджета – всего', labelUz: 'Byudjet xarajatlari – jami', unit: 'млрд сум' },
      { key: 's3_6', label: 'Социальная сфера', labelUz: 'Ijtimoiy soha', unit: 'млрд сум' },
      { key: 's3_7', label: 'Инфраструктура и экономика', labelUz: 'Infratuzilma va iqtisodiyot', unit: 'млрд сум' },
      { key: 's3_8', label: 'Управление и прочее', labelUz: 'Boshqaruv va boshqalar', unit: 'млрд сум' },
      { key: 's3_9', label: 'Дефицит / Профицит бюджета', labelUz: 'Byudjet defitsiti / profitsiti', unit: 'млрд сум' },
    ],
  },
  {
    n: 4, title: 'Внешняя торговля', titleUz: 'Tashqi savdo', icon: 'public',
    attrs: [
      { key: 's4_1', label: 'Экспорт', labelUz: 'Eksport', unit: 'млрд сум' },
      { key: 's4_2', label: 'Импорт', labelUz: 'Import', unit: 'млрд сум' },
      { key: 's4_3', label: 'Сальдо торговли (экспорт − импорт)', labelUz: 'Savdo saldosi (eksport − import)', unit: 'млрд сум' },
    ],
  },
  {
    n: 5, title: 'Основные торговые партнёры', titleUz: 'Asosiy savdo hamkorlari', icon: 'flag',
    attrs: [
      { key: 's5_1', label: 'Экспорт – страна 1: название', labelUz: 'Eksport – mamlakat 1: nomi', unit: 'текст' },
      { key: 's5_2', label: 'Экспорт – страна 1: объём', labelUz: 'Eksport – mamlakat 1: hajmi', unit: 'млрд сум' },
      { key: 's5_3', label: 'Экспорт – страна 2: объём', labelUz: 'Eksport – mamlakat 2: hajmi', unit: 'млрд сум' },
      { key: 's5_4', label: 'Экспорт – страна 3: название', labelUz: 'Eksport – mamlakat 3: nomi', unit: 'текст' },
      { key: 's5_5', label: 'Экспорт – страна 3: объём', labelUz: 'Eksport – mamlakat 3: hajmi', unit: 'млрд сум' },
      { key: 's5_6', label: 'Импорт – страна 1: название', labelUz: 'Import – mamlakat 1: nomi', unit: 'текст' },
      { key: 's5_7', label: 'Импорт – страна 1: объём', labelUz: 'Import – mamlakat 1: hajmi', unit: 'млрд сум' },
      { key: 's5_8', label: 'Импорт – страна 2: название', labelUz: 'Import – mamlakat 2: nomi', unit: 'текст' },
      { key: 's5_9', label: 'Импорт – страна 2: объём', labelUz: 'Import – mamlakat 2: hajmi', unit: 'млрд сум' },
      { key: 's5_10', label: 'Импорт – страна 3: название', labelUz: 'Import – mamlakat 3: nomi', unit: 'текст' },
      { key: 's5_11', label: 'Импорт – страна 3: объём', labelUz: 'Import – mamlakat 3: hajmi', unit: 'млрд сум' },
    ],
  },
  {
    n: 6, title: 'Инвестиции по источникам', titleUz: 'Manba boʻyicha investitsiyalar', icon: 'savings',
    attrs: [
      { key: 's6_1', label: 'Собственные средства предприятий', labelUz: 'Korxonalarning oʻz mablagʻlari', unit: 'млрд сум' },
      { key: 's6_2', label: 'Иностранные инвестиции', labelUz: 'Xorijiy investitsiyalar', unit: 'млрд сум' },
      { key: 's6_3', label: 'Госбюджет', labelUz: 'Davlat byudjeti', unit: 'млрд сум' },
      { key: 's6_4', label: 'Банковские кредиты', labelUz: 'Bank kreditlari', unit: 'млрд сум' },
      { key: 's6_5', label: 'Средства населения', labelUz: 'Aholi mablagʻlari', unit: 'млрд сум' },
      { key: 's6_6', label: 'Фонд реконструкции', labelUz: 'Rekonstruksiya jamgʻarmasi', unit: 'млрд сум' },
    ],
  },
  {
    n: 7, title: 'Предпринимательство', titleUz: 'Tadbirkorlik', icon: 'storefront',
    attrs: [
      { key: 's7_1', label: 'Активных субъектов – всего', labelUz: 'Faol subʼyektlar – jami', unit: 'шт.' },
      { key: 's7_2', label: 'ООО', labelUz: 'MChJ', unit: 'шт.' },
      { key: 's7_3', label: 'ИП (ЯТТ)', labelUz: 'YaTT', unit: 'шт.' },
      { key: 's7_4', label: 'Фермерские хозяйства', labelUz: 'Fermer xoʻjaliklari', unit: 'шт.' },
      { key: 's7_5', label: 'Прочие', labelUz: 'Boshqalar', unit: 'шт.' },
      { key: 's7_6', label: 'Неактивных (приостановл.)', labelUz: 'Faolmas (toʻxtatilgan)', unit: 'шт.' },
      { key: 's7_7', label: 'Открыто новых за год', labelUz: 'Yil davomida yangi ochilgan', unit: 'шт.' },
      { key: 's7_8', label: 'Предприятий-экспортёров', labelUz: 'Eksport korxonalari', unit: 'шт.' },
    ],
  },
  {
    n: 8, title: 'Рынок труда', titleUz: 'Mehnat bozori', icon: 'work',
    attrs: [
      { key: 's8_1', label: 'Экономически активное население', labelUz: 'Iqtisodiy faol aholi', unit: 'чел.' },
      { key: 's8_2', label: 'Официально занятых', labelUz: 'Rasmiy bandlar', unit: 'тыс. чел.' },
      { key: 's8_3', label: 'Неофициально занятых', labelUz: 'Norasmiy bandlar', unit: 'тыс. чел.' },
      { key: 's8_4', label: 'Безработных', labelUz: 'Ishsizlar', unit: 'чел.' },
      { key: 's8_5', label: 'Уровень безработицы', labelUz: 'Ishsizlik darajasi', unit: '%' },
      { key: 's8_6', label: 'Создано новых рабочих мест за год', labelUz: 'Yil davomida yaratilgan yangi ish oʻrinlari', unit: 'раб. мест' },
      { key: 's8_7', label: 'Трудовых мигрантов за рубежом', labelUz: 'Chet eldagi mehnat migrantlari', unit: 'чел.' },
      { key: 's8_8', label: 'Средняя номинальная зарплата – всего', labelUz: 'Oʻrtacha nominal ish haqi – jami', unit: 'тыс. сум/мес' },
      { key: 's8_9', label: 'в промышленности', labelUz: 'sanoatda', unit: 'тыс. сум/мес' },
      { key: 's8_10', label: 'в торговле', labelUz: 'savdoda', unit: 'тыс. сум/мес' },
      { key: 's8_11', label: 'в строительстве', labelUz: 'qurilishda', unit: 'тыс. сум/мес' },
      { key: 's8_12', label: 'в бюджетной сфере', labelUz: 'byudjet sohasida', unit: 'тыс. сум/мес' },
      { key: 's8_13', label: 'в сельском хозяйстве', labelUz: 'qishloq xoʻjaligida', unit: 'тыс. сум/мес' },
    ],
  },
  {
    n: 9, title: 'Бедность и социальная сфера', titleUz: 'Kambagʻallik va ijtimoiy soha', icon: 'volunteer_activism',
    attrs: [
      { key: 's9_1', label: 'Семей в Социальном реестре', labelUz: 'Ijtimoiy reyestrdagi oilalar', unit: 'семей' },
      { key: 's9_2', label: 'Семей в бедности на начало года', labelUz: 'Yil boshida kambagʻal oilalar', unit: 'семей' },
      { key: 's9_3', label: 'Семей в бедности на конец года', labelUz: 'Yil oxirida kambagʻal oilalar', unit: 'семей' },
      { key: 's9_4', label: 'Покрытие Соц. реестром (от семей в бедности нач. года), %', labelUz: 'Ijt. reyestr qamrovi (yil boshidagi kambagʻal oilalardan), %', unit: '%' },
      { key: 's9_5', label: 'Родившихся за год', labelUz: 'Yil davomida tugʻilganlar', unit: 'чел.' },
      { key: 's9_6', label: 'Умерших за год', labelUz: 'Yil davomida vafot etganlar', unit: 'чел.' },
      { key: 's9_7', label: 'Эмиграция', labelUz: 'Emigratsiya', unit: 'чел.' },
      { key: 's9_8', label: 'Иммиграция', labelUz: 'Immigratsiya', unit: 'чел.' },
      { key: 's9_9', label: 'Заключено браков за год', labelUz: 'Yil davomida tuzilgan nikohlar', unit: 'браков' },
      { key: 's9_10', label: 'Разводов за год', labelUz: 'Yil davomida ajralishlar', unit: 'разводов' },
    ],
  },
  {
    n: 10, title: 'Образование', titleUz: 'Taʼlim', icon: 'school',
    attrs: [
      { key: 's10_1', label: 'Школ (общеобразовательных)', labelUz: 'Maktablar (umumtaʼlim)', unit: 'шт.' },
      { key: 's10_2', label: 'Учеников в школах', labelUz: 'Maktab oʻquvchilari', unit: 'чел.' },
      { key: 's10_3', label: 'Учителей', labelUz: 'Oʻqituvchilar', unit: 'чел.' },
      { key: 's10_4', label: 'Колледжей / техникумов', labelUz: 'Kollejlar / texnikumlar', unit: 'шт.' },
      { key: 's10_5', label: 'Студентов в колледжах', labelUz: 'Kollej talabalari', unit: 'чел.' },
      { key: 's10_6', label: 'Вузов', labelUz: 'OTM', unit: 'шт.' },
      { key: 's10_7', label: 'Студентов в вузах', labelUz: 'OTM talabalari', unit: 'чел.' },
      { key: 's10_8', label: 'Детских садов (МТМ)', labelUz: 'Bolalar bogʻchalari (MTM)', unit: 'шт.' },
      { key: 's10_9', label: 'Детей в детсадах', labelUz: 'Bogʻchadagi bolalar', unit: 'чел.' },
    ],
  },
  {
    n: 11, title: 'Здравоохранение', titleUz: 'Sogʻliqni saqlash', icon: 'local_hospital',
    attrs: [
      { key: 's11_1', label: 'Больниц', labelUz: 'Shifoxonalar', unit: 'шт.' },
      { key: 's11_2', label: 'Поликлиник / ЦРП', labelUz: 'Poliklinikalar / TRP', unit: 'шт.' },
      { key: 's11_3', label: 'Койко-мест', labelUz: 'Oʻrin-joylar', unit: 'шт.' },
      { key: 's11_4', label: 'Врачей', labelUz: 'Shifokorlar', unit: 'чел.' },
      { key: 's11_5', label: 'Медсестёр и ср. мед. персонала', labelUz: 'Hamshira va oʻrta tibbiy xodimlar', unit: 'чел.' },
      { key: 's11_6', label: 'Младенческая смертность (на 1000 родившихся)', labelUz: 'Goʻdaklar oʻlimi (1000 tugʻilganga)', unit: '‰' },
      { key: 's11_7', label: 'Рождений (всего)', labelUz: 'Tugʻilishlar (jami)', unit: 'чел.' },
      { key: 's11_8', label: 'Смертей (всего)', labelUz: 'Oʻlimlar (jami)', unit: 'чел.' },
    ],
  },
  {
    n: 12, title: 'Банковский сектор', titleUz: 'Bank sektori', icon: 'account_balance_wallet',
    attrs: [
      { key: 's12_1', label: 'Кредитный портфель – всего', labelUz: 'Kredit portfeli – jami', unit: 'млрд сум' },
      { key: 's12_2', label: 'Кредиты МСБ', labelUz: 'KOB kreditlari', unit: 'млрд сум' },
      { key: 's12_3', label: 'Кредиты экспортёрам', labelUz: 'Eksportyorlarga kreditlar', unit: 'млрд сум' },
      { key: 's12_4', label: 'Кредиты физлицам', labelUz: 'Jismoniy shaxslarga kreditlar', unit: 'млрд сум' },
      { key: 's12_5', label: 'в т.ч. ипотечные / ИЖС', labelUz: 'shu jumladan ipoteka / IUQ', unit: 'млрд сум' },
      { key: 's12_6', label: 'Прочие кредиты', labelUz: 'Boshqa kreditlar', unit: 'млрд сум' },
      { key: 's12_7', label: 'Депозитный портфель – всего', labelUz: 'Depozit portfeli – jami', unit: 'млрд сум' },
      { key: 's12_8', label: 'Депозиты юр. лиц', labelUz: 'Yur. shaxs depozitlari', unit: 'млрд сум' },
      { key: 's12_9', label: 'Депозиты физ. лиц', labelUz: 'Jis. shaxs depozitlari', unit: 'млрд сум' },
      { key: 's12_10', label: 'Просроченная задолженность (NPL)', labelUz: 'Muddati oʻtgan qarz (NPL)', unit: 'млрд сум' },
      { key: 's12_11', label: 'Кредитов выдано МСБ (кол-во)', labelUz: 'KOB kreditlari berildi (soni)', unit: 'шт.' },
      { key: 's12_12', label: 'Кредитов выдано экспортёрам (кол-во)', labelUz: 'Eksportyorlarga kreditlar berildi (soni)', unit: 'шт.' },
      { key: 's12_13', label: 'Кредитов выдано самозанятым (кол-во)', labelUz: 'Oʻz-oʻzini taʼminlovchilarga kreditlar berildi (soni)', unit: 'шт.' },
      { key: 's12_14', label: 'Просроченных кредитов NPL (кол-во)', labelUz: 'NPL muddati oʻtgan kreditlar (soni)', unit: 'шт.' },
      { key: 's12_15', label: 'Новых ИП, получивших кредит (за квартал)', labelUz: 'Kredit olgan yangi YaTT (chorak)', unit: 'шт.' },
    ],
  },
  {
    n: 13, title: 'Туризм', titleUz: 'Turizm', icon: 'travel_explore',
    attrs: [
      { key: 's13_1', label: 'Иностранных туристов', labelUz: 'Xorijiy turistlar', unit: 'тыс.' },
      { key: 's13_2', label: 'Внутренних туристов', labelUz: 'Mahalliy turistlar', unit: 'тыс.' },
      { key: 's13_3', label: 'Объектов размещения', labelUz: 'Joylashtirish obyektlari', unit: 'шт.' },
      { key: 's13_4', label: 'Номеров в объектах размещения', labelUz: 'Joylashtirish obyektlari xonalari', unit: 'номеров' },
      { key: 's13_5', label: 'Доход от туризма (иностр. туристов)', labelUz: 'Turizm daromadi (xorijiy)', unit: 'млрд сум' },
      { key: 's13_6', label: 'Доход от туризма (внутр. туристов)', labelUz: 'Turizm daromadi (mahalliy)', unit: 'млрд сум' },
    ],
  },
  {
    n: 14, title: 'Жильё', titleUz: 'Uy-joy', icon: 'home',
    attrs: [
      { key: 's14_1', label: 'Жилой фонд – всего', labelUz: 'Uy-joy fondi – jami', unit: 'тыс. м²' },
      { key: 's14_2', label: 'Введено жилья за год', labelUz: 'Yil davomida foydalanishga topshirilgan', unit: 'тыс. м²' },
      { key: 's14_3', label: 'Многоквартирных домов', labelUz: 'Koʻp xonadonli uylar', unit: 'шт.' },
      { key: 's14_4', label: 'Частных домов', labelUz: 'Xususiy uylar', unit: 'шт.' },
      { key: 's14_5', label: 'Аварийного жилья', labelUz: 'Avariya uylar', unit: 'тыс. м²' },
      { key: 's14_6', label: 'Доля аварийного жилья, %', labelUz: 'Avariya uylar ulushi, %', unit: '%' },
    ],
  },
  {
    n: 15, title: 'Инфраструктура – подключения и сети', titleUz: 'Infratuzilma – ulanishlar va tarmoqlar', icon: 'hub',
    attrs: [
      { key: 's15_1', label: 'Подключено к электричеству', labelUz: 'Elektrga ulangan', unit: 'домохоз.' },
      { key: 's15_2', label: 'Охват электричеством, %', labelUz: 'Elektr qamrovi, %', unit: '%' },
      { key: 's15_3', label: 'Подключено к водопроводу', labelUz: 'Suvga ulangan', unit: 'домохоз.' },
      { key: 's15_4', label: 'Охват водопроводом, %', labelUz: 'Suv qamrovi, %', unit: '%' },
      { key: 's15_5', label: 'Охват канализацией, %', labelUz: 'Kanalizatsiya qamrovi, %', unit: '%' },
      { key: 's15_6', label: 'Подключено к газу', labelUz: 'Gazga ulangan', unit: 'домохоз.' },
    ],
  },
  {
    n: 16, title: 'Дороги', titleUz: 'Yoʻllar', icon: 'route',
    attrs: [
      { key: 's16_1', label: 'Дороги – всего', labelUz: 'Yoʻllar – jami', unit: 'км' },
      { key: 's16_2', label: 'Асфальтированные', labelUz: 'Asfaltlangan', unit: 'км' },
      { key: 's16_3', label: 'Доля асфальтированных дорог, %', labelUz: 'Asfaltlangan yoʻllar ulushi, %', unit: '%' },
      { key: 's16_4', label: 'Грунтовые', labelUz: 'Tuproq yoʻllar', unit: 'км' },
      { key: 's16_5', label: 'В хорошем состоянии', labelUz: 'Yaxshi holatda', unit: 'км' },
      { key: 's16_6', label: 'Доля дорог в хорошем состоянии, %', labelUz: 'Yaxshi holatdagi yoʻllar ulushi, %', unit: '%' },
      { key: 's16_7', label: 'Требуют ремонта', labelUz: 'Taʼmir talab qiladi', unit: 'км' },
      { key: 's16_8', label: 'Требуют капитального ремонта', labelUz: 'Kapital taʼmir talab qiladi', unit: 'км' },
    ],
  },
  {
    n: 17, title: 'Транспорт', titleUz: 'Transport', icon: 'directions_bus',
    attrs: [
      { key: 's17_1', label: 'Автобусных маршрутов', labelUz: 'Avtobus marshrutlari', unit: 'маршрутов' },
      { key: 's17_2', label: 'Автобусов в парке общ. транспорта', labelUz: 'Jamoat transportidagi avtobuslar', unit: 'шт.' },
      { key: 's17_3', label: 'Такси (зарегистрировано)', labelUz: 'Taksi (roʻyxatdan oʻtgan)', unit: 'шт.' },
      { key: 's17_4', label: 'Легковых авто (зарегистрировано)', labelUz: 'Yengil avtomobillar (roʻyxatdan oʻtgan)', unit: 'шт.' },
    ],
  },
  {
    n: 18, title: 'Экология', titleUz: 'Ekologiya', icon: 'park',
    attrs: [
      { key: 's18_1', label: 'Зелёных насаждений', labelUz: 'Yashil koʻchatlar', unit: 'га' },
      { key: 's18_2', label: 'Вывоз ТБО за год', labelUz: 'MMChIning olib chiqarilishi', unit: 'тонн' },
    ],
  },
  {
    n: 19, title: 'Цифровизация', titleUz: 'Raqamlashtirish', icon: 'devices',
    attrs: [
      { key: 's19_1', label: 'Онлайн-платежи (транзакций в год)', labelUz: 'Onlayn toʻlovlar (yiliga tranzaksiya)', unit: 'тыс. шт.' },
      { key: 's19_2', label: 'Онлайн-кредитов выдано за год', labelUz: 'Yil davomida onlayn kreditlar berildi', unit: 'шт.' },
      { key: 's19_3', label: 'Покрытие 4G (по площади территории)', labelUz: '4G qamrovi (hudud maydoni boʻyicha)', unit: '%' },
    ],
  },
  {
    n: 20, title: 'Топ-5 махаллей по кредитной активности', titleUz: 'Kredit faolligi boʻyicha top-5 mahalla', icon: 'leaderboard',
    attrs: [
      { key: 's20_1', label: 'Махалля 1: название', labelUz: 'Mahalla 1: nomi', unit: 'текст' },
      { key: 's20_2', label: 'Махалля 1: количество кредитов', labelUz: 'Mahalla 1: kreditlar soni', unit: 'шт.' },
      { key: 's20_3', label: 'Махалля 1: рейтинг/скор', labelUz: 'Mahalla 1: reyting/skor', unit: 'балл' },
      { key: 's20_4', label: 'Махалля 2: название', labelUz: 'Mahalla 2: nomi', unit: 'текст' },
      { key: 's20_5', label: 'Махалля 2: количество кредитов', labelUz: 'Mahalla 2: kreditlar soni', unit: 'шт.' },
      { key: 's20_6', label: 'Махалля 2: рейтинг/скор', labelUz: 'Mahalla 2: reyting/skor', unit: 'балл' },
      { key: 's20_7', label: 'Махалля 3: название', labelUz: 'Mahalla 3: nomi', unit: 'текст' },
      { key: 's20_8', label: 'Махалля 3: количество кредитов', labelUz: 'Mahalla 3: kreditlar soni', unit: 'шт.' },
      { key: 's20_9', label: 'Махалля 3: рейтинг/скор', labelUz: 'Mahalla 3: reyting/skor', unit: 'балл' },
      { key: 's20_10', label: 'Махалля 4: название', labelUz: 'Mahalla 4: nomi', unit: 'текст' },
      { key: 's20_11', label: 'Махалля 4: количество кредитов', labelUz: 'Mahalla 4: kreditlar soni', unit: 'шт.' },
      { key: 's20_12', label: 'Махалля 4: рейтинг/скор', labelUz: 'Mahalla 4: reyting/skor', unit: 'балл' },
      { key: 's20_13', label: 'Махалля 5: количество кредитов', labelUz: 'Mahalla 5: kreditlar soni', unit: 'шт.' },
      { key: 's20_14', label: 'Махалля 5: рейтинг/скор', labelUz: 'Mahalla 5: reyting/skor', unit: 'балл' },
      { key: 's20_15', label: 'Махалля 1: название', labelUz: 'Mahalla 1: nomi', unit: 'текст' },
      { key: 's20_16', label: 'Махалля 1: ремесленных мастерских', labelUz: 'Mahalla 1: hunarmandchilik ustaxonalari', unit: 'шт.' },
      { key: 's20_17', label: 'Махалля 1: объём ремесл. производства', labelUz: 'Mahalla 1: hunarmandchilik ishlab chiqarish hajmi', unit: 'млрд сум' },
      { key: 's20_18', label: 'Махалля 2: название', labelUz: 'Mahalla 2: nomi', unit: 'текст' },
      { key: 's20_19', label: 'Махалля 2: ремесленных мастерских', labelUz: 'Mahalla 2: hunarmandchilik ustaxonalari', unit: 'шт.' },
      { key: 's20_20', label: 'Махалля 2: объём ремесл. производства', labelUz: 'Mahalla 2: hunarmandchilik ishlab chiqarish hajmi', unit: 'млрд сум' },
      { key: 's20_21', label: 'Махалля 3: название', labelUz: 'Mahalla 3: nomi', unit: 'текст' },
      { key: 's20_22', label: 'Махалля 3: ремесленных мастерских', labelUz: 'Mahalla 3: hunarmandchilik ustaxonalari', unit: 'шт.' },
      { key: 's20_23', label: 'Махалля 3: объём ремесл. производства', labelUz: 'Mahalla 3: hunarmandchilik ishlab chiqarish hajmi', unit: 'млрд сум' },
      { key: 's20_24', label: 'Махалля 4: название', labelUz: 'Mahalla 4: nomi', unit: 'текст' },
      { key: 's20_25', label: 'Махалля 4: ремесленных мастерских', labelUz: 'Mahalla 4: hunarmandchilik ustaxonalari', unit: 'шт.' },
      { key: 's20_26', label: 'Махалля 4: объём ремесл. производства', labelUz: 'Mahalla 4: hunarmandchilik ishlab chiqarish hajmi', unit: 'млрд сум' },
      { key: 's20_27', label: 'Махалля 5: название', labelUz: 'Mahalla 5: nomi', unit: 'текст' },
      { key: 's20_28', label: 'Махалля 5: ремесленных мастерских', labelUz: 'Mahalla 5: hunarmandchilik ustaxonalari', unit: 'шт.' },
      { key: 's20_29', label: 'Махалля 5: объём ремесл. производства', labelUz: 'Mahalla 5: hunarmandchilik ishlab chiqarish hajmi', unit: 'млрд сум' },
    ],
  },
  {
    n: 21, title: 'Критические проблемы инфраструктуры', titleUz: 'Kritik infratuzilma muammolari', icon: 'warning',
    attrs: [
      { key: 's21_1', label: 'Проблема 1: название', labelUz: 'Muammo 1: nomi', unit: 'текст' },
      { key: 's21_2', label: 'Проблема 1: приоритет (выс/ср/низ)', labelUz: 'Muammo 1: prioritet (yuq/oʻrta/past)', unit: 'текст' },
      { key: 's21_3', label: 'Проблема 1: стоимость решения', labelUz: 'Muammo 1: yechim qiymati', unit: 'млрд сум' },
      { key: 's21_4', label: 'Проблема 2: название', labelUz: 'Muammo 2: nomi', unit: 'текст' },
      { key: 's21_5', label: 'Проблема 2: приоритет (выс/ср/низ)', labelUz: 'Muammo 2: prioritet (yuq/oʻrta/past)', unit: 'текст' },
      { key: 's21_6', label: 'Проблема 2: стоимость решения', labelUz: 'Muammo 2: yechim qiymati', unit: 'млрд сум' },
      { key: 's21_7', label: 'Проблема 3: название', labelUz: 'Muammo 3: nomi', unit: 'текст' },
      { key: 's21_8', label: 'Проблема 3: приоритет (выс/ср/низ)', labelUz: 'Muammo 3: prioritet (yuq/oʻrta/past)', unit: 'текст' },
      { key: 's21_9', label: 'Проблема 3: стоимость решения', labelUz: 'Muammo 3: yechim qiymati', unit: 'млрд сум' },
      { key: 's21_10', label: 'Проблема 4: название', labelUz: 'Muammo 4: nomi', unit: 'текст' },
      { key: 's21_11', label: 'Проблема 4: приоритет (выс/ср/низ)', labelUz: 'Muammo 4: prioritet (yuq/oʻrta/past)', unit: 'текст' },
      { key: 's21_12', label: 'Проблема 4: стоимость решения', labelUz: 'Muammo 4: yechim qiymati', unit: 'млрд сум' },
      { key: 's21_13', label: 'Проблема 5: название', labelUz: 'Muammo 5: nomi', unit: 'текст' },
      { key: 's21_14', label: 'Проблема 5: приоритет (выс/ср/низ)', labelUz: 'Muammo 5: prioritet (yuq/oʻrta/past)', unit: 'текст' },
      { key: 's21_15', label: 'Проблема 5: стоимость решения', labelUz: 'Muammo 5: yechim qiymati', unit: 'млрд сум' },
    ],
  },
]

export const CITY_TOTAL_FIELDS = CITY_SECTIONS.reduce(
  (n, s) => n + s.attrs.length,
  0,
)

export const CITY_TABS = [
  { id: 'basic', num: '01', icon: 'badge', label: 'Базовая', sections: [1] },
  { id: 'economy', num: '02', icon: 'finance', label: 'Экономика', sections: [2, 3, 4, 5, 6, 7] },
  { id: 'people', num: '03', icon: 'groups', label: 'Население', sections: [8, 9, 11] },
  { id: 'social', num: '04', icon: 'school', label: 'Соц-инфра', sections: [10, 14, 15, 16, 17] },
  { id: 'finance', num: '05', icon: 'account_balance_wallet', label: 'Финансы и цифра', sections: [12, 13, 19, 20] },
  { id: 'mahalla', num: '06', icon: 'storefront', label: 'Махалля и среда', sections: [18, 21] },
]

export function tabSections(tabId) {
  const tab = CITY_TABS.find((t) => t.id === tabId)
  if (!tab) return []
  return tab.sections
    .map((n) => CITY_SECTIONS.find((s) => s.n === n))
    .filter(Boolean)
}
