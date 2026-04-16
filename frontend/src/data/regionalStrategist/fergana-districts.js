/**
 * Fergana region — textile industry opportunity map.
 *
 * Data sources:
 *   Population:  citypopulation.de 2025 estimates (stat.uz census-based)
 *   Enterprises: stat.uz reports 855 textile enterprises in Fergana region
 *                (Jan-Oct 2021). District breakdown estimated proportionally.
 *   Margilan:    Yodgorlik (2 000+ workers), Margilan Silk Factory (15 000
 *                workers, 22 mln m² silk/yr), 600 craftsmen at handicraft
 *                center, 1 000+ artisan families.
 *   Qo'shtepa:   Innovative Apparel — $15M FDI, H&M contract, 3 500 jobs.
 *   Fergana city: Global Textile LLC (62 000 t knitwear for Kiabi), SEZ.
 *
 * Ported from NBU-business-analysis/lib/fergana-districts.ts
 */
export const FERGANA_DISTRICTS = [
  { id: 'margilon',   name: 'Марғилон ш.',  score: 95, population: 257_878, businesses: 180, competition: 'высокая', verdict: 'Столица шёлка Узбекистана. Yodgorlik (2 000+ рабочих), Маргиланская шёлковая фабрика (15 000 рабочих, 22 млн м²/год). 1 000+ семей-ремесленников.' },
  { id: 'fargona',    name: 'Фарғона ш.',   score: 88, population: 328_409, businesses: 150, competition: 'высокая', verdict: 'Региональный центр. Global Textile (62 000 т трикотажа для Kiabi). СЭЗ «Фергана», развитая логистика.' },
  { id: 'quva',       name: 'Қува',         score: 76, population: 280_720, businesses: 75,  competition: 'средняя', verdict: 'Шелководческий район (четверть коконов Узбекистана). Хлопкопереработка, крупное население — трудовой резерв.' },
  { id: 'rishton',    name: 'Риштон',       score: 68, population: 221_216, businesses: 40,  competition: 'средняя', verdict: 'Развитое ремесленное производство. Потенциал для текстильного мини-цеха рядом с кластером Маргилана.' },
  { id: 'oltiariq',   name: 'Олтиариқ',     score: 74, population: 233_047, businesses: 55,  competition: 'средняя', verdict: 'Между Ферганой и Маргиланом — логистическое преимущество. Доступная аренда, трудовой резерв.' },
  { id: 'bogdod',     name: 'Бағдод',       score: 65, population: 238_203, businesses: 30,  competition: 'низкая',  verdict: 'Хлопководческий район. Сырьевая база, крупное население, но слабая промышленная инфраструктура.' },
  { id: 'buvayda',    name: 'Бувайда',      score: 63, population: 252_733, businesses: 30,  competition: 'низкая',  verdict: 'Аграрный район с крупным населением. Потенциал для первичной переработки хлопка.' },
  { id: 'beshariq',   name: 'Бешариқ',      score: 60, population: 247_223, businesses: 25,  competition: 'низкая',  verdict: 'Крупный аграрный район. Доступная рабочая сила, мало текстильных предприятий — окно возможностей.' },
  { id: 'furqat',     name: 'Фурқат',       score: 56, population: 129_754, businesses: 15,  competition: 'низкая',  verdict: 'Небольшой район. Хлопковая база, но слабая инфраструктура и удалённость от кластеров.' },
  { id: 'dangara',    name: 'Дангара',      score: 58, population: 181_036, businesses: 20,  competition: 'низкая',  verdict: 'Аграрный район. Низкая конкуренция, но удалён от основных логистических узлов.' },
  { id: 'toshloq',    name: 'Тошлоқ',       score: 72, population: 221_924, businesses: 50,  competition: 'средняя', verdict: 'Близость к Фергане. Швейные мини-цеха, средний потенциал для текстильного роста.' },
  { id: 'uchkuprik',  name: 'Учкўприк',     score: 55, population: 246_935, businesses: 20,  competition: 'низкая',  verdict: 'Крупное население, но удалённый район. Есть трудовой резерв, слабая транспортная связь.' },
  { id: 'yozyovon',   name: 'Ёзёвон',       score: 57, population: 122_142, businesses: 15,  competition: 'низкая',  verdict: 'Небольшой аграрный район. Мало производств, ограниченная инфраструктура.' },
  { id: 'uzbekiston', name: 'Ўзбекистон',   score: 52, population: 241_278, businesses: 15,  competition: 'низкая',  verdict: 'Периферийный район. Крупное население, но минимальная текстильная активность.' },
  { id: 'quvasoy',    name: 'Қувасой ш.',   score: 70, population: 103_145, businesses: 45,  competition: 'средняя', verdict: 'Промышленный город. Есть производственные площади и квалифицированные кадры.' },
  { id: 'qoqon',      name: 'Қўқон ш.',     score: 82, population: 313_597, businesses: 95,  competition: 'средняя', verdict: 'Второй по величине город региона. Текстильный кластер, исторический центр хан-атласа.' },
  { id: 'sux',        name: 'Сўх',          score: 30, population: 86_094,  businesses: 5,   competition: 'низкая',  verdict: 'Эксклав — логистически изолирован от основной территории (окружён Кыргызстаном). Крайне сложно для текстиля.' },
  { id: 'qoshtepa',   name: 'Қўштепа',      score: 80, population: 213_294, businesses: 85,  competition: 'средняя', verdict: 'Innovative Apparel ($15 млн FDI, контракт H&M, 3 500 рабочих мест). Активный рост текстильного кластера.' },
]
