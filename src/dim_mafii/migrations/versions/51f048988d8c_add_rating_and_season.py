"""Add rating and season

Revision ID: 51f048988d8c
Revises: 51e1e875662c

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '51f048988d8c'
down_revision = '51e1e875662c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'seasons',
        sa.Column(
            'season_id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('uuid_generate_v4()'),
            nullable=False
        ),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('start', sa.DateTime(), nullable=True),
        sa.Column('end', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('season_id')
    )
    op.create_table(
        'rating',
        sa.Column(
            'rating_id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('uuid_generate_v4()'),
            nullable=False
        ),
        sa.Column('player', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('mmr', sa.Integer(), nullable=True),
        sa.Column('season', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(('player',), ['players.player_id'], ),
        sa.ForeignKeyConstraint(('season',), ['seasons.season_id'], ),
        sa.PrimaryKeyConstraint('rating_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rating')
    op.drop_table('seasons')
    # ### end Alembic commands ###
