"""Phase 2A: business directory tables + views

Revision ID: b1f3c2d8a9e0
Revises: 4d6923012422
Create Date: 2026-05-11 02:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

from cerr_chatbot.db.views import (
    BUSINESS_CREATE_VIEW_STATEMENTS,
    BUSINESS_DROP_VIEW_STATEMENTS,
)

revision: str = "b1f3c2d8a9e0"
down_revision: Union[str, None] = "4d6923012422"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Mirrors cerr_chatbot.db.base.JsonbType (JSONB on postgres, JSON elsewhere).
_JSONB_TYPE = sa.JSON().with_variant(JSONB(), "postgresql")
# Mirrors cerr_chatbot.db.base.BigIntPk (Integer on sqlite, BigInteger elsewhere).
_BIGINT_PK = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "tnved_categories",
        sa.Column("tnved_category_id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("import_run_id", sa.BigInteger(), nullable=False),
        sa.Column("source_file", sa.Text(), nullable=False),
        sa.Column("source_row_index", sa.Integer(), nullable=False),
        sa.Column("tnved_code", sa.String(length=16), nullable=False),
        sa.Column("description_ru", sa.Text(), nullable=True),
        sa.Column("chapter", sa.String(length=2), nullable=True),
        sa.Column("heading", sa.String(length=4), nullable=True),
        sa.ForeignKeyConstraint(
            ["import_run_id"], ["import_runs.import_run_id"],
            name="fk_tnved_categories_import_run_id_import_runs",
        ),
        sa.PrimaryKeyConstraint("tnved_category_id", name="pk_tnved_categories"),
        sa.UniqueConstraint(
            "import_run_id", "source_file", "source_row_index", name="uq_tnved_category_lineage"
        ),
    )
    op.create_index("ix_tnved_categories_tnved_code", "tnved_categories", ["tnved_code"])
    op.create_index("ix_tnved_categories_chapter", "tnved_categories", ["chapter"])
    op.create_index("ix_tnved_categories_import_run_id", "tnved_categories", ["import_run_id"])

    op.create_table(
        "business_companies",
        sa.Column("company_id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("import_run_id", sa.BigInteger(), nullable=False),
        sa.Column("source_file", sa.Text(), nullable=False),
        sa.Column("source_row_index", sa.Integer(), nullable=False),
        sa.Column("inn", sa.String(length=16), nullable=True),
        sa.Column("client_code", sa.String(length=16), nullable=True),
        sa.Column("company_name", sa.Text(), nullable=True),
        sa.Column("client_type_cyr", sa.Text(), nullable=True),
        sa.Column("address_raw", sa.Text(), nullable=True),
        sa.Column("country_name_cyr", sa.Text(), nullable=True),
        sa.Column("region_name_raw_cyr", sa.Text(), nullable=True),
        sa.Column("district_name_raw_cyr", sa.Text(), nullable=True),
        sa.Column("region_id", sa.BigInteger(), nullable=True),
        sa.Column("district_id", sa.BigInteger(), nullable=True),
        sa.Column("oked_label_ru", sa.Text(), nullable=True),
        sa.Column("oked_label_uz", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["import_run_id"], ["import_runs.import_run_id"],
            name="fk_business_companies_import_run_id_import_runs",
        ),
        sa.ForeignKeyConstraint(
            ["region_id"], ["regions.region_id"],
            name="fk_business_companies_region_id_regions",
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["districts.district_id"],
            name="fk_business_companies_district_id_districts",
        ),
        sa.PrimaryKeyConstraint("company_id", name="pk_business_companies"),
        sa.UniqueConstraint(
            "import_run_id", "source_file", "source_row_index", name="uq_business_company_lineage"
        ),
    )
    op.create_index("ix_business_companies_inn", "business_companies", ["inn"])
    op.create_index("ix_business_companies_region_id", "business_companies", ["region_id"])
    op.create_index("ix_business_companies_district_id", "business_companies", ["district_id"])
    op.create_index(
        "ix_business_companies_import_run_id", "business_companies", ["import_run_id"]
    )

    op.create_table(
        "business_imports",
        sa.Column("business_import_id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("import_run_id", sa.BigInteger(), nullable=False),
        sa.Column("source_file", sa.Text(), nullable=False),
        sa.Column("source_row_index", sa.Integer(), nullable=False),
        sa.Column("inn", sa.String(length=16), nullable=True),
        sa.Column("company_id", sa.BigInteger(), nullable=True),
        sa.Column("company_name", sa.Text(), nullable=True),
        sa.Column("contract_number", sa.String(length=64), nullable=True),
        sa.Column("declaration_number", sa.String(length=32), nullable=True),
        sa.Column("declaration_date", sa.Date(), nullable=True),
        sa.Column("region_name_raw_cyr", sa.Text(), nullable=True),
        sa.Column("district_name_raw_cyr", sa.Text(), nullable=True),
        sa.Column("mahalla_name_raw_cyr", sa.Text(), nullable=True),
        sa.Column("region_id", sa.BigInteger(), nullable=True),
        sa.Column("district_id", sa.BigInteger(), nullable=True),
        sa.Column("mahalla_id", sa.BigInteger(), nullable=True),
        sa.Column("tnved_code", sa.String(length=16), nullable=True),
        sa.Column("tnved_chapter", sa.String(length=2), nullable=True),
        sa.Column("currency_code", sa.String(length=8), nullable=True),
        sa.Column("origin_country_code", sa.String(length=8), nullable=True),
        sa.Column("invoice_value_total", sa.Float(), nullable=True),
        sa.Column("invoice_value_item", sa.Float(), nullable=True),
        sa.Column("value_usd", sa.Float(), nullable=True),
        sa.Column("exchange_rate", sa.Float(), nullable=True),
        sa.Column("item_description", sa.Text(), nullable=True),
        sa.Column("raw_row_json", _JSONB_TYPE, nullable=True),
        sa.ForeignKeyConstraint(
            ["import_run_id"], ["import_runs.import_run_id"],
            name="fk_business_imports_import_run_id_import_runs",
        ),
        sa.ForeignKeyConstraint(
            ["company_id"], ["business_companies.company_id"],
            name="fk_business_imports_company_id_business_companies",
        ),
        sa.ForeignKeyConstraint(
            ["region_id"], ["regions.region_id"],
            name="fk_business_imports_region_id_regions",
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["districts.district_id"],
            name="fk_business_imports_district_id_districts",
        ),
        sa.ForeignKeyConstraint(
            ["mahalla_id"], ["mahallas.mahalla_id"],
            name="fk_business_imports_mahalla_id_mahallas",
        ),
        sa.PrimaryKeyConstraint("business_import_id", name="pk_business_imports"),
        sa.UniqueConstraint(
            "import_run_id", "source_file", "source_row_index", name="uq_business_import_lineage"
        ),
    )
    op.create_index("ix_business_imports_inn", "business_imports", ["inn"])
    op.create_index("ix_business_imports_company_id", "business_imports", ["company_id"])
    op.create_index("ix_business_imports_tnved_code", "business_imports", ["tnved_code"])
    op.create_index("ix_business_imports_tnved_chapter", "business_imports", ["tnved_chapter"])
    op.create_index("ix_business_imports_region_id", "business_imports", ["region_id"])
    op.create_index("ix_business_imports_district_id", "business_imports", ["district_id"])
    op.create_index("ix_business_imports_mahalla_id", "business_imports", ["mahalla_id"])
    op.create_index(
        "ix_business_imports_declaration_date", "business_imports", ["declaration_date"]
    )
    op.create_index(
        "ix_business_imports_import_run_id", "business_imports", ["import_run_id"]
    )

    op.create_table(
        "business_import_summaries",
        sa.Column("business_import_summary_id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("import_run_id", sa.BigInteger(), nullable=False),
        sa.Column("source_file", sa.Text(), nullable=False),
        sa.Column("source_row_index", sa.Integer(), nullable=False),
        sa.Column("inn", sa.String(length=16), nullable=True),
        sa.Column("company_id", sa.BigInteger(), nullable=True),
        sa.Column("company_name", sa.Text(), nullable=True),
        sa.Column("total_import_usd", sa.Float(), nullable=True),
        sa.Column("value_machines_usd", sa.Float(), nullable=True),
        sa.Column("value_chemicals_usd", sa.Float(), nullable=True),
        sa.Column("value_misc_goods_usd", sa.Float(), nullable=True),
        sa.Column("value_industrial_usd", sa.Float(), nullable=True),
        sa.Column("value_animal_oils_usd", sa.Float(), nullable=True),
        sa.Column("value_non_food_raw_usd", sa.Float(), nullable=True),
        sa.Column("value_building_mats_usd", sa.Float(), nullable=True),
        sa.Column("value_food_products_usd", sa.Float(), nullable=True),
        sa.Column("value_fruit_veg_usd", sa.Float(), nullable=True),
        sa.Column("value_mineral_fuel_usd", sa.Float(), nullable=True),
        sa.Column("value_beverages_tobacco_usd", sa.Float(), nullable=True),
        sa.Column("value_other_goods_usd", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["import_run_id"], ["import_runs.import_run_id"],
            name="fk_business_import_summaries_import_run_id_import_runs",
        ),
        sa.ForeignKeyConstraint(
            ["company_id"], ["business_companies.company_id"],
            name="fk_business_import_summaries_company_id_business_companies",
        ),
        sa.PrimaryKeyConstraint(
            "business_import_summary_id", name="pk_business_import_summaries"
        ),
        sa.UniqueConstraint(
            "import_run_id",
            "source_file",
            "source_row_index",
            name="uq_business_import_summary_lineage",
        ),
    )
    op.create_index(
        "ix_business_import_summaries_inn", "business_import_summaries", ["inn"]
    )
    op.create_index(
        "ix_business_import_summaries_company_id", "business_import_summaries", ["company_id"]
    )
    op.create_index(
        "ix_business_import_summaries_import_run_id",
        "business_import_summaries",
        ["import_run_id"],
    )

    for stmt in BUSINESS_CREATE_VIEW_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in BUSINESS_DROP_VIEW_STATEMENTS:
        op.execute(stmt)
    op.drop_index(
        "ix_business_import_summaries_import_run_id", table_name="business_import_summaries"
    )
    op.drop_index(
        "ix_business_import_summaries_company_id", table_name="business_import_summaries"
    )
    op.drop_index("ix_business_import_summaries_inn", table_name="business_import_summaries")
    op.drop_table("business_import_summaries")

    op.drop_index("ix_business_imports_import_run_id", table_name="business_imports")
    op.drop_index("ix_business_imports_declaration_date", table_name="business_imports")
    op.drop_index("ix_business_imports_mahalla_id", table_name="business_imports")
    op.drop_index("ix_business_imports_district_id", table_name="business_imports")
    op.drop_index("ix_business_imports_region_id", table_name="business_imports")
    op.drop_index("ix_business_imports_tnved_chapter", table_name="business_imports")
    op.drop_index("ix_business_imports_tnved_code", table_name="business_imports")
    op.drop_index("ix_business_imports_company_id", table_name="business_imports")
    op.drop_index("ix_business_imports_inn", table_name="business_imports")
    op.drop_table("business_imports")

    op.drop_index("ix_business_companies_import_run_id", table_name="business_companies")
    op.drop_index("ix_business_companies_district_id", table_name="business_companies")
    op.drop_index("ix_business_companies_region_id", table_name="business_companies")
    op.drop_index("ix_business_companies_inn", table_name="business_companies")
    op.drop_table("business_companies")

    op.drop_index("ix_tnved_categories_import_run_id", table_name="tnved_categories")
    op.drop_index("ix_tnved_categories_chapter", table_name="tnved_categories")
    op.drop_index("ix_tnved_categories_tnved_code", table_name="tnved_categories")
    op.drop_table("tnved_categories")
