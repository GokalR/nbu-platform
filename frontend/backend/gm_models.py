"""Golden Mart database models — AUTO-GENERATED.

Source of truth: goldenmarts/GM_country.md, GM_region.md, GM_city.md
(themselves regenerated from goldenmarts/golden_mart_*.xlsx).

To regenerate this file:
  PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_sqlalchemy.py

Tables:
  gm_entities — lookup: which countries / regions / cities exist
  gm_country  — country-level GM data (one row per (entity, year))
  gm_region   — region-level GM data (one row per (entity, year))
  gm_city     — city/tuman-level GM data (one row per (entity, year))
"""

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, Numeric, Text,
)
from sqlalchemy.dialects.postgresql import UUID

from models import Base, utcnow  # type: ignore[import-not-found]


class GmEntity(Base):
    """Lookup for entity display names + nesting (parent_key)."""
    __tablename__ = 'gm_entities'

    key = Column(Text, primary_key=True)            # 'qoqon_city', 'fergana_region', 'uzbekistan'
    level = Column(Text, nullable=False)             # 'country' | 'region' | 'city'
    parent_key = Column(Text, nullable=True)         # 'fergana_region' for cities
    name_ru = Column(Text, nullable=False)
    name_uz = Column(Text, nullable=False)
    iso_kind = Column(Text, nullable=True)           # 'shahar' | 'tuman' | 'viloyat'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class GmCountry(Base):
    """Golden Mart — country level. Auto-generated from GM_country.md."""
    __tablename__ = 'gm_country'

    entity_key = Column(Text, primary_key=True)
    year = Column(Integer, primary_key=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # ── §1 (17 fields) ──
    s1_1 = Column(Text, nullable=True)  # Название (текст)
    s1_2 = Column(Text, nullable=True)  # Административный центр (текст)
    s1_3 = Column(Numeric, nullable=True)  # Площадь (тыс. км²)
    s1_4 = Column(Numeric, nullable=True)  # Областей (вилоятов) (областей)
    s1_5 = Column(Numeric, nullable=True)  # Городов областного подчинения (городов)
    s1_6 = Column(Numeric, nullable=True)  # Районов (туманов) (районов)
    s1_7 = Column(Numeric, nullable=True)  # Махаллей (махаллей)
    s1_8 = Column(Numeric, nullable=True)  # Население постоянное (млн чел.)
    s1_9 = Column(Numeric, nullable=True)  # Мужчин (млн чел.)
    s1_10 = Column(Numeric, nullable=True)  # Женщин (млн чел.)
    s1_11 = Column(Numeric, nullable=True)  # Городское население (млн чел.)
    s1_12 = Column(Numeric, nullable=True)  # Сельское население (млн чел.)
    s1_13 = Column(Numeric, nullable=True)  # Население 0–14 лет (млн чел.)
    s1_14 = Column(Numeric, nullable=True)  # Население 15–64 лет (млн чел.)
    s1_15 = Column(Numeric, nullable=True)  # Население 65+ лет (млн чел.)
    s1_16 = Column(Numeric, nullable=True)  # Семей (млн)
    s1_17 = Column(Numeric, nullable=True)  # Домохозяйств (млн)

    # ── §2 (7 fields) ──
    s2_1 = Column(Numeric, nullable=True)  # ВВП (валовой внутренний продукт) (трлн сум)
    s2_2 = Column(Numeric, nullable=True)  # Промышленность – объём (трлн сум)
    s2_3 = Column(Numeric, nullable=True)  # Услуги – объём (трлн сум)
    s2_4 = Column(Numeric, nullable=True)  # Розничная торговля – объём (трлн сум)
    s2_5 = Column(Numeric, nullable=True)  # Строительство – объём (трлн сум)
    s2_6 = Column(Numeric, nullable=True)  # Сельское хозяйство – объём (трлн сум)
    s2_7 = Column(Numeric, nullable=True)  # Инвестиции в основной капитал (трлн сум)

    # ── §3 (10 fields) ──
    s3_1 = Column(Numeric, nullable=True)  # Доходы бюджета – всего (трлн сум)
    s3_2 = Column(Numeric, nullable=True)  # Налоговые поступления (трлн сум)
    s3_3 = Column(Numeric, nullable=True)  # Неналоговые доходы (трлн сум)
    s3_4 = Column(Numeric, nullable=True)  # Трансферты из вышестоящ. бюджета (трлн сум)
    s3_5 = Column(Numeric, nullable=True)  # Расходы бюджета – всего (трлн сум)
    s3_6 = Column(Numeric, nullable=True)  # Социальная сфера (трлн сум)
    s3_7 = Column(Numeric, nullable=True)  # Инфраструктура и экономика (трлн сум)
    s3_8 = Column(Numeric, nullable=True)  # Управление и прочее (трлн сум)
    s3_9 = Column(Numeric, nullable=True)  # Дефицит / Профицит бюджета (трлн сум)
    s3_10 = Column(Numeric, nullable=True)  # Государственный долг (трлн сум)

    # ── §4 (4 fields) ──
    s4_1 = Column(Numeric, nullable=True)  # Товарооборот (млн USD)
    s4_2 = Column(Numeric, nullable=True)  # Экспорт (млн USD)
    s4_3 = Column(Numeric, nullable=True)  # Импорт (млн USD)
    s4_4 = Column(Numeric, nullable=True)  # Сальдо торговли (экспорт − импорт) (млн USD)

    # ── §5 (12 fields) ──
    s5_1 = Column(Text, nullable=True)  # Экспорт – страна 1: название (текст)
    s5_2 = Column(Numeric, nullable=True)  # Экспорт – страна 1: объём (млн USD)
    s5_3 = Column(Text, nullable=True)  # Экспорт – страна 2: название (текст)
    s5_4 = Column(Numeric, nullable=True)  # Экспорт – страна 2: объём (млн USD)
    s5_5 = Column(Text, nullable=True)  # Экспорт – страна 3: название (текст)
    s5_6 = Column(Numeric, nullable=True)  # Экспорт – страна 3: объём (млн USD)
    s5_7 = Column(Text, nullable=True)  # Импорт – страна 1: название (текст)
    s5_8 = Column(Numeric, nullable=True)  # Импорт – страна 1: объём (млн USD)
    s5_9 = Column(Text, nullable=True)  # Импорт – страна 2: название (текст)
    s5_10 = Column(Numeric, nullable=True)  # Импорт – страна 2: объём (млн USD)
    s5_11 = Column(Text, nullable=True)  # Импорт – страна 3: название (текст)
    s5_12 = Column(Numeric, nullable=True)  # Импорт – страна 3: объём (млн USD)

    # ── §6 (6 fields) ──
    s6_1 = Column(Numeric, nullable=True)  # Собственные средства предприятий (трлн сум)
    s6_2 = Column(Numeric, nullable=True)  # Иностранные инвестиции (трлн сум)
    s6_3 = Column(Numeric, nullable=True)  # Госбюджет (трлн сум)
    s6_4 = Column(Numeric, nullable=True)  # Банковские кредиты (трлн сум)
    s6_5 = Column(Numeric, nullable=True)  # Средства населения (трлн сум)
    s6_6 = Column(Numeric, nullable=True)  # Фонд реконструкции (трлн сум)

    # ── §7 (9 fields) ──
    s7_1 = Column(Numeric, nullable=True)  # Активных субъектов – всего (тыс.)
    s7_2 = Column(Numeric, nullable=True)  # ООО (тыс.)
    s7_3 = Column(Numeric, nullable=True)  # ИП (ЯТТ) (тыс.)
    s7_4 = Column(Numeric, nullable=True)  # Фермерские хозяйства (тыс.)
    s7_5 = Column(Numeric, nullable=True)  # Прочие (тыс.)
    s7_6 = Column(Numeric, nullable=True)  # Неактивных (приостановл.) (тыс.)
    s7_7 = Column(Numeric, nullable=True)  # Открыто новых за год (тыс.)
    s7_8 = Column(Numeric, nullable=True)  # Закрыто за год (тыс.)
    s7_9 = Column(Numeric, nullable=True)  # Предприятий-экспортёров (шт.)

    # ── §8 (14 fields) ──
    s8_1 = Column(Numeric, nullable=True)  # Экономически активное население (млн чел.)
    s8_2 = Column(Numeric, nullable=True)  # Официально занятых (млн чел.)
    s8_3 = Column(Numeric, nullable=True)  # Неофициально занятых (млн чел.)
    s8_4 = Column(Numeric, nullable=True)  # Безработных (тыс. чел.)
    s8_5 = Column(Numeric, nullable=True)  # Уровень безработицы (%)
    s8_6 = Column(Numeric, nullable=True)  # Создано новых рабочих мест за год (тыс. раб. мест)
    s8_7 = Column(Numeric, nullable=True)  # Трудовых мигрантов за рубежом (млн чел.)
    s8_8 = Column(Numeric, nullable=True)  # Средняя номинальная зарплата – всего (тыс. сум/мес)
    s8_9 = Column(Numeric, nullable=True)  # в промышленности (тыс. сум/мес)
    s8_10 = Column(Numeric, nullable=True)  # в услугах (тыс. сум/мес)
    s8_11 = Column(Numeric, nullable=True)  # в торговле (тыс. сум/мес)
    s8_12 = Column(Numeric, nullable=True)  # в строительстве (тыс. сум/мес)
    s8_13 = Column(Numeric, nullable=True)  # в бюджетной сфере (тыс. сум/мес)
    s8_14 = Column(Numeric, nullable=True)  # в сельском хозяйстве (тыс. сум/мес)

    # ── §9 (11 fields) ──
    s9_1 = Column(Numeric, nullable=True)  # Семей в Социальном реестре (млн)
    s9_2 = Column(Numeric, nullable=True)  # Семей в бедности на начало года (млн)
    s9_3 = Column(Numeric, nullable=True)  # Семей в бедности на конец года (млн)
    s9_4 = Column(Numeric, nullable=True)  # Покрытие Соц. реестром (от семей в бедности нач. года), % (%)
    s9_5 = Column(Numeric, nullable=True)  # Пенсионеров (млн чел.)
    s9_6 = Column(Numeric, nullable=True)  # Родившихся за год (тыс. чел.)
    s9_7 = Column(Numeric, nullable=True)  # Умерших за год (тыс. чел.)
    s9_8 = Column(Numeric, nullable=True)  # Эмиграция (тыс. чел.)
    s9_9 = Column(Numeric, nullable=True)  # Иммиграция (тыс. чел.)
    s9_10 = Column(Numeric, nullable=True)  # Заключено браков за год (тыс. браков)
    s9_11 = Column(Numeric, nullable=True)  # Разводов за год (тыс. разводов)

    # ── §10 (9 fields) ──
    s10_1 = Column(Numeric, nullable=True)  # Школ (общеобразовательных) (тыс.)
    s10_2 = Column(Numeric, nullable=True)  # Учеников в школах (млн)
    s10_3 = Column(Numeric, nullable=True)  # Учителей (тыс.)
    s10_4 = Column(Numeric, nullable=True)  # Колледжей / техникумов (шт.)
    s10_5 = Column(Numeric, nullable=True)  # Студентов в колледжах (тыс.)
    s10_6 = Column(Numeric, nullable=True)  # Вузов (шт.)
    s10_7 = Column(Numeric, nullable=True)  # Студентов в вузах (тыс.)
    s10_8 = Column(Numeric, nullable=True)  # Детских садов (МТМ) (тыс.)
    s10_9 = Column(Numeric, nullable=True)  # Детей в детсадах (млн)

    # ── §11 (6 fields) ──
    s11_1 = Column(Numeric, nullable=True)  # Больниц (тыс.)
    s11_2 = Column(Numeric, nullable=True)  # Поликлиник / ЦРП (тыс.)
    s11_3 = Column(Numeric, nullable=True)  # Койко-мест (тыс.)
    s11_4 = Column(Numeric, nullable=True)  # Врачей (тыс.)
    s11_5 = Column(Numeric, nullable=True)  # Медсестёр и ср. мед. персонала (тыс.)
    s11_6 = Column(Numeric, nullable=True)  # Младенческая смертность (на 1000 родившихся) (‰)

    # ── §12 (11 fields) ──
    s12_1 = Column(Numeric, nullable=True)  # Кредитный портфель – всего (трлн сум)
    s12_2 = Column(Numeric, nullable=True)  # Кредиты МСБ (трлн сум)
    s12_3 = Column(Numeric, nullable=True)  # Кредиты экспортёрам (трлн сум)
    s12_4 = Column(Numeric, nullable=True)  # Кредиты физлицам (трлн сум)
    s12_5 = Column(Numeric, nullable=True)  # в т.ч. ипотечные / ИЖС (трлн сум)
    s12_6 = Column(Numeric, nullable=True)  # Прочие кредиты (трлн сум)
    s12_7 = Column(Numeric, nullable=True)  # Выдано кредитов за год (трлн сум)
    s12_8 = Column(Numeric, nullable=True)  # Депозитный портфель – всего (трлн сум)
    s12_9 = Column(Numeric, nullable=True)  # Депозиты юр. лиц (трлн сум)
    s12_10 = Column(Numeric, nullable=True)  # Депозиты физ. лиц (трлн сум)
    s12_11 = Column(Numeric, nullable=True)  # Просроченная задолженность (NPL) (трлн сум)

    # ── §13 (7 fields) ──
    s13_1 = Column(Numeric, nullable=True)  # Иностранных туристов (млн чел.)
    s13_2 = Column(Numeric, nullable=True)  # Внутренних туристов (млн чел.)
    s13_3 = Column(Numeric, nullable=True)  # Объектов размещения (тыс.)
    s13_4 = Column(Numeric, nullable=True)  # Номеров в объектах размещения (тыс.)
    s13_5 = Column(Numeric, nullable=True)  # Ночёвок за год (млн)
    s13_6 = Column(Numeric, nullable=True)  # Доход от туризма (иностр. туристов) (млн USD)
    s13_7 = Column(Numeric, nullable=True)  # Доход от туризма (внутр. туристов) (млрд сум)

    # ── §14 (6 fields) ──
    s14_1 = Column(Numeric, nullable=True)  # Жилой фонд – всего (млн м²)
    s14_2 = Column(Numeric, nullable=True)  # Введено жилья за год (млн м²)
    s14_3 = Column(Numeric, nullable=True)  # Многоквартирных домов (тыс.)
    s14_4 = Column(Numeric, nullable=True)  # Частных домов (млн)
    s14_5 = Column(Numeric, nullable=True)  # Аварийного жилья (млн м²)
    s14_6 = Column(Numeric, nullable=True)  # Доля аварийного жилья, % (%)

    # ── §15 (11 fields) ──
    s15_1 = Column(Numeric, nullable=True)  # Подключено к электричеству (млн)
    s15_2 = Column(Numeric, nullable=True)  # Охват электричеством, % (%)
    s15_3 = Column(Numeric, nullable=True)  # Подключено к водопроводу (млн)
    s15_4 = Column(Numeric, nullable=True)  # Охват водопроводом, % (%)
    s15_5 = Column(Numeric, nullable=True)  # Подключено к канализации (млн)
    s15_6 = Column(Numeric, nullable=True)  # Охват канализацией, % (%)
    s15_7 = Column(Numeric, nullable=True)  # Подключено к газу (млн)
    s15_8 = Column(Numeric, nullable=True)  # Охват газом, % (%)
    s15_9 = Column(Numeric, nullable=True)  # Трансформаторных подстанций (тыс.)
    s15_10 = Column(Numeric, nullable=True)  # Скважин водоснабжения (тыс.)
    s15_11 = Column(Numeric, nullable=True)  # Очистных сооружений (шт.)

    # ── §16 (9 fields) ──
    s16_1 = Column(Numeric, nullable=True)  # Дороги – всего (тыс. км)
    s16_2 = Column(Numeric, nullable=True)  # Асфальтированные (тыс. км)
    s16_3 = Column(Numeric, nullable=True)  # Доля асфальтированных дорог, % (%)
    s16_4 = Column(Numeric, nullable=True)  # Щебень / гравий (тыс. км)
    s16_5 = Column(Numeric, nullable=True)  # Грунтовые (тыс. км)
    s16_6 = Column(Numeric, nullable=True)  # В хорошем состоянии (тыс. км)
    s16_7 = Column(Numeric, nullable=True)  # Доля дорог в хорошем состоянии, % (%)
    s16_8 = Column(Numeric, nullable=True)  # Требуют ремонта (тыс. км)
    s16_9 = Column(Numeric, nullable=True)  # Требуют капитального ремонта (тыс. км)

    # ── §19 (39 fields) ──
    s19_1 = Column(Numeric, nullable=True)  # Онлайн-платежи (транзакций в год) (млрд)
    s19_2 = Column(Numeric, nullable=True)  # POS-терминалы (торговцев подключено) (тыс.)
    s19_3 = Column(Numeric, nullable=True)  # Онлайн-кредитов выдано за год (тыс.)
    s19_4 = Column(Numeric, nullable=True)  # Покрытие 4G (по площади территории) (%)
    s19_5 = Column(Numeric, nullable=True)  # ВВП (Валовой внутренний продукт. Сумма стоимости всех товаров и услуг, произведённых на территории страны за год.)
    s19_6 = Column(Numeric, nullable=True)  # ВРП (Валовой региональный продукт. То же, что ВВП, но в разрезе одной области.)
    s19_7 = Column(Numeric, nullable=True)  # ВТП (Валовой территориальный продукт. То же, что ВВП, но в разрезе одного города или тумана.)
    s19_8 = Column(Numeric, nullable=True)  # Возрастная структура (Распределение населения по группам: 0–14, 15–64, 65+ лет.)
    s19_9 = Column(Numeric, nullable=True)  # Дефицит бюджета (Превышение расходов над доходами. Профицит – обратная ситуация.)
    s19_10 = Column(Numeric, nullable=True)  # Семья (Лица, связанные родством или браком. Могут жить раздельно.)
    s19_11 = Column(Numeric, nullable=True)  # Домохозяйство (Лица, живущие в одном жилье и ведущие общий быт. Один человек – тоже домохозяйство.)
    s19_12 = Column(Numeric, nullable=True)  # Активный субъект (Юр. лицо или ИП, ведущий деятельность и сдающий отчётность.)
    s19_13 = Column(Numeric, nullable=True)  # МСБ (Малый и средний бизнес по узбекскому законодательству.)
    s19_14 = Column(Numeric, nullable=True)  # ЯТТ (Якка тартибдаги тадбиркор – индивидуальный предприниматель.)
    s19_15 = Column(Numeric, nullable=True)  # Предприятие-экспортёр (Субъект, хотя бы раз осуществивший экспорт в отчётном году.)
    s19_16 = Column(Numeric, nullable=True)  # Экономически активное население (Лица 15+ лет, работающие или ищущие работу.)
    s19_17 = Column(Numeric, nullable=True)  # Официально занятые (С трудовым договором или зарегистрированные ИП/самозанятые.)
    s19_18 = Column(Numeric, nullable=True)  # Неофициально занятые (Работающие без официальной регистрации (оценка Госкомстата).)
    s19_19 = Column(Numeric, nullable=True)  # Социальный реестр (Единая база нуждающихся семей, получающих гос. помощь.)
    s19_20 = Column(Numeric, nullable=True)  # Эмиграция / Иммиграция (Выезд / прибытие на ПМЖ за год.)
    s19_21 = Column(Numeric, nullable=True)  # Младенческая смертность (Число смертей детей до 1 года на 1000 родившихся живыми (‰).)
    s19_22 = Column(Numeric, nullable=True)  # Кредитный портфель (Сумма выданных и непогашенных кредитов на конец года.)
    s19_23 = Column(Numeric, nullable=True)  # Ипотечные / ИЖС (Кредиты на жильё и индивидуальное жилищное строительство.)
    s19_24 = Column(Numeric, nullable=True)  # NPL (Non-Performing Loans – кредиты с просрочкой более 90 дней.)
    s19_25 = Column(Numeric, nullable=True)  # Депозитный портфель (Сумма всех вкладов физ. и юр. лиц на конец года.)
    s19_26 = Column(Numeric, nullable=True)  # Жилой фонд (Общая площадь всех жилых помещений.)
    s19_27 = Column(Numeric, nullable=True)  # Введено жилья (Площадь жилья, введённого в эксплуатацию по актам ввода.)
    s19_28 = Column(Numeric, nullable=True)  # Аварийное жильё (Официально признанное непригодным для проживания.)
    s19_29 = Column(Numeric, nullable=True)  # Доля аварийного жилья, % (Аварийное жильё ÷ жилой фонд × 100. Считается автоматически.)
    s19_30 = Column(Numeric, nullable=True)  # Охват электр./водопр./канализ./газ, % (Подключённые домохозяйства ÷ всего домохозяйств × 100. Считается автоматически.)
    s19_31 = Column(Numeric, nullable=True)  # Доля дорог в хорошем состоянии, % (Дороги в хорошем состоянии ÷ все дороги × 100. Считается автоматически.)
    s19_32 = Column(Numeric, nullable=True)  # Доля асфальтированных дорог, % (Асфальтированные дороги ÷ все дороги × 100. Считается автоматически.)
    s19_33 = Column(Numeric, nullable=True)  # Покрытие 4G (Процент территории с сетью 4G LTE.)
    s19_34 = Column(Numeric, nullable=True)  # Ночёвки (Человеко-ночи в объектах размещения. 1 турист × 3 ночи = 3 ночёвки.)
    s19_35 = Column(Numeric, nullable=True)  # МТМ (Мактабгача таълим муассасаси – детский сад.)
    s19_36 = Column(Numeric, nullable=True)  # Махалля (Орган самоуправления и территориальная единица в Узбекистане.)
    s19_37 = Column(Numeric, nullable=True)  # ТБО (Твёрдые бытовые отходы.)
    s19_38 = Column(Numeric, nullable=True)  # План 2026 (Целевое значение показателя на конец 2026 года.)
    s19_39 = Column(Numeric, nullable=True)  # н/д (Нет данных. Лучше этого, чем 0.)


class GmRegion(Base):
    """Golden Mart — region level. Auto-generated from GM_region.md."""
    __tablename__ = 'gm_region'

    entity_key = Column(Text, primary_key=True)
    year = Column(Integer, primary_key=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # ── §1 (16 fields) ──
    s1_1 = Column(Text, nullable=True)  # Название (текст)
    s1_2 = Column(Text, nullable=True)  # Административный центр (текст)
    s1_3 = Column(Numeric, nullable=True)  # Площадь (тыс. км²)
    s1_4 = Column(Numeric, nullable=True)  # Городов областного подчинения (городов)
    s1_5 = Column(Numeric, nullable=True)  # Районов (туманов) (районов)
    s1_6 = Column(Numeric, nullable=True)  # Махаллей (махаллей)
    s1_7 = Column(Numeric, nullable=True)  # Население постоянное (млн чел.)
    s1_8 = Column(Numeric, nullable=True)  # Мужчин (млн чел.)
    s1_9 = Column(Numeric, nullable=True)  # Женщин (млн чел.)
    s1_10 = Column(Numeric, nullable=True)  # Городское население (млн чел.)
    s1_11 = Column(Numeric, nullable=True)  # Сельское население (млн чел.)
    s1_12 = Column(Numeric, nullable=True)  # Население 0–14 лет (млн чел.)
    s1_13 = Column(Numeric, nullable=True)  # Население 15–64 лет (млн чел.)
    s1_14 = Column(Numeric, nullable=True)  # Население 65+ лет (млн чел.)
    s1_15 = Column(Numeric, nullable=True)  # Семей (тыс.)
    s1_16 = Column(Numeric, nullable=True)  # Домохозяйств (тыс.)

    # ── §2 (7 fields) ──
    s2_1 = Column(Numeric, nullable=True)  # ВРП (валовой региональный продукт) (млрд сум)
    s2_2 = Column(Numeric, nullable=True)  # Промышленность – объём (млрд сум)
    s2_3 = Column(Numeric, nullable=True)  # Услуги – объём (млрд сум)
    s2_4 = Column(Numeric, nullable=True)  # Розничная торговля – объём (млрд сум)
    s2_5 = Column(Numeric, nullable=True)  # Строительство – объём (млрд сум)
    s2_6 = Column(Numeric, nullable=True)  # Сельское хозяйство – объём (млрд сум)
    s2_7 = Column(Numeric, nullable=True)  # Инвестиции в основной капитал (млрд сум)

    # ── §3 (9 fields) ──
    s3_1 = Column(Numeric, nullable=True)  # Доходы бюджета – всего (млрд сум)
    s3_2 = Column(Numeric, nullable=True)  # Налоговые поступления (млрд сум)
    s3_3 = Column(Numeric, nullable=True)  # Неналоговые доходы (млрд сум)
    s3_4 = Column(Numeric, nullable=True)  # Трансферты из вышестоящ. бюджета (млрд сум)
    s3_5 = Column(Numeric, nullable=True)  # Расходы бюджета – всего (млрд сум)
    s3_6 = Column(Numeric, nullable=True)  # Социальная сфера (млрд сум)
    s3_7 = Column(Numeric, nullable=True)  # Инфраструктура и экономика (млрд сум)
    s3_8 = Column(Numeric, nullable=True)  # Управление и прочее (млрд сум)
    s3_9 = Column(Numeric, nullable=True)  # Дефицит / Профицит бюджета (млрд сум)

    # ── §4 (4 fields) ──
    s4_1 = Column(Numeric, nullable=True)  # Товарооборот (млн USD)
    s4_2 = Column(Numeric, nullable=True)  # Экспорт (млн USD)
    s4_3 = Column(Numeric, nullable=True)  # Импорт (млн USD)
    s4_4 = Column(Numeric, nullable=True)  # Сальдо торговли (экспорт − импорт) (млн USD)

    # ── §5 (12 fields) ──
    s5_1 = Column(Text, nullable=True)  # Экспорт – страна 1: название (текст)
    s5_2 = Column(Numeric, nullable=True)  # Экспорт – страна 1: объём (млн USD)
    s5_3 = Column(Text, nullable=True)  # Экспорт – страна 2: название (текст)
    s5_4 = Column(Numeric, nullable=True)  # Экспорт – страна 2: объём (млн USD)
    s5_5 = Column(Text, nullable=True)  # Экспорт – страна 3: название (текст)
    s5_6 = Column(Numeric, nullable=True)  # Экспорт – страна 3: объём (млн USD)
    s5_7 = Column(Text, nullable=True)  # Импорт – страна 1: название (текст)
    s5_8 = Column(Numeric, nullable=True)  # Импорт – страна 1: объём (млн USD)
    s5_9 = Column(Text, nullable=True)  # Импорт – страна 2: название (текст)
    s5_10 = Column(Numeric, nullable=True)  # Импорт – страна 2: объём (млн USD)
    s5_11 = Column(Text, nullable=True)  # Импорт – страна 3: название (текст)
    s5_12 = Column(Numeric, nullable=True)  # Импорт – страна 3: объём (млн USD)

    # ── §6 (6 fields) ──
    s6_1 = Column(Numeric, nullable=True)  # Собственные средства предприятий (млрд сум)
    s6_2 = Column(Numeric, nullable=True)  # Иностранные инвестиции (млрд сум)
    s6_3 = Column(Numeric, nullable=True)  # Госбюджет (млрд сум)
    s6_4 = Column(Numeric, nullable=True)  # Банковские кредиты (млрд сум)
    s6_5 = Column(Numeric, nullable=True)  # Средства населения (млрд сум)
    s6_6 = Column(Numeric, nullable=True)  # Фонд реконструкции (млрд сум)

    # ── §7 (9 fields) ──
    s7_1 = Column(Numeric, nullable=True)  # Активных субъектов – всего (тыс.)
    s7_2 = Column(Numeric, nullable=True)  # ООО (тыс.)
    s7_3 = Column(Numeric, nullable=True)  # ИП (ЯТТ) (тыс.)
    s7_4 = Column(Numeric, nullable=True)  # Фермерские хозяйства (тыс.)
    s7_5 = Column(Numeric, nullable=True)  # Прочие (тыс.)
    s7_6 = Column(Numeric, nullable=True)  # Неактивных (приостановл.) (тыс.)
    s7_7 = Column(Numeric, nullable=True)  # Открыто новых за год (тыс.)
    s7_8 = Column(Numeric, nullable=True)  # Закрыто за год (тыс.)
    s7_9 = Column(Numeric, nullable=True)  # Предприятий-экспортёров (шт.)

    # ── §8 (14 fields) ──
    s8_1 = Column(Numeric, nullable=True)  # Экономически активное население (млн чел.)
    s8_2 = Column(Numeric, nullable=True)  # Официально занятых (млн чел.)
    s8_3 = Column(Numeric, nullable=True)  # Неофициально занятых (млн чел.)
    s8_4 = Column(Numeric, nullable=True)  # Безработных (тыс. чел.)
    s8_5 = Column(Numeric, nullable=True)  # Уровень безработицы (%)
    s8_6 = Column(Numeric, nullable=True)  # Создано новых рабочих мест за год (тыс. раб. мест)
    s8_7 = Column(Numeric, nullable=True)  # Трудовых мигрантов за рубежом (тыс. чел.)
    s8_8 = Column(Numeric, nullable=True)  # Средняя номинальная зарплата – всего (тыс. сум/мес)
    s8_9 = Column(Numeric, nullable=True)  # в промышленности (тыс. сум/мес)
    s8_10 = Column(Numeric, nullable=True)  # в услугах (тыс. сум/мес)
    s8_11 = Column(Numeric, nullable=True)  # в торговле (тыс. сум/мес)
    s8_12 = Column(Numeric, nullable=True)  # в строительстве (тыс. сум/мес)
    s8_13 = Column(Numeric, nullable=True)  # в бюджетной сфере (тыс. сум/мес)
    s8_14 = Column(Numeric, nullable=True)  # в сельском хозяйстве (тыс. сум/мес)

    # ── §9 (11 fields) ──
    s9_1 = Column(Numeric, nullable=True)  # Семей в Социальном реестре (тыс.)
    s9_2 = Column(Numeric, nullable=True)  # Семей в бедности на начало года (тыс.)
    s9_3 = Column(Numeric, nullable=True)  # Семей в бедности на конец года (тыс.)
    s9_4 = Column(Numeric, nullable=True)  # Покрытие Соц. реестром (от семей в бедности нач. года), % (%)
    s9_5 = Column(Numeric, nullable=True)  # Пенсионеров (тыс.)
    s9_6 = Column(Numeric, nullable=True)  # Родившихся за год (тыс.)
    s9_7 = Column(Numeric, nullable=True)  # Умерших за год (тыс.)
    s9_8 = Column(Numeric, nullable=True)  # Эмиграция (тыс. чел.)
    s9_9 = Column(Numeric, nullable=True)  # Иммиграция (тыс. чел.)
    s9_10 = Column(Numeric, nullable=True)  # Заключено браков за год (тыс. браков)
    s9_11 = Column(Numeric, nullable=True)  # Разводов за год (тыс. разводов)

    # ── §10 (9 fields) ──
    s10_1 = Column(Numeric, nullable=True)  # Школ (общеобразовательных) (шт.)
    s10_2 = Column(Numeric, nullable=True)  # Учеников в школах (тыс.)
    s10_3 = Column(Numeric, nullable=True)  # Учителей (тыс.)
    s10_4 = Column(Numeric, nullable=True)  # Колледжей / техникумов (шт.)
    s10_5 = Column(Numeric, nullable=True)  # Студентов в колледжах (тыс.)
    s10_6 = Column(Numeric, nullable=True)  # Вузов (шт.)
    s10_7 = Column(Numeric, nullable=True)  # Студентов в вузах (тыс.)
    s10_8 = Column(Numeric, nullable=True)  # Детских садов (МТМ) (шт.)
    s10_9 = Column(Numeric, nullable=True)  # Детей в детсадах (тыс.)

    # ── §11 (6 fields) ──
    s11_1 = Column(Numeric, nullable=True)  # Больниц (шт.)
    s11_2 = Column(Numeric, nullable=True)  # Поликлиник / ЦРП (шт.)
    s11_3 = Column(Numeric, nullable=True)  # Койко-мест (шт.)
    s11_4 = Column(Numeric, nullable=True)  # Врачей (тыс.)
    s11_5 = Column(Numeric, nullable=True)  # Медсестёр и ср. мед. персонала (тыс.)
    s11_6 = Column(Numeric, nullable=True)  # Младенческая смертность (на 1000 родившихся) (‰)

    # ── §12 (11 fields) ──
    s12_1 = Column(Numeric, nullable=True)  # Кредитный портфель – всего (млрд сум)
    s12_2 = Column(Numeric, nullable=True)  # Кредиты МСБ (млрд сум)
    s12_3 = Column(Numeric, nullable=True)  # Кредиты экспортёрам (млрд сум)
    s12_4 = Column(Numeric, nullable=True)  # Кредиты физлицам (млрд сум)
    s12_5 = Column(Numeric, nullable=True)  # в т.ч. ипотечные / ИЖС (млрд сум)
    s12_6 = Column(Numeric, nullable=True)  # Прочие кредиты (млрд сум)
    s12_7 = Column(Numeric, nullable=True)  # Выдано кредитов за год (млрд сум)
    s12_8 = Column(Numeric, nullable=True)  # Депозитный портфель – всего (млрд сум)
    s12_9 = Column(Numeric, nullable=True)  # Депозиты юр. лиц (млрд сум)
    s12_10 = Column(Numeric, nullable=True)  # Депозиты физ. лиц (млрд сум)
    s12_11 = Column(Numeric, nullable=True)  # Просроченная задолженность (NPL) (млрд сум)

    # ── §13 (7 fields) ──
    s13_1 = Column(Numeric, nullable=True)  # Иностранных туристов (тыс. чел.)
    s13_2 = Column(Numeric, nullable=True)  # Внутренних туристов (тыс. чел.)
    s13_3 = Column(Numeric, nullable=True)  # Объектов размещения (шт.)
    s13_4 = Column(Numeric, nullable=True)  # Номеров в объектах размещения (тыс.)
    s13_5 = Column(Numeric, nullable=True)  # Ночёвок за год (млн)
    s13_6 = Column(Numeric, nullable=True)  # Доход от туризма (иностр. туристов) (млн USD)
    s13_7 = Column(Numeric, nullable=True)  # Доход от туризма (внутр. туристов) (млрд сум)

    # ── §14 (6 fields) ──
    s14_1 = Column(Numeric, nullable=True)  # Жилой фонд – всего (тыс. м²)
    s14_2 = Column(Numeric, nullable=True)  # Введено жилья за год (тыс. м²)
    s14_3 = Column(Numeric, nullable=True)  # Многоквартирных домов (шт.)
    s14_4 = Column(Numeric, nullable=True)  # Частных домов (шт.)
    s14_5 = Column(Numeric, nullable=True)  # Аварийного жилья (тыс. м²)
    s14_6 = Column(Numeric, nullable=True)  # Доля аварийного жилья, % (%)

    # ── §15 (17 fields) ──
    s15_1 = Column(Numeric, nullable=True)  # Подключено к электричеству (тыс.)
    s15_2 = Column(Numeric, nullable=True)  # Охват электричеством, % (%)
    s15_3 = Column(Numeric, nullable=True)  # Подключено к водопроводу (тыс.)
    s15_4 = Column(Numeric, nullable=True)  # Охват водопроводом, % (%)
    s15_5 = Column(Numeric, nullable=True)  # Подключено к канализации (тыс.)
    s15_6 = Column(Numeric, nullable=True)  # Охват канализацией, % (%)
    s15_7 = Column(Numeric, nullable=True)  # Подключено к газу (тыс.)
    s15_8 = Column(Numeric, nullable=True)  # Охват газом, % (%)
    s15_9 = Column(Numeric, nullable=True)  # Трансформаторных подстанций (шт.)
    s15_10 = Column(Numeric, nullable=True)  # Скважин водоснабжения (шт.)
    s15_11 = Column(Numeric, nullable=True)  # Очистных сооружений (шт.)
    s15_12 = Column(Numeric, nullable=True)  # Инфра-индекс (общий, /100) (балл)
    s15_13 = Column(Numeric, nullable=True)  # Подындекс: дороги (балл)
    s15_14 = Column(Numeric, nullable=True)  # Подындекс: водоснабжение (балл)
    s15_15 = Column(Numeric, nullable=True)  # Подындекс: канализация (балл)
    s15_16 = Column(Numeric, nullable=True)  # Подындекс: газоснабжение (балл)
    s15_17 = Column(Numeric, nullable=True)  # Подындекс: электроснабжение (балл)

    # ── §16 (9 fields) ──
    s16_1 = Column(Numeric, nullable=True)  # Дороги – всего (км)
    s16_2 = Column(Numeric, nullable=True)  # Асфальтированные (км)
    s16_3 = Column(Numeric, nullable=True)  # Доля асфальтированных дорог, % (%)
    s16_4 = Column(Numeric, nullable=True)  # Щебень / гравий (км)
    s16_5 = Column(Numeric, nullable=True)  # Грунтовые (км)
    s16_6 = Column(Numeric, nullable=True)  # В хорошем состоянии (км)
    s16_7 = Column(Numeric, nullable=True)  # Доля дорог в хорошем состоянии, % (%)
    s16_8 = Column(Numeric, nullable=True)  # Требуют ремонта (км)
    s16_9 = Column(Numeric, nullable=True)  # Требуют капитального ремонта (км)

    # ── §17 (4 fields) ──
    s17_1 = Column(Numeric, nullable=True)  # Автобусных маршрутов (маршрутов)
    s17_2 = Column(Numeric, nullable=True)  # Автобусов в парке общ. транспорта (шт.)
    s17_3 = Column(Numeric, nullable=True)  # Такси (зарегистрировано) (шт.)
    s17_4 = Column(Numeric, nullable=True)  # Легковых авто (зарегистрировано) (шт.)

    # ── §18 (2 fields) ──
    s18_1 = Column(Numeric, nullable=True)  # Зелёных насаждений (га)
    s18_2 = Column(Numeric, nullable=True)  # Вывоз ТБО за год (тыс. тонн)

    # ── §19 (4 fields) ──
    s19_1 = Column(Numeric, nullable=True)  # Онлайн-платежи (транзакций в год) (млн шт.)
    s19_2 = Column(Numeric, nullable=True)  # POS-терминалы (торговцев подключено) (шт.)
    s19_3 = Column(Numeric, nullable=True)  # Онлайн-кредитов выдано за год (шт.)
    s19_4 = Column(Numeric, nullable=True)  # Покрытие 4G (по площади территории) (%)

    # ── §20 (6 fields) ──
    s20_1 = Column(Numeric, nullable=True)  # Промышленность – реальный рост (%)
    s20_2 = Column(Numeric, nullable=True)  # Услуги – реальный рост (%)
    s20_3 = Column(Numeric, nullable=True)  # Розничная торговля – реальный рост (%)
    s20_4 = Column(Numeric, nullable=True)  # Строительство – реальный рост (%)
    s20_5 = Column(Numeric, nullable=True)  # Сельское хозяйство – реальный рост (%)
    s20_6 = Column(Numeric, nullable=True)  # ВРП – реальный рост (%)


class GmCity(Base):
    """Golden Mart — city level. Auto-generated from GM_city.md."""
    __tablename__ = 'gm_city'

    entity_key = Column(Text, primary_key=True)
    year = Column(Integer, primary_key=True)
    region_key = Column(Text, nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # ── §1 (30 fields) ──
    s1_1 = Column(Text, nullable=True)  # Название (текст)
    s1_2 = Column(Text, nullable=True)  # Тип объекта (город / туман) (текст)
    s1_3 = Column(Text, nullable=True)  # Админ. центр области (да/нет) (да/нет)
    s1_4 = Column(Numeric, nullable=True)  # Площадь (км²)
    s1_5 = Column(Numeric, nullable=True)  # Махаллей (шт.)
    s1_6 = Column(Numeric, nullable=True)  # Население постоянное (чел.)
    s1_7 = Column(Numeric, nullable=True)  # Мужчин (чел.)
    s1_8 = Column(Numeric, nullable=True)  # Женщин (чел.)
    s1_9 = Column(Numeric, nullable=True)  # Население 0–14 лет (чел.)
    s1_10 = Column(Numeric, nullable=True)  # Население 15–64 лет (чел.)
    s1_11 = Column(Numeric, nullable=True)  # Население 65+ лет (чел.)
    s1_12 = Column(Numeric, nullable=True)  # Население 0–2 лет (чел.)
    s1_13 = Column(Numeric, nullable=True)  # Население 3–5 лет (чел.)
    s1_14 = Column(Numeric, nullable=True)  # Население 6–7 лет (чел.)
    s1_15 = Column(Numeric, nullable=True)  # Население 8–15 лет (чел.)
    s1_16 = Column(Numeric, nullable=True)  # Население 16–17 лет (чел.)
    s1_17 = Column(Numeric, nullable=True)  # Население 18–19 лет (чел.)
    s1_18 = Column(Numeric, nullable=True)  # Население 20–24 лет (чел.)
    s1_19 = Column(Numeric, nullable=True)  # Население 25–29 лет (чел.)
    s1_20 = Column(Numeric, nullable=True)  # Население 30–34 лет (чел.)
    s1_21 = Column(Numeric, nullable=True)  # Население 35–39 лет (чел.)
    s1_22 = Column(Numeric, nullable=True)  # Население 40–49 лет (чел.)
    s1_23 = Column(Numeric, nullable=True)  # Население 50–59 лет (чел.)
    s1_24 = Column(Numeric, nullable=True)  # Население 60–69 лет (чел.)
    s1_25 = Column(Numeric, nullable=True)  # Население 70–74 лет (чел.)
    s1_26 = Column(Numeric, nullable=True)  # Население 75–79 лет (чел.)
    s1_27 = Column(Numeric, nullable=True)  # Население 80–84 лет (чел.)
    s1_28 = Column(Numeric, nullable=True)  # Население 85+ лет (чел.)
    s1_29 = Column(Numeric, nullable=True)  # Семей (тыс.)
    s1_30 = Column(Numeric, nullable=True)  # Домохозяйств (тыс.)

    # ── §2 (7 fields) ──
    s2_1 = Column(Numeric, nullable=True)  # ВТП (валовой территориальный продукт) (млрд сум)
    s2_2 = Column(Numeric, nullable=True)  # Промышленность – объём (млрд сум)
    s2_3 = Column(Numeric, nullable=True)  # Услуги – объём (млрд сум)
    s2_4 = Column(Numeric, nullable=True)  # Розничная торговля – объём (млрд сум)
    s2_5 = Column(Numeric, nullable=True)  # Строительство – объём (млрд сум)
    s2_6 = Column(Numeric, nullable=True)  # Сельское хозяйство – объём (млрд сум)
    s2_7 = Column(Numeric, nullable=True)  # Инвестиции в основной капитал (млрд сум)

    # ── §3 (9 fields) ──
    s3_1 = Column(Numeric, nullable=True)  # Доходы бюджета – всего (млрд сум)
    s3_2 = Column(Numeric, nullable=True)  # Налоговые поступления (млрд сум)
    s3_3 = Column(Numeric, nullable=True)  # Неналоговые доходы (млрд сум)
    s3_4 = Column(Numeric, nullable=True)  # Трансферты из вышестоящ. бюджета (млрд сум)
    s3_5 = Column(Numeric, nullable=True)  # Расходы бюджета – всего (млрд сум)
    s3_6 = Column(Numeric, nullable=True)  # Социальная сфера (млрд сум)
    s3_7 = Column(Numeric, nullable=True)  # Инфраструктура и экономика (млрд сум)
    s3_8 = Column(Numeric, nullable=True)  # Управление и прочее (млрд сум)
    s3_9 = Column(Numeric, nullable=True)  # Дефицит / Профицит бюджета (млрд сум)

    # ── §4 (3 fields) ──
    s4_1 = Column(Numeric, nullable=True)  # Экспорт (млрд сум)
    s4_2 = Column(Numeric, nullable=True)  # Импорт (млрд сум)
    s4_3 = Column(Numeric, nullable=True)  # Сальдо торговли (экспорт − импорт) (млрд сум)

    # ── §5 (11 fields) ──
    s5_1 = Column(Text, nullable=True)  # Экспорт – страна 1: название (текст)
    s5_2 = Column(Numeric, nullable=True)  # Экспорт – страна 1: объём (млрд сум)
    s5_3 = Column(Numeric, nullable=True)  # Экспорт – страна 2: объём (млрд сум)
    s5_4 = Column(Text, nullable=True)  # Экспорт – страна 3: название (текст)
    s5_5 = Column(Numeric, nullable=True)  # Экспорт – страна 3: объём (млрд сум)
    s5_6 = Column(Text, nullable=True)  # Импорт – страна 1: название (текст)
    s5_7 = Column(Numeric, nullable=True)  # Импорт – страна 1: объём (млрд сум)
    s5_8 = Column(Text, nullable=True)  # Импорт – страна 2: название (текст)
    s5_9 = Column(Numeric, nullable=True)  # Импорт – страна 2: объём (млрд сум)
    s5_10 = Column(Text, nullable=True)  # Импорт – страна 3: название (текст)
    s5_11 = Column(Numeric, nullable=True)  # Импорт – страна 3: объём (млрд сум)

    # ── §6 (6 fields) ──
    s6_1 = Column(Numeric, nullable=True)  # Собственные средства предприятий (млрд сум)
    s6_2 = Column(Numeric, nullable=True)  # Иностранные инвестиции (млрд сум)
    s6_3 = Column(Numeric, nullable=True)  # Госбюджет (млрд сум)
    s6_4 = Column(Numeric, nullable=True)  # Банковские кредиты (млрд сум)
    s6_5 = Column(Numeric, nullable=True)  # Средства населения (млрд сум)
    s6_6 = Column(Numeric, nullable=True)  # Фонд реконструкции (млрд сум)

    # ── §7 (8 fields) ──
    s7_1 = Column(Numeric, nullable=True)  # Активных субъектов – всего (шт.)
    s7_2 = Column(Numeric, nullable=True)  # ООО (шт.)
    s7_3 = Column(Numeric, nullable=True)  # ИП (ЯТТ) (шт.)
    s7_4 = Column(Numeric, nullable=True)  # Фермерские хозяйства (шт.)
    s7_5 = Column(Numeric, nullable=True)  # Прочие (шт.)
    s7_6 = Column(Numeric, nullable=True)  # Неактивных (приостановл.) (шт.)
    s7_7 = Column(Numeric, nullable=True)  # Открыто новых за год (шт.)
    s7_8 = Column(Numeric, nullable=True)  # Предприятий-экспортёров (шт.)

    # ── §8 (13 fields) ──
    s8_1 = Column(Numeric, nullable=True)  # Экономически активное население (чел.)
    s8_2 = Column(Numeric, nullable=True)  # Официально занятых (тыс. чел.)
    s8_3 = Column(Numeric, nullable=True)  # Неофициально занятых (тыс. чел.)
    s8_4 = Column(Numeric, nullable=True)  # Безработных (чел.)
    s8_5 = Column(Numeric, nullable=True)  # Уровень безработицы (%)
    s8_6 = Column(Numeric, nullable=True)  # Создано новых рабочих мест за год (раб. мест)
    s8_7 = Column(Numeric, nullable=True)  # Трудовых мигрантов за рубежом (чел.)
    s8_8 = Column(Numeric, nullable=True)  # Средняя номинальная зарплата – всего (тыс. сум/мес)
    s8_9 = Column(Numeric, nullable=True)  # в промышленности (тыс. сум/мес)
    s8_10 = Column(Numeric, nullable=True)  # в торговле (тыс. сум/мес)
    s8_11 = Column(Numeric, nullable=True)  # в строительстве (тыс. сум/мес)
    s8_12 = Column(Numeric, nullable=True)  # в бюджетной сфере (тыс. сум/мес)
    s8_13 = Column(Numeric, nullable=True)  # в сельском хозяйстве (тыс. сум/мес)

    # ── §9 (10 fields) ──
    s9_1 = Column(Numeric, nullable=True)  # Семей в Социальном реестре (семей)
    s9_2 = Column(Numeric, nullable=True)  # Семей в бедности на начало года (семей)
    s9_3 = Column(Numeric, nullable=True)  # Семей в бедности на конец года (семей)
    s9_4 = Column(Numeric, nullable=True)  # Покрытие Соц. реестром (от семей в бедности нач. года), % (%)
    s9_5 = Column(Numeric, nullable=True)  # Родившихся за год (чел.)
    s9_6 = Column(Numeric, nullable=True)  # Умерших за год (чел.)
    s9_7 = Column(Numeric, nullable=True)  # Эмиграция (чел.)
    s9_8 = Column(Numeric, nullable=True)  # Иммиграция (чел.)
    s9_9 = Column(Numeric, nullable=True)  # Заключено браков за год (браков)
    s9_10 = Column(Numeric, nullable=True)  # Разводов за год (разводов)

    # ── §10 (9 fields) ──
    s10_1 = Column(Numeric, nullable=True)  # Школ (общеобразовательных) (шт.)
    s10_2 = Column(Numeric, nullable=True)  # Учеников в школах (чел.)
    s10_3 = Column(Numeric, nullable=True)  # Учителей (чел.)
    s10_4 = Column(Numeric, nullable=True)  # Колледжей / техникумов (шт.)
    s10_5 = Column(Numeric, nullable=True)  # Студентов в колледжах (чел.)
    s10_6 = Column(Numeric, nullable=True)  # Вузов (шт.)
    s10_7 = Column(Numeric, nullable=True)  # Студентов в вузах (чел.)
    s10_8 = Column(Numeric, nullable=True)  # Детских садов (МТМ) (шт.)
    s10_9 = Column(Numeric, nullable=True)  # Детей в детсадах (чел.)

    # ── §11 (8 fields) ──
    s11_1 = Column(Numeric, nullable=True)  # Больниц (шт.)
    s11_2 = Column(Numeric, nullable=True)  # Поликлиник / ЦРП (шт.)
    s11_3 = Column(Numeric, nullable=True)  # Койко-мест (шт.)
    s11_4 = Column(Numeric, nullable=True)  # Врачей (чел.)
    s11_5 = Column(Numeric, nullable=True)  # Медсестёр и ср. мед. персонала (чел.)
    s11_6 = Column(Numeric, nullable=True)  # Младенческая смертность (на 1000 родившихся) (‰)
    s11_7 = Column(Numeric, nullable=True)  # Рождений (всего) (чел.)
    s11_8 = Column(Numeric, nullable=True)  # Смертей (всего) (чел.)

    # ── §12 (15 fields) ──
    s12_1 = Column(Numeric, nullable=True)  # Кредитный портфель – всего (млрд сум)
    s12_2 = Column(Numeric, nullable=True)  # Кредиты МСБ (млрд сум)
    s12_3 = Column(Numeric, nullable=True)  # Кредиты экспортёрам (млрд сум)
    s12_4 = Column(Numeric, nullable=True)  # Кредиты физлицам (млрд сум)
    s12_5 = Column(Numeric, nullable=True)  # в т.ч. ипотечные / ИЖС (млрд сум)
    s12_6 = Column(Numeric, nullable=True)  # Прочие кредиты (млрд сум)
    s12_7 = Column(Numeric, nullable=True)  # Депозитный портфель – всего (млрд сум)
    s12_8 = Column(Numeric, nullable=True)  # Депозиты юр. лиц (млрд сум)
    s12_9 = Column(Numeric, nullable=True)  # Депозиты физ. лиц (млрд сум)
    s12_10 = Column(Numeric, nullable=True)  # Просроченная задолженность (NPL) (млрд сум)
    s12_11 = Column(Numeric, nullable=True)  # Кредитов выдано МСБ (кол-во) (шт.)
    s12_12 = Column(Numeric, nullable=True)  # Кредитов выдано экспортёрам (кол-во) (шт.)
    s12_13 = Column(Numeric, nullable=True)  # Кредитов выдано самозанятым (кол-во) (шт.)
    s12_14 = Column(Numeric, nullable=True)  # Просроченных кредитов NPL (кол-во) (шт.)
    s12_15 = Column(Numeric, nullable=True)  # Новых ИП, получивших кредит (за квартал) (шт.)

    # ── §13 (6 fields) ──
    s13_1 = Column(Numeric, nullable=True)  # Иностранных туристов (тыс.)
    s13_2 = Column(Numeric, nullable=True)  # Внутренних туристов (тыс.)
    s13_3 = Column(Numeric, nullable=True)  # Объектов размещения (шт.)
    s13_4 = Column(Numeric, nullable=True)  # Номеров в объектах размещения (номеров)
    s13_5 = Column(Numeric, nullable=True)  # Доход от туризма (иностр. туристов) (млрд сум)
    s13_6 = Column(Numeric, nullable=True)  # Доход от туризма (внутр. туристов) (млрд сум)

    # ── §14 (6 fields) ──
    s14_1 = Column(Numeric, nullable=True)  # Жилой фонд – всего (тыс. м²)
    s14_2 = Column(Numeric, nullable=True)  # Введено жилья за год (тыс. м²)
    s14_3 = Column(Numeric, nullable=True)  # Многоквартирных домов (шт.)
    s14_4 = Column(Numeric, nullable=True)  # Частных домов (шт.)
    s14_5 = Column(Numeric, nullable=True)  # Аварийного жилья (тыс. м²)
    s14_6 = Column(Numeric, nullable=True)  # Доля аварийного жилья, % (%)

    # ── §15 (6 fields) ──
    s15_1 = Column(Numeric, nullable=True)  # Подключено к электричеству (домохоз.)
    s15_2 = Column(Numeric, nullable=True)  # Охват электричеством, % (%)
    s15_3 = Column(Numeric, nullable=True)  # Подключено к водопроводу (домохоз.)
    s15_4 = Column(Numeric, nullable=True)  # Охват водопроводом, % (%)
    s15_5 = Column(Numeric, nullable=True)  # Охват канализацией, % (%)
    s15_6 = Column(Numeric, nullable=True)  # Подключено к газу (домохоз.)

    # ── §16 (8 fields) ──
    s16_1 = Column(Numeric, nullable=True)  # Дороги – всего (км)
    s16_2 = Column(Numeric, nullable=True)  # Асфальтированные (км)
    s16_3 = Column(Numeric, nullable=True)  # Доля асфальтированных дорог, % (%)
    s16_4 = Column(Numeric, nullable=True)  # Грунтовые (км)
    s16_5 = Column(Numeric, nullable=True)  # В хорошем состоянии (км)
    s16_6 = Column(Numeric, nullable=True)  # Доля дорог в хорошем состоянии, % (%)
    s16_7 = Column(Numeric, nullable=True)  # Требуют ремонта (км)
    s16_8 = Column(Numeric, nullable=True)  # Требуют капитального ремонта (км)

    # ── §17 (4 fields) ──
    s17_1 = Column(Numeric, nullable=True)  # Автобусных маршрутов (маршрутов)
    s17_2 = Column(Numeric, nullable=True)  # Автобусов в парке общ. транспорта (шт.)
    s17_3 = Column(Numeric, nullable=True)  # Такси (зарегистрировано) (шт.)
    s17_4 = Column(Numeric, nullable=True)  # Легковых авто (зарегистрировано) (шт.)

    # ── §18 (2 fields) ──
    s18_1 = Column(Numeric, nullable=True)  # Зелёных насаждений (га)
    s18_2 = Column(Numeric, nullable=True)  # Вывоз ТБО за год (тонн)

    # ── §19 (3 fields) ──
    s19_1 = Column(Numeric, nullable=True)  # Онлайн-платежи (транзакций в год) (тыс. шт.)
    s19_2 = Column(Numeric, nullable=True)  # Онлайн-кредитов выдано за год (шт.)
    s19_3 = Column(Numeric, nullable=True)  # Покрытие 4G (по площади территории) (%)

    # ── §20 (29 fields) ──
    s20_1 = Column(Text, nullable=True)  # Махалля 1: название (текст)
    s20_2 = Column(Numeric, nullable=True)  # Махалля 1: количество кредитов (шт.)
    s20_3 = Column(Numeric, nullable=True)  # Махалля 1: рейтинг/скор (балл)
    s20_4 = Column(Text, nullable=True)  # Махалля 2: название (текст)
    s20_5 = Column(Numeric, nullable=True)  # Махалля 2: количество кредитов (шт.)
    s20_6 = Column(Numeric, nullable=True)  # Махалля 2: рейтинг/скор (балл)
    s20_7 = Column(Text, nullable=True)  # Махалля 3: название (текст)
    s20_8 = Column(Numeric, nullable=True)  # Махалля 3: количество кредитов (шт.)
    s20_9 = Column(Numeric, nullable=True)  # Махалля 3: рейтинг/скор (балл)
    s20_10 = Column(Text, nullable=True)  # Махалля 4: название (текст)
    s20_11 = Column(Numeric, nullable=True)  # Махалля 4: количество кредитов (шт.)
    s20_12 = Column(Numeric, nullable=True)  # Махалля 4: рейтинг/скор (балл)
    s20_13 = Column(Numeric, nullable=True)  # Махалля 5: количество кредитов (шт.)
    s20_14 = Column(Numeric, nullable=True)  # Махалля 5: рейтинг/скор (балл)
    s20_15 = Column(Text, nullable=True)  # Махалля 1: название (текст)
    s20_16 = Column(Numeric, nullable=True)  # Махалля 1: ремесленных мастерских (шт.)
    s20_17 = Column(Numeric, nullable=True)  # Махалля 1: объём ремесл. производства (млрд сум)
    s20_18 = Column(Text, nullable=True)  # Махалля 2: название (текст)
    s20_19 = Column(Numeric, nullable=True)  # Махалля 2: ремесленных мастерских (шт.)
    s20_20 = Column(Numeric, nullable=True)  # Махалля 2: объём ремесл. производства (млрд сум)
    s20_21 = Column(Text, nullable=True)  # Махалля 3: название (текст)
    s20_22 = Column(Numeric, nullable=True)  # Махалля 3: ремесленных мастерских (шт.)
    s20_23 = Column(Numeric, nullable=True)  # Махалля 3: объём ремесл. производства (млрд сум)
    s20_24 = Column(Text, nullable=True)  # Махалля 4: название (текст)
    s20_25 = Column(Numeric, nullable=True)  # Махалля 4: ремесленных мастерских (шт.)
    s20_26 = Column(Numeric, nullable=True)  # Махалля 4: объём ремесл. производства (млрд сум)
    s20_27 = Column(Text, nullable=True)  # Махалля 5: название (текст)
    s20_28 = Column(Numeric, nullable=True)  # Махалля 5: ремесленных мастерских (шт.)
    s20_29 = Column(Numeric, nullable=True)  # Махалля 5: объём ремесл. производства (млрд сум)

    # ── §21 (15 fields) ──
    s21_1 = Column(Text, nullable=True)  # Проблема 1: название (текст)
    s21_2 = Column(Text, nullable=True)  # Проблема 1: приоритет (выс/ср/низ) (текст)
    s21_3 = Column(Numeric, nullable=True)  # Проблема 1: стоимость решения (млрд сум)
    s21_4 = Column(Text, nullable=True)  # Проблема 2: название (текст)
    s21_5 = Column(Text, nullable=True)  # Проблема 2: приоритет (выс/ср/низ) (текст)
    s21_6 = Column(Numeric, nullable=True)  # Проблема 2: стоимость решения (млрд сум)
    s21_7 = Column(Text, nullable=True)  # Проблема 3: название (текст)
    s21_8 = Column(Text, nullable=True)  # Проблема 3: приоритет (выс/ср/низ) (текст)
    s21_9 = Column(Numeric, nullable=True)  # Проблема 3: стоимость решения (млрд сум)
    s21_10 = Column(Text, nullable=True)  # Проблема 4: название (текст)
    s21_11 = Column(Text, nullable=True)  # Проблема 4: приоритет (выс/ср/низ) (текст)
    s21_12 = Column(Numeric, nullable=True)  # Проблема 4: стоимость решения (млрд сум)
    s21_13 = Column(Text, nullable=True)  # Проблема 5: название (текст)
    s21_14 = Column(Text, nullable=True)  # Проблема 5: приоритет (выс/ср/низ) (текст)
    s21_15 = Column(Numeric, nullable=True)  # Проблема 5: стоимость решения (млрд сум)

