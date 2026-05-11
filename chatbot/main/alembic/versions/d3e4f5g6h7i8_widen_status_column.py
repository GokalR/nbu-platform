"""Phase 2A: widen import_runs.status to fit business-import status values

Revision ID: d3e4f5g6h7i8
Revises: c2d3e4f5g6h7
Create Date: 2026-05-11 13:05:00.000000

The baseline column was VARCHAR(16). Business-import status values like
'completed_business' (18 chars) and 'running_business' (16 chars — exactly at
the boundary) overflow. Widen to VARCHAR(32) for headroom.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from cerr_chatbot.db.views import (
    BUSINESS_CREATE_VIEW_STATEMENTS,
    BUSINESS_DROP_VIEW_STATEMENTS,
    CREATE_VIEW_STATEMENTS,
    DROP_VIEW_STATEMENTS,
)

revision: str = "d3e4f5g6h7i8"
down_revision: Union[str, None] = "c2d3e4f5g6h7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Every CERR + business view filters on import_runs.status, so PostgreSQL
    # refuses ALTER COLUMN TYPE while views depend on it. Drop all views, alter
    # the column, recreate the same views.
    for stmt in BUSINESS_DROP_VIEW_STATEMENTS:
        op.execute(stmt)
    for stmt in DROP_VIEW_STATEMENTS:
        op.execute(stmt)
    op.alter_column(
        "import_runs",
        "status",
        existing_type=sa.String(length=16),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
    for stmt in CREATE_VIEW_STATEMENTS:
        op.execute(stmt)
    for stmt in BUSINESS_CREATE_VIEW_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in BUSINESS_DROP_VIEW_STATEMENTS:
        op.execute(stmt)
    for stmt in DROP_VIEW_STATEMENTS:
        op.execute(stmt)
    op.alter_column(
        "import_runs",
        "status",
        existing_type=sa.String(length=32),
        type_=sa.String(length=16),
        existing_nullable=False,
    )
    for stmt in CREATE_VIEW_STATEMENTS:
        op.execute(stmt)
    for stmt in BUSINESS_CREATE_VIEW_STATEMENTS:
        op.execute(stmt)
