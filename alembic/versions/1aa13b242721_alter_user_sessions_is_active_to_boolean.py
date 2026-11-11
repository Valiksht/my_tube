"""alter user_sessions is_active to boolean

Revision ID: 1aa13b242721
Revises: 8817bb8f02d3
Create Date: 2026-11-12 00:40:19.805968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1aa13b242721'
down_revision: Union[str, Sequence[str], None] = '8817bb8f02d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменить тип колонки is_active с VARCHAR(1) на BOOLEAN
    # Используем USING для явной конвертации значений
    op.alter_column(
        'user_sessions',
        'is_active',
        type_=sa.Boolean(),
        existing_type=sa.VARCHAR(length=1),
        nullable=False,
        postgresql_using="is_active::boolean",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'user_sessions',
        'is_active',
        type_=sa.VARCHAR(length=1),
        existing_type=sa.Boolean(),
        nullable=False,
    )
    # Вернуть строковые значения
    op.execute("UPDATE user_sessions SET is_active = CASE WHEN is_active THEN '1' ELSE '0' END")
