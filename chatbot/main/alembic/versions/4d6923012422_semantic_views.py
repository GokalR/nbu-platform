"""semantic views

Revision ID: 4d6923012422
Revises: 770ec9ae0fcc
Create Date: 2026-05-10 03:17:53.584684
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from cerr_chatbot.db.views import CREATE_VIEW_STATEMENTS, DROP_VIEW_STATEMENTS

# revision identifiers, used by Alembic.
revision: str = '4d6923012422'
down_revision: Union[str, None] = '770ec9ae0fcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for stmt in CREATE_VIEW_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DROP_VIEW_STATEMENTS:
        op.execute(stmt)
