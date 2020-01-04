"""сreate_tables

Revision ID: 1cca555484a7
Revises: 
Create Date: 2019-10-16 19:01:57.091851

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1cca555484a7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'players',
        sa.Column('player_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'),
                  nullable=False),
        sa.Column('nickname', sa.String(length=40), nullable=False),
        sa.Column('name', sa.String(length=40), nullable=True),
        sa.Column('club', sa.String(length=40), nullable=True),
        sa.PrimaryKeyConstraint('player_id')
    )
    op.create_table(
        'houses',
        sa.Column('house_id', postgresql.UUID(as_uuid=True),
                  server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Integer(), nullable=False),
        sa.Column('slot', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.player_id']),
        sa.PrimaryKeyConstraint('house_id')
    )
    op.create_table(
        'games',
        sa.Column('game_id', postgresql.UUID(as_uuid=True),
                  server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('date', sa.DateTime()),
        sa.Column('result', sa.Integer(), nullable=False),
        sa.Column('club', sa.String(length=40), nullable=True),
        sa.Column('table', sa.Integer(), nullable=True),
        sa.Column('heading', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tournament', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['heading'], ['players.player_id'], ),
        sa.PrimaryKeyConstraint('game_id')
    )



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('games')
    op.drop_table('houses')
    op.drop_table('players')
    # ### end Alembic commands ###
