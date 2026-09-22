"""add submission idempotency constraint

Revision ID: a7f82c05cda9
Revises: bc228b00a5c5
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a7f82c05cda9"
down_revision: Union[str, Sequence[str], None] = "bc228b00a5c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_submissions_widget_idempotency_key",
        "submissions",
        ["widget_id", "idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_submissions_widget_idempotency_key",
        "submissions",
        type_="unique",
    )