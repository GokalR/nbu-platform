"""Phase 2A: extend import_runs.status allowlist for business imports

Revision ID: c2d3e4f5g6h7
Revises: b1f3c2d8a9e0
Create Date: 2026-05-11 12:55:00.000000

The baseline check constraint allowed only ('running', 'completed', 'failed',
'aborted'). Business imports use namespaced status values so the existing CERR
latest-run subquery (WHERE status='completed') never mistakes a business run
for a CERR run.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "c2d3e4f5g6h7"
down_revision: Union[str, None] = "b1f3c2d8a9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("status_allowed", "import_runs", type_="check")
    op.create_check_constraint(
        "status_allowed",
        "import_runs",
        "status IN ("
        "'running', 'completed', 'failed', 'aborted', "
        "'running_business', 'completed_business', 'failed_business'"
        ")",
    )


def downgrade() -> None:
    op.drop_constraint("status_allowed", "import_runs", type_="check")
    op.create_check_constraint(
        "status_allowed",
        "import_runs",
        "status IN ('running', 'completed', 'failed', 'aborted')",
    )
