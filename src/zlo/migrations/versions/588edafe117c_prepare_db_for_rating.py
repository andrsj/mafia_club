"""Prepare DB for rating

Revision ID: 588edafe117c
Revises: 51f048988d8c

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '588edafe117c'
down_revision = '51f048988d8c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'rating',
        sa.Column(
            'club',
            sa.String(),
            nullable=False
        )
    )
    op.add_column(
        'games',
        sa.Column(
            'calculated',
            sa.Boolean,
            default=False,
            unique=False,
        )
    )
    op.execute("UPDATE games SET calculated = false")
    op.alter_column('games', 'calculated', nullable=False)
    op.add_column(
        'games',
        sa.Column(
            'season',
            postgresql.UUID(as_uuid=True)
        )
    )
    op.create_foreign_key(
        'fk_season_game',
        'games',
        'seasons',
        local_cols=['season'],
        remote_cols=['season_id'],
        ondelete='CASCADE'
    )

def downgrade():
    op.drop_column('rating', 'club')
    op.drop_column('games', 'calculated')
    op.drop_column('games', 'season')
