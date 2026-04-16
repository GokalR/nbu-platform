"""Seed the database with sample courses, videos, and learning content."""

import asyncio

from models import Base, Course, LearningContent, Video, async_session, engine


# ── Course 1: Digital Culture of Banking Data (8 videos) ──────────────────────

COURSE_1 = {
    "title": {"ru": "Цифровая культура данных в банковском деле", "uz": "Bank ishida ma'lumotlarning raqamli madaniyati"},
    "description": {"ru": "Полный курс из 12 видеоуроков о цифровой культуре данных в банковском секторе Узбекистана — от основ до интеграции систем и аналитики.", "uz": "O'zbekiston bank sektorida ma'lumotlarning raqamli madaniyati haqida 12 ta videodarsdan iborat to'liq kurs — asoslardan tizimlar integratsiyasi va tahlilgacha."},
    "thumbnail_url": "/thumbnails/digital-culture-bank.png",
    "category": {"ru": "Банкинг", "uz": "Banking"},
    "educator_name": "NBU Education",
}

COURSE_1_VIDEOS = [
    {
        "title": {"ru": "Выпуск 1: Основы данных в банковском деле", "uz": "1-son: Bank ishida ma'lumotlar asoslari"},
        "description": {"ru": "Введение в цифровую культуру данных для банковского сектора.", "uz": "Bank sektori uchun ma'lumotlarning raqamli madaniyatiga kirish."},
        "video_url": "/videos/digital-culture-bank/uz1.mp4",
        "duration_sec": 900,
    },
    {
        "title": {"ru": "Выпуск 2: Архитектура хранилищ данных", "uz": "2-son: Ma'lumotlar omborxonasi arxitekturasi"},
        "description": {"ru": "Структура и принципы построения хранилищ данных.", "uz": "Ma'lumotlar omborxonalarini qurish tuzilmasi va tamoyillari."},
        "video_url": "/videos/digital-culture-bank/uz2.mp4",
        "duration_sec": 1020,
    },
    {
        "title": {"ru": "Выпуск 3: Типы и качество данных", "uz": "3-son: Ma'lumotlar turlari va sifati"},
        "description": {"ru": "Классификация данных и критерии их качества.", "uz": "Ma'lumotlarni tasniflash va ularning sifat mezonlari."},
        "video_url": "/videos/digital-culture-bank/uz3.mp4",
        "duration_sec": 840,
    },
    {
        "title": {"ru": "Выпуск 4: Путешествие данных", "uz": "4-son: Ma'lumotlar sayohati"},
        "description": {"ru": "Жизненный цикл данных от сбора до анализа.", "uz": "Ma'lumotlarning yig'ishdan tahlilgacha bo'lgan hayot sikli."},
        "video_url": "/videos/digital-culture-bank/uz4.mp4",
        "duration_sec": 960,
    },
    {
        "title": {"ru": "Выпуск 5: Качество данных", "uz": "5-son: Ma'lumotlar sifati"},
        "description": {"ru": "Обеспечение и контроль качества данных в организации.", "uz": "Tashkilotda ma'lumotlar sifatini ta'minlash va nazorat qilish."},
        "video_url": "/videos/digital-culture-bank/uz5.mp4",
        "duration_sec": 780,
    },
    {
        "title": {"ru": "Выпуск 6: Визуализация банковских данных", "uz": "6-son: Bank ma'lumotlarini vizualizatsiya qilish"},
        "description": {"ru": "Методы и инструменты визуализации данных в банковской аналитике.", "uz": "Bank tahlilida ma'lumotlarni vizualizatsiya qilish usullari va vositalari."},
        "video_url": "/videos/digital-culture-bank/uz6.mp4",
        "duration_sec": 870,
    },
    {
        "title": {"ru": "Выпуск 7: Безопасность данных", "uz": "7-son: Ma'lumotlar xavfsizligi"},
        "description": {"ru": "Защита персональных и финансовых данных в банковской сфере.", "uz": "Bank sohasida shaxsiy va moliyaviy ma'lumotlarni himoya qilish."},
        "video_url": "/videos/digital-culture-bank/uz7.mp4",
        "duration_sec": 930,
    },
    {
        "title": {"ru": "Выпуск 8: Управление рисками данных", "uz": "8-son: Ma'lumotlar xavflarini boshqarish"},
        "description": {"ru": "Идентификация и минимизация рисков при работе с данными.", "uz": "Ma'lumotlar bilan ishlashda xavflarni aniqlash va kamaytirish."},
        "video_url": "/videos/digital-culture-bank/uz8.mp4",
        "duration_sec": 1050,
    },
    {
        "title": {"ru": "Выпуск 9: Регуляторные требования", "uz": "9-son: Regulyator talablari"},
        "description": {"ru": "Нормативные акты и требования регулятора к данным в банковской сфере.", "uz": "Bank sohasida ma'lumotlarga oid normativ hujjatlar va regulyator talablari."},
        "video_url": "/videos/digital-culture-bank/uz9.mp4",
        "duration_sec": 960,
    },
    {
        "title": {"ru": "Выпуск 10: Аналитика и отчётность", "uz": "10-son: Tahlil va hisobot"},
        "description": {"ru": "Построение аналитических отчётов и дашбордов для банковского сектора.", "uz": "Bank sektori uchun tahliliy hisobotlar va dashboardlar yaratish."},
        "video_url": "/videos/digital-culture-bank/uz10.mp4",
        "duration_sec": 900,
    },
    {
        "title": {"ru": "Выпуск 11: Интеграция систем данных", "uz": "11-son: Ma'lumotlar tizimlarini integratsiya qilish"},
        "description": {"ru": "Объединение различных источников данных в единую экосистему.", "uz": "Turli ma'lumot manbalarini yagona ekotizimga birlashtirish."},
        "video_url": "/videos/digital-culture-bank/uz11.mp4",
        "duration_sec": 1020,
    },
    {
        "title": {"ru": "Выпуск 12: Будущее банковской аналитики", "uz": "12-son: Bank tahlilining kelajagi"},
        "description": {"ru": "Тренды и перспективы использования данных в банковском секторе.", "uz": "Bank sektorida ma'lumotlardan foydalanish tendensiyalari va istiqbollari."},
        "video_url": "/videos/digital-culture-bank/uz12.mp4",
        "duration_sec": 840,
    },
]


# ── Course 2: Financial Literacy (6 videos) ──────────────────────────────────

COURSE_2 = {
    "title": "Финансовая грамотность для предпринимателей",
    "description": "Практический курс по финансовому управлению для малого и среднего бизнеса в Узбекистане.",
    "thumbnail_url": "/thumbnails/financial-literacy.png",
    "category": "Финансы",
    "educator_name": "NBU Education",
}

COURSE_2_VIDEOS = [
    {
        "title": "Урок 1: Основы финансового планирования",
        "description": "Бюджетирование и финансовое прогнозирование для малого бизнеса.",
        "video_url": "/videos/digital-culture-bank/uz1.mp4",
        "duration_sec": 720,
    },
    {
        "title": "Урок 2: Управление денежными потоками",
        "description": "Cash flow: как контролировать и оптимизировать движение денежных средств.",
        "video_url": "/videos/digital-culture-bank/uz2.mp4",
        "duration_sec": 840,
    },
    {
        "title": "Урок 3: Кредитование и финансирование",
        "description": "Виды кредитов, условия и стратегии привлечения финансирования.",
        "video_url": "/videos/digital-culture-bank/uz3.mp4",
        "duration_sec": 900,
    },
    {
        "title": "Урок 4: Налогообложение в Узбекистане",
        "description": "Основные налоги, льготы и отчётность для предпринимателей.",
        "video_url": "/videos/digital-culture-bank/uz4.mp4",
        "duration_sec": 960,
    },
    {
        "title": "Урок 5: Инвестиции и диверсификация",
        "description": "Стратегии инвестирования и распределения рисков.",
        "video_url": "/videos/digital-culture-bank/uz5.mp4",
        "duration_sec": 780,
    },
    {
        "title": "Урок 6: Финансовая отчётность и анализ",
        "description": "Чтение балансов, P&L отчётов и ключевые показатели бизнеса.",
        "video_url": "/videos/digital-culture-bank/uz6.mp4",
        "duration_sec": 1020,
    },
]


# ── Course 3: Digital Transformation (7 videos) ──────────────────────────────

COURSE_3 = {
    "title": "Цифровая трансформация бизнеса",
    "description": "Как внедрить цифровые технологии в бизнес-процессы. Автоматизация, AI и современные платформы.",
    "thumbnail_url": "/thumbnails/digital-transformation.png",
    "category": "Технологии",
    "educator_name": "NBU Education",
}

COURSE_3_VIDEOS = [
    {
        "title": "Модуль 1: Что такое цифровая трансформация",
        "description": "Определение, этапы и стратегии цифровой трансформации.",
        "video_url": "/videos/digital-culture-bank/uz7.mp4",
        "duration_sec": 660,
    },
    {
        "title": "Модуль 2: Автоматизация бизнес-процессов",
        "description": "RPA, workflow-автоматизация и интеграция систем.",
        "video_url": "/videos/digital-culture-bank/uz8.mp4",
        "duration_sec": 780,
    },
    {
        "title": "Модуль 3: Облачные технологии",
        "description": "Cloud computing, SaaS решения и миграция в облако.",
        "video_url": "/videos/digital-culture-bank/uz9.mp4",
        "duration_sec": 900,
    },
    {
        "title": "Модуль 4: Искусственный интеллект в бизнесе",
        "description": "Применение AI и ML для оптимизации бизнес-процессов.",
        "video_url": "/videos/digital-culture-bank/uz10.mp4",
        "duration_sec": 1020,
    },
    {
        "title": "Модуль 5: Кибербезопасность",
        "description": "Защита бизнеса от цифровых угроз и атак.",
        "video_url": "/videos/digital-culture-bank/uz11.mp4",
        "duration_sec": 840,
    },
    {
        "title": "Модуль 6: Электронная коммерция",
        "description": "Онлайн-продажи, маркетплейсы и цифровые платежи.",
        "video_url": "/videos/digital-culture-bank/uz12.mp4",
        "duration_sec": 720,
    },
]


# ── Learning content templates ────────────────────────────────────────────────

def make_quiz(topic_ru, topic_uz):
    return {
        "title": {"ru": f"Квиз: {topic_ru}", "uz": f"Viktorina: {topic_uz}"},
        "questions": [
            {
                "question": {"ru": f"Какой основной принцип {topic_ru.lower()}?", "uz": f"{topic_uz}ning asosiy tamoyili qanday?"},
                "hint": {"ru": "Подумайте о ключевых концепциях из видеоурока.", "uz": "Videodarsdan asosiy tushunchalar haqida o'ylang."},
                "answerOptions": [
                    {"text": {"ru": "Системный подход к управлению данными", "uz": "Ma'lumotlarni boshqarishda tizimli yondashuv"}, "isCorrect": True,
                     "rationale": {"ru": "Верно! Системный подход является фундаментальным принципом.", "uz": "To'g'ri! Tizimli yondashuv asosiy tamoyil hisoblanadi."}},
                    {"text": {"ru": "Случайная обработка информации", "uz": "Axborotni tasodifiy qayta ishlash"}, "isCorrect": False,
                     "rationale": {"ru": "Случайный подход не обеспечивает качественный результат.", "uz": "Tasodifiy yondashuv sifatli natijani ta'minlamaydi."}},
                    {"text": {"ru": "Игнорирование стандартов", "uz": "Standartlarni e'tiborsiz qoldirish"}, "isCorrect": False,
                     "rationale": {"ru": "Стандарты необходимы для обеспечения качества.", "uz": "Sifatni ta'minlash uchun standartlar zarur."}},
                    {"text": {"ru": "Минимизация документации", "uz": "Hujjatlarni minimallashtirish"}, "isCorrect": False,
                     "rationale": {"ru": "Документация важна для прозрачности и воспроизводимости.", "uz": "Hujjatlar shaffoflik va takrorlanish uchun muhim."}},
                ],
            },
            {
                "question": {"ru": f"Какой инструмент наиболее эффективен для {topic_ru.lower()}?", "uz": f"{topic_uz} uchun qaysi vosita eng samarali?"},
                "hint": {"ru": "Вспомните инструменты, упомянутые в уроке.", "uz": "Darsda aytib o'tilgan vositalarni eslang."},
                "answerOptions": [
                    {"text": {"ru": "Специализированные аналитические платформы", "uz": "Maxsus tahliliy platformalar"}, "isCorrect": True,
                     "rationale": {"ru": "Правильно! Специализированные платформы обеспечивают лучший результат.", "uz": "To'g'ri! Maxsus platformalar eng yaxshi natijani ta'minlaydi."}},
                    {"text": {"ru": "Только бумажные документы", "uz": "Faqat qog'oz hujjatlar"}, "isCorrect": False,
                     "rationale": {"ru": "Бумажные документы не масштабируются.", "uz": "Qog'oz hujjatlar kengaytirilmaydi."}},
                    {"text": {"ru": "Устная передача информации", "uz": "Og'zaki axborot uzatish"}, "isCorrect": False,
                     "rationale": {"ru": "Устная информация не фиксируется и теряется.", "uz": "Og'zaki axborot qayd etilmaydi va yo'qoladi."}},
                    {"text": {"ru": "Нет необходимости в инструментах", "uz": "Vositalarga ehtiyoj yo'q"}, "isCorrect": False,
                     "rationale": {"ru": "Инструменты значительно повышают эффективность.", "uz": "Vositalar samaradorlikni sezilarli darajada oshiradi."}},
                ],
            },
            {
                "question": {"ru": f"Какой первый шаг при внедрении {topic_ru.lower()}?", "uz": f"{topic_uz}ni joriy etishda birinchi qadam qanday?"},
                "hint": {"ru": "Любой процесс начинается с определённого этапа.", "uz": "Har qanday jarayon ma'lum bir bosqichdan boshlanadi."},
                "answerOptions": [
                    {"text": {"ru": "Немедленная покупка самого дорогого ПО", "uz": "Darhol eng qimmat dasturiy ta'minotni sotib olish"}, "isCorrect": False,
                     "rationale": {"ru": "Сначала нужно оценить потребности.", "uz": "Avval ehtiyojlarni baholash kerak."}},
                    {"text": {"ru": "Аудит текущего состояния и определение целей", "uz": "Joriy holatni audit qilish va maqsadlarni belgilash"}, "isCorrect": True,
                     "rationale": {"ru": "Верно! Аудит помогает понять текущее положение и определить направление.", "uz": "To'g'ri! Audit joriy holatni tushunish va yo'nalishni belgilashga yordam beradi."}},
                    {"text": {"ru": "Увольнение всех сотрудников", "uz": "Barcha xodimlarni ishdan bo'shatish"}, "isCorrect": False,
                     "rationale": {"ru": "Люди — ключевой ресурс трансформации.", "uz": "Odamlar transformatsiyaning asosiy resursi."}},
                    {"text": {"ru": "Отказ от всех существующих процессов", "uz": "Barcha mavjud jarayonlardan voz kechish"}, "isCorrect": False,
                     "rationale": {"ru": "Нужно сохранить то, что работает, и улучшить остальное.", "uz": "Ishlaydigan narsalarni saqlab qolish va qolganini yaxshilash kerak."}},
                ],
            },
        ],
    }


def make_flashcards(topic_ru, topic_uz):
    return {
        "cards": [
            {"front": {"ru": f"Что такое {topic_ru.lower()}?", "uz": f"{topic_uz} nima?"},
             "back": {"ru": f"Это системный подход к организации и управлению процессами {topic_ru.lower()} с целью повышения эффективности.", "uz": f"Bu samaradorlikni oshirish maqsadida {topic_uz.lower()} jarayonlarini tashkil etish va boshqarishga tizimli yondashuv."}},
            {"front": {"ru": "Какие основные этапы включает процесс?", "uz": "Jarayon qanday asosiy bosqichlarni o'z ichiga oladi?"},
             "back": {"ru": "1. Анализ текущего состояния\n2. Планирование\n3. Внедрение\n4. Мониторинг\n5. Оптимизация", "uz": "1. Joriy holatni tahlil qilish\n2. Rejalashtirish\n3. Joriy etish\n4. Monitoring\n5. Optimallashtirish"}},
            {"front": {"ru": "Какие ключевые показатели (KPI) используются?", "uz": "Qanday asosiy ko'rsatkichlar (KPI) qo'llaniladi?"},
             "back": {"ru": "Скорость обработки, точность данных, стоимость операций, уровень удовлетворённости пользователей.", "uz": "Qayta ishlash tezligi, ma'lumotlar aniqligi, operatsiyalar narxi, foydalanuvchilar mamnuniyati darajasi."}},
            {"front": {"ru": "Какие риски необходимо учитывать?", "uz": "Qanday xavflarni hisobga olish kerak?"},
             "back": {"ru": "Технические сбои, человеческий фактор, устаревание технологий, несоответствие стандартам.", "uz": "Texnik nosozliklar, inson omili, texnologiyalarning eskirishi, standartlarga mos kelmaslik."}},
            {"front": {"ru": "Какие преимущества даёт автоматизация?", "uz": "Avtomatlashtirish qanday afzalliklar beradi?"},
             "back": {"ru": "Снижение ошибок, ускорение процессов, экономия ресурсов, улучшение качества данных.", "uz": "Xatolarni kamaytirish, jarayonlarni tezlashtirish, resurslarni tejash, ma'lumotlar sifatini yaxshilash."}},
            {"front": {"ru": "Как обеспечить безопасность данных?", "uz": "Ma'lumotlar xavfsizligini qanday ta'minlash mumkin?"},
             "back": {"ru": "Шифрование, контроль доступа, регулярные аудиты, обучение персонала, резервное копирование.", "uz": "Shifrlash, kirishni nazorat qilish, muntazam auditlar, xodimlarni o'qitish, zaxira nusxa olish."}},
        ],
    }


def make_mind_map(topic_ru, topic_uz):
    return {
        "root": {
            "label": {"ru": topic_ru, "uz": topic_uz},
            "detail": {"ru": f"Комплексный обзор {topic_ru.lower()}", "uz": f"{topic_uz}ning kompleks sharhi"},
            "children": [
                {
                    "label": {"ru": "Основы", "uz": "Asoslar"},
                    "detail": {"ru": "Фундаментальные концепции и определения", "uz": "Fundamental tushunchalar va ta'riflar"},
                    "children": [
                        {"label": {"ru": "Определения", "uz": "Ta'riflar"}, "detail": {"ru": "Ключевые термины и понятия", "uz": "Asosiy atamalar va tushunchalar"}},
                        {"label": {"ru": "Принципы", "uz": "Tamoyillar"}, "detail": {"ru": "Базовые принципы и подходы", "uz": "Asosiy tamoyillar va yondashuvlar"}},
                        {"label": {"ru": "Стандарты", "uz": "Standartlar"}, "detail": {"ru": "Международные и локальные стандарты", "uz": "Xalqaro va mahalliy standartlar"}},
                    ],
                },
                {
                    "label": {"ru": "Инструменты", "uz": "Vositalar"},
                    "detail": {"ru": "Технологии и платформы", "uz": "Texnologiyalar va platformalar"},
                    "children": [
                        {"label": {"ru": "Аналитика", "uz": "Tahlil"}, "detail": {"ru": "Инструменты анализа данных", "uz": "Ma'lumotlarni tahlil qilish vositalari"}},
                        {"label": {"ru": "Автоматизация", "uz": "Avtomatlashtirish"}, "detail": {"ru": "Системы автоматизации процессов", "uz": "Jarayonlarni avtomatlashtirish tizimlari"}},
                        {"label": {"ru": "Визуализация", "uz": "Vizualizatsiya"}, "detail": {"ru": "Дашборды и отчёты", "uz": "Dashboardlar va hisobotlar"}},
                    ],
                },
                {
                    "label": {"ru": "Практика", "uz": "Amaliyot"},
                    "detail": {"ru": "Применение в реальных условиях", "uz": "Real sharoitlarda qo'llash"},
                    "children": [
                        {"label": {"ru": "Кейсы", "uz": "Keyslar"}, "detail": {"ru": "Примеры успешного внедрения", "uz": "Muvaffaqiyatli joriy etish namunalari"}},
                        {"label": {"ru": "Метрики", "uz": "Metrikalar"}, "detail": {"ru": "Измерение эффективности", "uz": "Samaradorlikni o'lchash"}},
                    ],
                },
            ],
        },
    }


def make_test(topic_ru, topic_uz):
    return {
        "passingScore": 70,
        "timeLimitSec": 300,
        "questions": [
            {
                "type": "mcq",
                "question": {"ru": f"Выберите правильное определение {topic_ru.lower()}:", "uz": f"{topic_uz}ning to'g'ri ta'rifini tanlang:"},
                "options": [
                    {"ru": "Процесс хаотичного сбора информации", "uz": "Axborotni tartibsiz yig'ish jarayoni"},
                    {"ru": f"Системный подход к управлению {topic_ru.lower()} для достижения бизнес-целей", "uz": f"Biznes maqsadlariga erishish uchun {topic_uz.lower()}ni boshqarishda tizimli yondashuv"},
                    {"ru": "Метод уничтожения устаревших данных", "uz": "Eskirgan ma'lumotlarni yo'q qilish usuli"},
                    {"ru": "Способ ручной обработки документов", "uz": "Hujjatlarni qo'lda qayta ishlash usuli"},
                ],
                "correctIndex": 1,
            },
            {
                "type": "true_false",
                "question": {"ru": f"Автоматизация процессов в {topic_ru.lower()} повышает точность и скорость работы.", "uz": f"{topic_uz}da jarayonlarni avtomatlashtirish ish aniqligini va tezligini oshiradi."},
                "correctAnswer": True,
            },
            {
                "type": "mcq",
                "question": {"ru": "Какой подход обеспечивает наилучшие результаты?", "uz": "Qaysi yondashuv eng yaxshi natijalarni ta'minlaydi?"},
                "options": [
                    {"ru": "Работа без плана", "uz": "Rejasiz ishlash"},
                    {"ru": "Копирование чужого опыта без адаптации", "uz": "Boshqalarning tajribasini moslashtirishsiz nusxalash"},
                    {"ru": "Постепенное внедрение с тестированием на каждом этапе", "uz": "Har bir bosqichda sinov bilan bosqichma-bosqich joriy etish"},
                    {"ru": "Одномоментная замена всех систем", "uz": "Barcha tizimlarni bir vaqtda almashtirish"},
                ],
                "correctIndex": 2,
            },
            {
                "type": "true_false",
                "question": {"ru": "Обучение сотрудников не является важной частью внедрения новых технологий.", "uz": "Xodimlarni o'qitish yangi texnologiyalarni joriy etishning muhim qismi emas."},
                "correctAnswer": False,
            },
            {
                "type": "mcq",
                "question": {"ru": "Что является ключевым фактором успеха?", "uz": "Muvaffaqiyatning asosiy omili nima?"},
                "options": [
                    {"ru": "Только технологии", "uz": "Faqat texnologiyalar"},
                    {"ru": "Только бюджет", "uz": "Faqat byudjet"},
                    {"ru": "Сочетание технологий, людей и процессов", "uz": "Texnologiyalar, odamlar va jarayonlarning uyg'unligi"},
                    {"ru": "Только руководство", "uz": "Faqat rahbariyat"},
                ],
                "correctIndex": 2,
            },
        ],
    }


async def seed():
    async with engine.begin() as conn:
        # Drop and recreate all tables for clean seed
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        all_courses = [
            (COURSE_1, COURSE_1_VIDEOS),
        ]

        for sort_idx, (course_data, videos_data) in enumerate(all_courses):
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                thumbnail_url=course_data["thumbnail_url"],
                category=course_data["category"],
                educator_name=course_data["educator_name"],
                is_published=True,
                sort_order=sort_idx,
            )
            db.add(course)
            await db.flush()

            for i, ep in enumerate(videos_data):
                video = Video(
                    course_id=course.id,
                    title=ep["title"],
                    description=ep["description"],
                    video_url=ep["video_url"],
                    duration_sec=ep["duration_sec"],
                    sort_order=i,
                )
                db.add(video)
                await db.flush()

                # Generate learning content for each video
                topic_ru = ep["title"]["ru"].split(": ", 1)[-1] if ": " in ep["title"]["ru"] else ep["title"]["ru"]
                topic_uz = ep["title"]["uz"].split(": ", 1)[-1] if ": " in ep["title"]["uz"] else ep["title"]["uz"]

                for content_type, content_fn in [
                    ("quiz", make_quiz),
                    ("flashcards", make_flashcards),
                    ("mental_map", make_mind_map),
                    ("test", make_test),
                ]:
                    lc = LearningContent(
                        video_id=video.id,
                        content_type=content_type,
                        content=content_fn(topic_ru, topic_uz),
                    )
                    db.add(lc)

            print(f"  Course: {course_data['title'].get('ru', course_data['title'])} ({len(videos_data)} videos)")

        await db.commit()
        total_videos = sum(len(v) for _, v in all_courses)
        print(f"\nDatabase seeded successfully!")
        print(f"  {len(all_courses)} courses, {total_videos} videos")
        print(f"  No authentication required — all content is free")


if __name__ == "__main__":
    asyncio.run(seed())
