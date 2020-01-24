"""Add advanced game result

Revision ID: d48548d1942e
Revises: 4a61cbf0877e
Create Date: 2020-01-19 22:32:26.295811

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd48548d1942e'
down_revision = '4a61cbf0877e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('advance_result', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'advance_result')
    # ### end Alembic commands ###
