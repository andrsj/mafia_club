"""ok

Revision ID: 51e1e875662c
Revises: 2980eec614d7

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '51e1e875662c'
down_revision = '2980eec614d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bonuses_from_heading',
    sa.Column('bonus_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ),
    sa.ForeignKeyConstraint(['house_id'], ['houses.house_id'], ),
    sa.PrimaryKeyConstraint('bonus_id')
    )
    op.create_table('breaks',
    sa.Column('devise_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house_from', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house_to', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ),
    sa.ForeignKeyConstraint(['house_from'], ['houses.house_id'], ),
    sa.ForeignKeyConstraint(['house_to'], ['houses.house_id'], ),
    sa.PrimaryKeyConstraint('devise_id')
    )
    op.create_table('devises',
    sa.Column('devise_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('killed_house', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house_1', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house_2', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house_3', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ),
    sa.ForeignKeyConstraint(['house_1'], ['houses.house_id'], ),
    sa.ForeignKeyConstraint(['house_2'], ['houses.house_id'], ),
    sa.ForeignKeyConstraint(['house_3'], ['houses.house_id'], ),
    sa.ForeignKeyConstraint(['killed_house'], ['houses.house_id'], ),
    sa.PrimaryKeyConstraint('devise_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('devises')
    op.drop_table('breaks')
    op.drop_table('bonuses_from_heading')
    # ### end Alembic commands ###
