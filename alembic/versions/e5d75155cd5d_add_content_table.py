"""add content table

Revision ID: e5d75155cd5d
Revises: 9543c8d9c6b9
Create Date: 2024-01-17 08:47:46.940182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5d75155cd5d'
down_revision: Union[str, None] = '9543c8d9c6b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
