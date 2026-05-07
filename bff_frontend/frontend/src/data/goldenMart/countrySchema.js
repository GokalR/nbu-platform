/**
 * Golden Mart — country schema.
 *
 * AUTO-GENERATED from goldenmarts/GM_country.md (which itself is
 * generated from goldenmarts/golden_mart_country.xlsx via _to_md.py).
 * Do not hand-edit. To change: edit the Excel, run _to_md.py, then
 * goldenmarts/_md_to_schema_js.py. Bilingual labels come from
 * goldenmarts/_translations_uz.json — missing keys fall back to RU.
 *
 * Per-entity data files reference fields by `key` (positional s{section}_{index}).
 */

export const COUNTRY_SECTIONS = [
  {
    n: 1, title: 'Базовая информация', titleUz: 'Asosiy maʼlumotlar', icon: 'badge',
    attrs: [
      { key: 's1_1', label: 'Название', labelUz: 'Nomi', unit: 'текст' },
      { key: 's1_2', label: 'Административный центр', labelUz: 'Maʼmuriy markaz', unit: 'текст' },
      { key: 's1_3', label: 'Площадь', labelUz: 'Maydon', unit: 'тыс. км²' },
      { key: 's1_4', label: 'Областей (вилоятов)', labelUz: 'Viloyatlar', unit: 'областей' },
      { key: 's1_5', label: 'Городов областного подчинения', labelUz: 'Viloyat boʻysinuvidagi shaharlar', unit: 'городов' },
      { key: 's1_6', label: 'Районов (туманов)', labelUz: 'Tumanlar', unit: 'районов' },
      { key: 's1_7', label: 'Махаллей', labelUz: 'Mahallalar', unit: 'махаллей' },
      { key: 's1_8', label: 'Население постоянное', labelUz: 'Doimiy aholi', unit: 'млн чел.' },
      { key: 's1_9', label: 'Мужчин', labelUz: 'Erkaklar', unit: 'млн чел.' },
      { key: 's1_10', label: 'Женщин', labelUz: 'Ayollar', unit: 'млн чел.' },
      { key: 's1_11', label: 'Городское население', labelUz: 'Shahar aholisi', unit: 'млн чел.' },
      { key: 's1_12', label: 'Сельское население', labelUz: 'Qishloq aholisi', unit: 'млн чел.' },
      { key: 's1_13', label: 'Население 0–14 лет', labelUz: '0–14 yosh aholisi', unit: 'млн чел.' },
      { key: 's1_14', label: 'Население 15–64 лет', labelUz: '15–64 yosh aholisi', unit: 'млн чел.' },
      { key: 's1_15', label: 'Население 65+ лет', labelUz: '65+ yosh aholisi', unit: 'млн чел.' },
      { key: 's1_16', label: 'Семей', labelUz: 'Oilalar', unit: 'млн' },
      { key: 's1_17', label: 'Домохозяйств', labelUz: 'Xonadonlar', unit: 'млн' },
    ],
  },
  {
    n: 2, title: 'Экономика – объёмы', titleUz: 'Iqtisodiyot – hajmlar', icon: 'finance',
    attrs: [
      { key: 's2_1', label: 'ВВП (валовой внутренний продукт)', labelUz: 'YaIM (yalpi ichki mahsulot)', unit: 'трлн сум' },
      { key: 's2_2', label: 'Промышленность – объём', labelUz: 'Sanoat – hajmi', unit: 'трлн сум' },
      { key: 's2_3', label: 'Услуги – объём', labelUz: 'Xizmatlar – hajmi', unit: 'трлн сум' },
      { key: 's2_4', label: 'Розничная торговля – объём', labelUz: 'Chakana savdo – hajmi', unit: 'трлн сум' },
      { key: 's2_5', label: 'Строительство – объём', labelUz: 'Qurilish – hajmi', unit: 'трлн сум' },
      { key: 's2_6', label: 'Сельское хозяйство – объём', labelUz: 'Qishloq xoʻjaligi – hajmi', unit: 'трлн сум' },
      { key: 's2_7', label: 'Инвестиции в основной капитал', labelUz: 'Asosiy kapitalga investitsiyalar', unit: 'трлн сум' },
    ],
  },
  {
    n: 3, title: 'Бюджет', titleUz: 'Byudjet', icon: 'account_balance',
    attrs: [
      { key: 's3_1', label: 'Доходы бюджета – всего', labelUz: 'Byudjet daromadlari – jami', unit: 'трлн сум' },
      { key: 's3_2', label: 'Налоговые поступления', labelUz: 'Soliq tushumlari', unit: 'трлн сум' },
      { key: 's3_3', label: 'Неналоговые доходы', labelUz: 'Nosoliq daromadlar', unit: 'трлн сум' },
      { key: 's3_4', label: 'Трансферты из вышестоящ. бюджета', labelUz: 'Yuqori byudjetdan transfertlar', unit: 'трлн сум' },
      { key: 's3_5', label: 'Расходы бюджета – всего', labelUz: 'Byudjet xarajatlari – jami', unit: 'трлн сум' },
      { key: 's3_6', label: 'Социальная сфера', labelUz: 'Ijtimoiy soha', unit: 'трлн сум' },
      { key: 's3_7', label: 'Инфраструктура и экономика', labelUz: 'Infratuzilma va iqtisodiyot', unit: 'трлн сум' },
      { key: 's3_8', label: 'Управление и прочее', labelUz: 'Boshqaruv va boshqalar', unit: 'трлн сум' },
      { key: 's3_9', label: 'Дефицит / Профицит бюджета', labelUz: 'Byudjet defitsiti / profitsiti', unit: 'трлн сум' },
      { key: 's3_10', label: 'Государственный долг', labelUz: 'Государственный долг', unit: 'трлн сум' },
    ],
  },
  {
    n: 4, title: 'Внешняя торговля', titleUz: 'Tashqi savdo', icon: 'public',
    attrs: [
      { key: 's4_1', label: 'Товарооборот', labelUz: 'Tovar aylanmasi', unit: 'млн USD' },
      { key: 's4_2', label: 'Экспорт', labelUz: 'Eksport', unit: 'млн USD' },
      { key: 's4_3', label: 'Импорт', labelUz: 'Import', unit: 'млн USD' },
      { key: 's4_4', label: 'Сальдо торговли (экспорт − импорт)', labelUz: 'Savdo saldosi (eksport − import)', unit: 'млн USD' },
    ],
  },
  {
    n: 5, title: 'Основные торговые партнёры', titleUz: 'Asosiy savdo hamkorlari', icon: 'flag',
    attrs: [
      { key: 's5_1', label: 'Экспорт – страна 1: название', labelUz: 'Eksport – mamlakat 1: nomi', unit: 'текст' },
      { key: 's5_2', label: 'Экспорт – страна 1: объём', labelUz: 'Eksport – mamlakat 1: hajmi', unit: 'млн USD' },
      { key: 's5_3', label: 'Экспорт – страна 2: название', labelUz: 'Eksport – mamlakat 2: nomi', unit: 'текст' },
      { key: 's5_4', label: 'Экспорт – страна 2: объём', labelUz: 'Eksport – mamlakat 2: hajmi', unit: 'млн USD' },
      { key: 's5_5', label: 'Экспорт – страна 3: название', labelUz: 'Eksport – mamlakat 3: nomi', unit: 'текст' },
      { key: 's5_6', label: 'Экспорт – страна 3: объём', labelUz: 'Eksport – mamlakat 3: hajmi', unit: 'млн USD' },
      { key: 's5_7', label: 'Импорт – страна 1: название', labelUz: 'Import – mamlakat 1: nomi', unit: 'текст' },
      { key: 's5_8', label: 'Импорт – страна 1: объём', labelUz: 'Import – mamlakat 1: hajmi', unit: 'млн USD' },
      { key: 's5_9', label: 'Импорт – страна 2: название', labelUz: 'Import – mamlakat 2: nomi', unit: 'текст' },
      { key: 's5_10', label: 'Импорт – страна 2: объём', labelUz: 'Import – mamlakat 2: hajmi', unit: 'млн USD' },
      { key: 's5_11', label: 'Импорт – страна 3: название', labelUz: 'Import – mamlakat 3: nomi', unit: 'текст' },
      { key: 's5_12', label: 'Импорт – страна 3: объём', labelUz: 'Import – mamlakat 3: hajmi', unit: 'млн USD' },
    ],
  },
  {
    n: 6, title: 'Инвестиции по источникам', titleUz: 'Manba boʻyicha investitsiyalar', icon: 'savings',
    attrs: [
      { key: 's6_1', label: 'Собственные средства предприятий', labelUz: 'Korxonalarning oʻz mablagʻlari', unit: 'трлн сум' },
      { key: 's6_2', label: 'Иностранные инвестиции', labelUz: 'Xorijiy investitsiyalar', unit: 'трлн сум' },
      { key: 's6_3', label: 'Госбюджет', labelUz: 'Davlat byudjeti', unit: 'трлн сум' },
      { key: 's6_4', label: 'Банковские кредиты', labelUz: 'Bank kreditlari', unit: 'трлн сум' },
      { key: 's6_5', label: 'Средства населения', labelUz: 'Aholi mablagʻlari', unit: 'трлн сум' },
      { key: 's6_6', label: 'Фонд реконструкции', labelUz: 'Rekonstruksiya jamgʻarmasi', unit: 'трлн сум' },
    ],
  },
  {
    n: 7, title: 'Предпринимательство', titleUz: 'Tadbirkorlik', icon: 'storefront',
    attrs: [
      { key: 's7_1', label: 'Активных субъектов – всего', labelUz: 'Faol subʼyektlar – jami', unit: 'тыс.' },
      { key: 's7_2', label: 'ООО', labelUz: 'MChJ', unit: 'тыс.' },
      { key: 's7_3', label: 'ИП (ЯТТ)', labelUz: 'YaTT', unit: 'тыс.' },
      { key: 's7_4', label: 'Фермерские хозяйства', labelUz: 'Fermer xoʻjaliklari', unit: 'тыс.' },
      { key: 's7_5', label: 'Прочие', labelUz: 'Boshqalar', unit: 'тыс.' },
      { key: 's7_6', label: 'Неактивных (приостановл.)', labelUz: 'Faolmas (toʻxtatilgan)', unit: 'тыс.' },
      { key: 's7_7', label: 'Открыто новых за год', labelUz: 'Yil davomida yangi ochilgan', unit: 'тыс.' },
      { key: 's7_8', label: 'Закрыто за год', labelUz: 'Yil davomida yopilgan', unit: 'тыс.' },
      { key: 's7_9', label: 'Предприятий-экспортёров', labelUz: 'Eksport korxonalari', unit: 'шт.' },
    ],
  },
  {
    n: 8, title: 'Рынок труда', titleUz: 'Mehnat bozori', icon: 'work',
    attrs: [
      { key: 's8_1', label: 'Экономически активное население', labelUz: 'Iqtisodiy faol aholi', unit: 'млн чел.' },
      { key: 's8_2', label: 'Официально занятых', labelUz: 'Rasmiy bandlar', unit: 'млн чел.' },
      { key: 's8_3', label: 'Неофициально занятых', labelUz: 'Norasmiy bandlar', unit: 'млн чел.' },
      { key: 's8_4', label: 'Безработных', labelUz: 'Ishsizlar', unit: 'тыс. чел.' },
      { key: 's8_5', label: 'Уровень безработицы', labelUz: 'Ishsizlik darajasi', unit: '%' },
      { key: 's8_6', label: 'Создано новых рабочих мест за год', labelUz: 'Yil davomida yaratilgan yangi ish oʻrinlari', unit: 'тыс. раб. мест' },
      { key: 's8_7', label: 'Трудовых мигрантов за рубежом', labelUz: 'Chet eldagi mehnat migrantlari', unit: 'млн чел.' },
      { key: 's8_8', label: 'Средняя номинальная зарплата – всего', labelUz: 'Oʻrtacha nominal ish haqi – jami', unit: 'тыс. сум/мес' },
      { key: 's8_9', label: 'в промышленности', labelUz: 'sanoatda', unit: 'тыс. сум/мес' },
      { key: 's8_10', label: 'в услугах', labelUz: 'xizmatlarda', unit: 'тыс. сум/мес' },
      { key: 's8_11', label: 'в торговле', labelUz: 'savdoda', unit: 'тыс. сум/мес' },
      { key: 's8_12', label: 'в строительстве', labelUz: 'qurilishda', unit: 'тыс. сум/мес' },
      { key: 's8_13', label: 'в бюджетной сфере', labelUz: 'byudjet sohasida', unit: 'тыс. сум/мес' },
      { key: 's8_14', label: 'в сельском хозяйстве', labelUz: 'qishloq xoʻjaligida', unit: 'тыс. сум/мес' },
    ],
  },
  {
    n: 9, title: 'Бедность и социальная сфера', titleUz: 'Kambagʻallik va ijtimoiy soha', icon: 'volunteer_activism',
    attrs: [
      { key: 's9_1', label: 'Семей в Социальном реестре', labelUz: 'Ijtimoiy reyestrdagi oilalar', unit: 'млн' },
      { key: 's9_2', label: 'Семей в бедности на начало года', labelUz: 'Yil boshida kambagʻal oilalar', unit: 'млн' },
      { key: 's9_3', label: 'Семей в бедности на конец года', labelUz: 'Yil oxirida kambagʻal oilalar', unit: 'млн' },
      { key: 's9_4', label: 'Покрытие Соц. реестром (от семей в бедности нач. года), %', labelUz: 'Ijt. reyestr qamrovi (yil boshidagi kambagʻal oilalardan), %', unit: '%' },
      { key: 's9_5', label: 'Пенсионеров', labelUz: 'Пенсионеров', unit: 'млн чел.' },
      { key: 's9_6', label: 'Родившихся за год', labelUz: 'Yil davomida tugʻilganlar', unit: 'тыс. чел.' },
      { key: 's9_7', label: 'Умерших за год', labelUz: 'Yil davomida vafot etganlar', unit: 'тыс. чел.' },
      { key: 's9_8', label: 'Эмиграция', labelUz: 'Emigratsiya', unit: 'тыс. чел.' },
      { key: 's9_9', label: 'Иммиграция', labelUz: 'Immigratsiya', unit: 'тыс. чел.' },
      { key: 's9_10', label: 'Заключено браков за год', labelUz: 'Yil davomida tuzilgan nikohlar', unit: 'тыс. браков' },
      { key: 's9_11', label: 'Разводов за год', labelUz: 'Yil davomida ajralishlar', unit: 'тыс. разводов' },
    ],
  },
  {
    n: 10, title: 'Образование', titleUz: 'Taʼlim', icon: 'school',
    attrs: [
      { key: 's10_1', label: 'Школ (общеобразовательных)', labelUz: 'Maktablar (umumtaʼlim)', unit: 'тыс.' },
      { key: 's10_2', label: 'Учеников в школах', labelUz: 'Maktab oʻquvchilari', unit: 'млн' },
      { key: 's10_3', label: 'Учителей', labelUz: 'Oʻqituvchilar', unit: 'тыс.' },
      { key: 's10_4', label: 'Колледжей / техникумов', labelUz: 'Kollejlar / texnikumlar', unit: 'шт.' },
      { key: 's10_5', label: 'Студентов в колледжах', labelUz: 'Kollej talabalari', unit: 'тыс.' },
      { key: 's10_6', label: 'Вузов', labelUz: 'OTM', unit: 'шт.' },
      { key: 's10_7', label: 'Студентов в вузах', labelUz: 'OTM talabalari', unit: 'тыс.' },
      { key: 's10_8', label: 'Детских садов (МТМ)', labelUz: 'Bolalar bogʻchalari (MTM)', unit: 'тыс.' },
      { key: 's10_9', label: 'Детей в детсадах', labelUz: 'Bogʻchadagi bolalar', unit: 'млн' },
    ],
  },
  {
    n: 11, title: 'Здравоохранение', titleUz: 'Sogʻliqni saqlash', icon: 'local_hospital',
    attrs: [
      { key: 's11_1', label: 'Больниц', labelUz: 'Shifoxonalar', unit: 'тыс.' },
      { key: 's11_2', label: 'Поликлиник / ЦРП', labelUz: 'Poliklinikalar / TRP', unit: 'тыс.' },
      { key: 's11_3', label: 'Койко-мест', labelUz: 'Oʻrin-joylar', unit: 'тыс.' },
      { key: 's11_4', label: 'Врачей', labelUz: 'Shifokorlar', unit: 'тыс.' },
      { key: 's11_5', label: 'Медсестёр и ср. мед. персонала', labelUz: 'Hamshira va oʻrta tibbiy xodimlar', unit: 'тыс.' },
      { key: 's11_6', label: 'Младенческая смертность (на 1000 родившихся)', labelUz: 'Goʻdaklar oʻlimi (1000 tugʻilganga)', unit: '‰' },
    ],
  },
  {
    n: 12, title: 'Банковский сектор', titleUz: 'Bank sektori', icon: 'account_balance_wallet',
    attrs: [
      { key: 's12_1', label: 'Кредитный портфель – всего', labelUz: 'Kredit portfeli – jami', unit: 'трлн сум' },
      { key: 's12_2', label: 'Кредиты МСБ', labelUz: 'KOB kreditlari', unit: 'трлн сум' },
      { key: 's12_3', label: 'Кредиты экспортёрам', labelUz: 'Eksportyorlarga kreditlar', unit: 'трлн сум' },
      { key: 's12_4', label: 'Кредиты физлицам', labelUz: 'Jismoniy shaxslarga kreditlar', unit: 'трлн сум' },
      { key: 's12_5', label: 'в т.ч. ипотечные / ИЖС', labelUz: 'shu jumladan ipoteka / IUQ', unit: 'трлн сум' },
      { key: 's12_6', label: 'Прочие кредиты', labelUz: 'Boshqa kreditlar', unit: 'трлн сум' },
      { key: 's12_7', label: 'Выдано кредитов за год', labelUz: 'Выдано кредитов за год', unit: 'трлн сум' },
      { key: 's12_8', label: 'Депозитный портфель – всего', labelUz: 'Depozit portfeli – jami', unit: 'трлн сум' },
      { key: 's12_9', label: 'Депозиты юр. лиц', labelUz: 'Yur. shaxs depozitlari', unit: 'трлн сум' },
      { key: 's12_10', label: 'Депозиты физ. лиц', labelUz: 'Jis. shaxs depozitlari', unit: 'трлн сум' },
      { key: 's12_11', label: 'Просроченная задолженность (NPL)', labelUz: 'Muddati oʻtgan qarz (NPL)', unit: 'трлн сум' },
    ],
  },
  {
    n: 13, title: 'Туризм', titleUz: 'Turizm', icon: 'travel_explore',
    attrs: [
      { key: 's13_1', label: 'Иностранных туристов', labelUz: 'Xorijiy turistlar', unit: 'млн чел.' },
      { key: 's13_2', label: 'Внутренних туристов', labelUz: 'Mahalliy turistlar', unit: 'млн чел.' },
      { key: 's13_3', label: 'Объектов размещения', labelUz: 'Joylashtirish obyektlari', unit: 'тыс.' },
      { key: 's13_4', label: 'Номеров в объектах размещения', labelUz: 'Joylashtirish obyektlari xonalari', unit: 'тыс.' },
      { key: 's13_5', label: 'Ночёвок за год', labelUz: 'Ночёвок за год', unit: 'млн' },
      { key: 's13_6', label: 'Доход от туризма (иностр. туристов)', labelUz: 'Turizm daromadi (xorijiy)', unit: 'млн USD' },
      { key: 's13_7', label: 'Доход от туризма (внутр. туристов)', labelUz: 'Turizm daromadi (mahalliy)', unit: 'млрд сум' },
    ],
  },
  {
    n: 14, title: 'Жильё', titleUz: 'Uy-joy', icon: 'home',
    attrs: [
      { key: 's14_1', label: 'Жилой фонд – всего', labelUz: 'Uy-joy fondi – jami', unit: 'млн м²' },
      { key: 's14_2', label: 'Введено жилья за год', labelUz: 'Yil davomida foydalanishga topshirilgan', unit: 'млн м²' },
      { key: 's14_3', label: 'Многоквартирных домов', labelUz: 'Koʻp xonadonli uylar', unit: 'тыс.' },
      { key: 's14_4', label: 'Частных домов', labelUz: 'Xususiy uylar', unit: 'млн' },
      { key: 's14_5', label: 'Аварийного жилья', labelUz: 'Avariya uylar', unit: 'млн м²' },
      { key: 's14_6', label: 'Доля аварийного жилья, %', labelUz: 'Avariya uylar ulushi, %', unit: '%' },
    ],
  },
  {
    n: 15, title: 'Инфраструктура – подключения и сети', titleUz: 'Infratuzilma – ulanishlar va tarmoqlar', icon: 'hub',
    attrs: [
      { key: 's15_1', label: 'Подключено к электричеству', labelUz: 'Elektrga ulangan', unit: 'млн' },
      { key: 's15_2', label: 'Охват электричеством, %', labelUz: 'Elektr qamrovi, %', unit: '%' },
      { key: 's15_3', label: 'Подключено к водопроводу', labelUz: 'Suvga ulangan', unit: 'млн' },
      { key: 's15_4', label: 'Охват водопроводом, %', labelUz: 'Suv qamrovi, %', unit: '%' },
      { key: 's15_5', label: 'Подключено к канализации', labelUz: 'Подключено к канализации', unit: 'млн' },
      { key: 's15_6', label: 'Охват канализацией, %', labelUz: 'Kanalizatsiya qamrovi, %', unit: '%' },
      { key: 's15_7', label: 'Подключено к газу', labelUz: 'Gazga ulangan', unit: 'млн' },
      { key: 's15_8', label: 'Охват газом, %', labelUz: 'Gaz qamrovi, %', unit: '%' },
      { key: 's15_9', label: 'Трансформаторных подстанций', labelUz: 'Трансформаторных подстанций', unit: 'тыс.' },
      { key: 's15_10', label: 'Скважин водоснабжения', labelUz: 'Скважин водоснабжения', unit: 'тыс.' },
      { key: 's15_11', label: 'Очистных сооружений', labelUz: 'Очистных сооружений', unit: 'шт.' },
    ],
  },
  {
    n: 16, title: 'Дороги', titleUz: 'Yoʻllar', icon: 'route',
    attrs: [
      { key: 's16_1', label: 'Дороги – всего', labelUz: 'Yoʻllar – jami', unit: 'тыс. км' },
      { key: 's16_2', label: 'Асфальтированные', labelUz: 'Asfaltlangan', unit: 'тыс. км' },
      { key: 's16_3', label: 'Доля асфальтированных дорог, %', labelUz: 'Asfaltlangan yoʻllar ulushi, %', unit: '%' },
      { key: 's16_4', label: 'Щебень / гравий', labelUz: 'Щебень / гравий', unit: 'тыс. км' },
      { key: 's16_5', label: 'Грунтовые', labelUz: 'Tuproq yoʻllar', unit: 'тыс. км' },
      { key: 's16_6', label: 'В хорошем состоянии', labelUz: 'Yaxshi holatda', unit: 'тыс. км' },
      { key: 's16_7', label: 'Доля дорог в хорошем состоянии, %', labelUz: 'Yaxshi holatdagi yoʻllar ulushi, %', unit: '%' },
      { key: 's16_8', label: 'Требуют ремонта', labelUz: 'Taʼmir talab qiladi', unit: 'тыс. км' },
      { key: 's16_9', label: 'Требуют капитального ремонта', labelUz: 'Kapital taʼmir talab qiladi', unit: 'тыс. км' },
    ],
  },
  {
    n: 19, title: 'Цифровизация', titleUz: 'Raqamlashtirish', icon: 'devices',
    attrs: [
      { key: 's19_1', label: 'Онлайн-платежи (транзакций в год)', labelUz: 'Onlayn toʻlovlar (yiliga tranzaksiya)', unit: 'млрд' },
      { key: 's19_2', label: 'POS-терминалы (торговцев подключено)', labelUz: 'POS-терминалы (торговцев подключено)', unit: 'тыс.' },
      { key: 's19_3', label: 'Онлайн-кредитов выдано за год', labelUz: 'Yil davomida onlayn kreditlar berildi', unit: 'тыс.' },
      { key: 's19_4', label: 'Покрытие 4G (по площади территории)', labelUz: '4G qamrovi (hudud maydoni boʻyicha)', unit: '%' },
      { key: 's19_5', label: 'ВВП', labelUz: 'ВВП', unit: 'Валовой внутренний продукт. Сумма стоимости всех товаров и услуг, произведённых на территории страны за год.' },
      { key: 's19_6', label: 'ВРП', labelUz: 'ВРП', unit: 'Валовой региональный продукт. То же, что ВВП, но в разрезе одной области.' },
      { key: 's19_7', label: 'ВТП', labelUz: 'ВТП', unit: 'Валовой территориальный продукт. То же, что ВВП, но в разрезе одного города или тумана.' },
      { key: 's19_8', label: 'Возрастная структура', labelUz: 'Возрастная структура', unit: 'Распределение населения по группам: 0–14, 15–64, 65+ лет.' },
      { key: 's19_9', label: 'Дефицит бюджета', labelUz: 'Дефицит бюджета', unit: 'Превышение расходов над доходами. Профицит – обратная ситуация.' },
      { key: 's19_10', label: 'Семья', labelUz: 'Семья', unit: 'Лица, связанные родством или браком. Могут жить раздельно.' },
      { key: 's19_11', label: 'Домохозяйство', labelUz: 'Домохозяйство', unit: 'Лица, живущие в одном жилье и ведущие общий быт. Один человек – тоже домохозяйство.' },
      { key: 's19_12', label: 'Активный субъект', labelUz: 'Активный субъект', unit: 'Юр. лицо или ИП, ведущий деятельность и сдающий отчётность.' },
      { key: 's19_13', label: 'МСБ', labelUz: 'МСБ', unit: 'Малый и средний бизнес по узбекскому законодательству.' },
      { key: 's19_14', label: 'ЯТТ', labelUz: 'ЯТТ', unit: 'Якка тартибдаги тадбиркор – индивидуальный предприниматель.' },
      { key: 's19_15', label: 'Предприятие-экспортёр', labelUz: 'Предприятие-экспортёр', unit: 'Субъект, хотя бы раз осуществивший экспорт в отчётном году.' },
      { key: 's19_16', label: 'Экономически активное население', labelUz: 'Iqtisodiy faol aholi', unit: 'Лица 15+ лет, работающие или ищущие работу.' },
      { key: 's19_17', label: 'Официально занятые', labelUz: 'Официально занятые', unit: 'С трудовым договором или зарегистрированные ИП/самозанятые.' },
      { key: 's19_18', label: 'Неофициально занятые', labelUz: 'Неофициально занятые', unit: 'Работающие без официальной регистрации (оценка Госкомстата).' },
      { key: 's19_19', label: 'Социальный реестр', labelUz: 'Социальный реестр', unit: 'Единая база нуждающихся семей, получающих гос. помощь.' },
      { key: 's19_20', label: 'Эмиграция / Иммиграция', labelUz: 'Эмиграция / Иммиграция', unit: 'Выезд / прибытие на ПМЖ за год.' },
      { key: 's19_21', label: 'Младенческая смертность', labelUz: 'Младенческая смертность', unit: 'Число смертей детей до 1 года на 1000 родившихся живыми (‰).' },
      { key: 's19_22', label: 'Кредитный портфель', labelUz: 'Кредитный портфель', unit: 'Сумма выданных и непогашенных кредитов на конец года.' },
      { key: 's19_23', label: 'Ипотечные / ИЖС', labelUz: 'Ипотечные / ИЖС', unit: 'Кредиты на жильё и индивидуальное жилищное строительство.' },
      { key: 's19_24', label: 'NPL', labelUz: 'NPL', unit: 'Non-Performing Loans – кредиты с просрочкой более 90 дней.' },
      { key: 's19_25', label: 'Депозитный портфель', labelUz: 'Депозитный портфель', unit: 'Сумма всех вкладов физ. и юр. лиц на конец года.' },
      { key: 's19_26', label: 'Жилой фонд', labelUz: 'Жилой фонд', unit: 'Общая площадь всех жилых помещений.' },
      { key: 's19_27', label: 'Введено жилья', labelUz: 'Введено жилья', unit: 'Площадь жилья, введённого в эксплуатацию по актам ввода.' },
      { key: 's19_28', label: 'Аварийное жильё', labelUz: 'Аварийное жильё', unit: 'Официально признанное непригодным для проживания.' },
      { key: 's19_29', label: 'Доля аварийного жилья, %', labelUz: 'Avariya uylar ulushi, %', unit: 'Аварийное жильё ÷ жилой фонд × 100. Считается автоматически.' },
      { key: 's19_30', label: 'Охват электр./водопр./канализ./газ, %', labelUz: 'Охват электр./водопр./канализ./газ, %', unit: 'Подключённые домохозяйства ÷ всего домохозяйств × 100. Считается автоматически.' },
      { key: 's19_31', label: 'Доля дорог в хорошем состоянии, %', labelUz: 'Yaxshi holatdagi yoʻllar ulushi, %', unit: 'Дороги в хорошем состоянии ÷ все дороги × 100. Считается автоматически.' },
      { key: 's19_32', label: 'Доля асфальтированных дорог, %', labelUz: 'Asfaltlangan yoʻllar ulushi, %', unit: 'Асфальтированные дороги ÷ все дороги × 100. Считается автоматически.' },
      { key: 's19_33', label: 'Покрытие 4G', labelUz: 'Покрытие 4G', unit: 'Процент территории с сетью 4G LTE.' },
      { key: 's19_34', label: 'Ночёвки', labelUz: 'Ночёвки', unit: 'Человеко-ночи в объектах размещения. 1 турист × 3 ночи = 3 ночёвки.' },
      { key: 's19_35', label: 'МТМ', labelUz: 'МТМ', unit: 'Мактабгача таълим муассасаси – детский сад.' },
      { key: 's19_36', label: 'Махалля', labelUz: 'Махалля', unit: 'Орган самоуправления и территориальная единица в Узбекистане.' },
      { key: 's19_37', label: 'ТБО', labelUz: 'ТБО', unit: 'Твёрдые бытовые отходы.' },
      { key: 's19_38', label: 'План 2026', labelUz: 'План 2026', unit: 'Целевое значение показателя на конец 2026 года.' },
      { key: 's19_39', label: 'н/д', labelUz: 'н/д', unit: 'Нет данных. Лучше этого, чем 0.' },
    ],
  },
]

export const COUNTRY_TOTAL_FIELDS = COUNTRY_SECTIONS.reduce(
  (n, s) => n + s.attrs.length,
  0,
)

export const COUNTRY_TABS = [
  { id: 'basic', num: '01', icon: 'badge', label: 'Базовая', sections: [1] },
  { id: 'economy', num: '02', icon: 'finance', label: 'Экономика', sections: [2, 3, 4, 5, 6, 7] },
  { id: 'people', num: '03', icon: 'groups', label: 'Население', sections: [8, 9, 11] },
  { id: 'social', num: '04', icon: 'school', label: 'Соц-инфра', sections: [10, 14, 15, 16, 17] },
  { id: 'finance', num: '05', icon: 'account_balance_wallet', label: 'Финансы и цифра', sections: [12, 13, 19, 20] },
  { id: 'mahalla', num: '06', icon: 'storefront', label: 'Махалля и среда', sections: [18, 21] },
]

export function tabSections(tabId) {
  const tab = COUNTRY_TABS.find((t) => t.id === tabId)
  if (!tab) return []
  return tab.sections
    .map((n) => COUNTRY_SECTIONS.find((s) => s.n === n))
    .filter(Boolean)
}
