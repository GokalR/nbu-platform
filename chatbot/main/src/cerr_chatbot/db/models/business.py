"""Phase 2A: Business directory schema.

Four tables imported from `chatbot/business/`:
- `tnved_categories`        — TN_VED code dictionary (HS classification, RU).
- `business_companies`      — OKED.xlsx: all registered companies (167k).
- `business_imports`        — TN_VED.xlsx "Ойоғи": import-declaration line items.
- `business_import_summaries` — TN_VED.xlsx "Мижозлар бўйича": per-importer aggregates.

Lineage and join-key conventions mirror the existing CERR analytics tables:
surrogate BigInt PKs, FKs only on surrogate ids, natural keys stored but never
joined on, every fact row carries `import_run_id` so views can filter to the
latest completed snapshot.

OKED companies resolve to `region_id` + `district_id` only (no mahalla).
Imports also try to resolve `mahalla_id` (NULL when the mahalla name does not
fuzzy-match a known mahalla).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import (
    BigInteger,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from cerr_chatbot.db.base import Base, BigIntPk, JsonbType


class TnvedCategory(Base):
    """TN_VED code → description dictionary (~28k rows).

    Code is a string (kept verbatim, including leading zeros). `chapter` is the
    first 2 digits, useful for HS chapter aggregations ("show imports of food
    products" → chapter LIKE '02%' etc).
    """

    __tablename__ = "tnved_categories"

    tnved_category_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_row_index: Mapped[int] = mapped_column(Integer, nullable=False)

    tnved_code: Mapped[str] = mapped_column(String(16), nullable=False)
    description_ru: Mapped[str | None] = mapped_column(Text)
    chapter: Mapped[str | None] = mapped_column(String(2))
    heading: Mapped[str | None] = mapped_column(String(4))

    __table_args__ = (
        UniqueConstraint(
            "import_run_id", "source_file", "source_row_index", name="uq_tnved_category_lineage"
        ),
        Index("ix_tnved_categories_tnved_code", "tnved_code"),
        Index("ix_tnved_categories_chapter", "chapter"),
        Index("ix_tnved_categories_import_run_id", "import_run_id"),
    )


class BusinessCompany(Base):
    """One row per registered company from OKED.xlsx (~167k rows).

    Geography resolved by Cyrillic-normalised name match against the existing
    `regions` / `districts` tables. Match misses leave the FK NULL — the company
    still imports but won't appear in district-scoped queries.
    """

    __tablename__ = "business_companies"

    company_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_row_index: Mapped[int] = mapped_column(Integer, nullable=False)

    inn: Mapped[str | None] = mapped_column(String(16))
    client_code: Mapped[str | None] = mapped_column(String(16))
    company_name: Mapped[str | None] = mapped_column(Text)
    client_type_cyr: Mapped[str | None] = mapped_column(Text)
    address_raw: Mapped[str | None] = mapped_column(Text)
    country_name_cyr: Mapped[str | None] = mapped_column(Text)

    region_name_raw_cyr: Mapped[str | None] = mapped_column(Text)
    district_name_raw_cyr: Mapped[str | None] = mapped_column(Text)

    region_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("regions.region_id"))
    district_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("districts.district_id"))

    oked_label_ru: Mapped[str | None] = mapped_column(Text)
    oked_label_uz: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "import_run_id", "source_file", "source_row_index", name="uq_business_company_lineage"
        ),
        Index("ix_business_companies_inn", "inn"),
        Index("ix_business_companies_region_id", "region_id"),
        Index("ix_business_companies_district_id", "district_id"),
        Index("ix_business_companies_import_run_id", "import_run_id"),
    )


class BusinessImport(Base):
    """One row per TN_VED line on an import declaration (~427k rows).

    Importer geography is resolved from the explicit regional/district/mahalla
    name columns the customs export ships with — these are typically a clean
    triple, so mahalla resolution succeeds where the mahalla name matches a
    known mahalla in the CERR snapshot.
    """

    __tablename__ = "business_imports"

    business_import_id: Mapped[int] = mapped_column(BigIntPk, primary_key=True, autoincrement=True)
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_row_index: Mapped[int] = mapped_column(Integer, nullable=False)

    inn: Mapped[str | None] = mapped_column(String(16))
    company_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("business_companies.company_id")
    )
    company_name: Mapped[str | None] = mapped_column(Text)

    contract_number: Mapped[str | None] = mapped_column(String(64))
    declaration_number: Mapped[str | None] = mapped_column(String(32))
    declaration_date: Mapped[date | None] = mapped_column(Date)

    region_name_raw_cyr: Mapped[str | None] = mapped_column(Text)
    district_name_raw_cyr: Mapped[str | None] = mapped_column(Text)
    mahalla_name_raw_cyr: Mapped[str | None] = mapped_column(Text)
    region_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("regions.region_id"))
    district_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("districts.district_id"))
    mahalla_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("mahallas.mahalla_id"))

    tnved_code: Mapped[str | None] = mapped_column(String(16))
    tnved_chapter: Mapped[str | None] = mapped_column(String(2))

    currency_code: Mapped[str | None] = mapped_column(String(8))
    origin_country_code: Mapped[str | None] = mapped_column(String(8))
    invoice_value_total: Mapped[float | None] = mapped_column(Float)
    invoice_value_item: Mapped[float | None] = mapped_column(Float)
    value_usd: Mapped[float | None] = mapped_column(Float)
    exchange_rate: Mapped[float | None] = mapped_column(Float)

    item_description: Mapped[str | None] = mapped_column(Text)
    raw_row_json: Mapped[Any | None] = mapped_column(JsonbType)

    __table_args__ = (
        UniqueConstraint(
            "import_run_id", "source_file", "source_row_index", name="uq_business_import_lineage"
        ),
        Index("ix_business_imports_inn", "inn"),
        Index("ix_business_imports_company_id", "company_id"),
        Index("ix_business_imports_tnved_code", "tnved_code"),
        Index("ix_business_imports_tnved_chapter", "tnved_chapter"),
        Index("ix_business_imports_region_id", "region_id"),
        Index("ix_business_imports_district_id", "district_id"),
        Index("ix_business_imports_mahalla_id", "mahalla_id"),
        Index("ix_business_imports_declaration_date", "declaration_date"),
        Index("ix_business_imports_import_run_id", "import_run_id"),
    )


class BusinessImportSummary(Base):
    """One row per importer aggregated across 12 product categories (~3k rows).

    Pre-aggregated by the source. Each `value_*_usd` column is the importer's
    total spend in that product category over the snapshot window (2024-2025).
    All numeric fields are in USD (transformed by source from declaration
    currencies via daily FX).
    """

    __tablename__ = "business_import_summaries"

    business_import_summary_id: Mapped[int] = mapped_column(
        BigIntPk, primary_key=True, autoincrement=True
    )
    import_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_runs.import_run_id"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_row_index: Mapped[int] = mapped_column(Integer, nullable=False)

    inn: Mapped[str | None] = mapped_column(String(16))
    company_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("business_companies.company_id")
    )
    company_name: Mapped[str | None] = mapped_column(Text)

    total_import_usd: Mapped[float | None] = mapped_column(Float)
    value_machines_usd: Mapped[float | None] = mapped_column(Float)
    value_chemicals_usd: Mapped[float | None] = mapped_column(Float)
    value_misc_goods_usd: Mapped[float | None] = mapped_column(Float)
    value_industrial_usd: Mapped[float | None] = mapped_column(Float)
    value_animal_oils_usd: Mapped[float | None] = mapped_column(Float)
    value_non_food_raw_usd: Mapped[float | None] = mapped_column(Float)
    value_building_mats_usd: Mapped[float | None] = mapped_column(Float)
    value_food_products_usd: Mapped[float | None] = mapped_column(Float)
    value_fruit_veg_usd: Mapped[float | None] = mapped_column(Float)
    value_mineral_fuel_usd: Mapped[float | None] = mapped_column(Float)
    value_beverages_tobacco_usd: Mapped[float | None] = mapped_column(Float)
    value_other_goods_usd: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        UniqueConstraint(
            "import_run_id",
            "source_file",
            "source_row_index",
            name="uq_business_import_summary_lineage",
        ),
        Index("ix_business_import_summaries_inn", "inn"),
        Index("ix_business_import_summaries_company_id", "company_id"),
        Index("ix_business_import_summaries_import_run_id", "import_run_id"),
    )
