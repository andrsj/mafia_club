"""Add displayname for players

Revision ID: 0bc99e8caf95
Revises: 588edafe117c
Create Date: 2021-04-12 19:41:47.678983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bc99e8caf95'
down_revision = '588edafe117c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('players', sa.Column('displayname', sa.String(length=40), nullable=True))


def downgrade():
    op.drop_column('players', 'displayname')

