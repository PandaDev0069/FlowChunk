"""initial

Revision ID: 1854893b6083
Revises:
Create Date: 2026-06-07 13:04:34.679995

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "1854893b6083"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
