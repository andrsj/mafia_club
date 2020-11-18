"""Add sheriff_version and disqualifield

Revision ID: cdf9b654ec97
Revises: 85e2fd6720da
Create Date: 2020-10-04 18:53:36.319144

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cdf9b654ec97'
down_revision = '85e2fd6720da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('disqualifieds',
    sa.Column('disqualified_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ),
    sa.ForeignKeyConstraint(['house'], ['houses.house_id'], ),
    sa.PrimaryKeyConstraint('disqualified_id')
    )
    op.create_table('sheriffversions',
    sa.Column('sheriff_version_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('house', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.game_id'], ),
    sa.ForeignKeyConstraint(['house'], ['houses.house_id'], ),
    sa.PrimaryKeyConstraint('sheriff_version_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sheriffversions')
    op.drop_table('disqualifieds')
    # ### end Alembic commands ###