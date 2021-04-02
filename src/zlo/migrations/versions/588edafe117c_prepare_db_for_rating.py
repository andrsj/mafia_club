"""Prepare DB for rating

Revision ID: 588edafe117c
Revises: 51f048988d8c

"""
from datetime import date
from uuid import uuid4


from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.dialects import postgresql


from zlo.domain.model import Game, Rating, Season, House


# revision identifiers, used by Alembic.
revision = '588edafe117c'
down_revision = '51f048988d8c'
branch_labels = None
depends_on = None


def upgrade():

    # Table with clubnames
    clubs = op.create_table(
        'clubs',
        sa.Column(
            'name',
            sa.String(),
            nullable=False,
            unique=True
        )
    )
    op.bulk_insert(clubs, [{'name': name} for name in ('ZLO', 'Школа Зло')])

    # Add foreign key to rating
    op.add_column(
        'rating',
        sa.Column(
            'club',
            sa.String(),
            nullable=False
        )
    )
    op.create_foreign_key(
        'fk_clubname_for_rating',
        'rating',
        'clubs',
        local_cols=['club'],
        remote_cols=['name'],
        ondelete='CASCADE'
    )

    # Update games
    # Add foreign key to club
    op.create_foreign_key(
        'fk_clubname_for_games',
        'games',
        'clubs',
        local_cols=['club'],
        remote_cols=['name'],
        ondelete='CASCADE'
    )
    # Add boolean column to games
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
    # Add foreign key to season
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

    # Add link to prew season
    op.add_column(
        'seasons',
        sa.Column(
            'prew_season',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('seasons.season_id')
        )
    )

    # Write rating for first season:

    players_ids = []

    start_day = date(day=1, month=1, year=2021)
    end_day = date(day=31, month=1, year=2021)

    session = Session(bind=op.get_bind())
    with session.begin(subtransactions=True):
        for game in session.query(Game)\
                .filter(Game.date >= start_day)\
                .filter(Game.date <= end_day):
            for house in session.query(House).filter_by(game_id=game.game_id):
                players_ids.append(house.player_id)

        season = Season(
            season_id=str(uuid4()),
            name="First season",
            start=start_day,
            end=end_day,
        )

    # TODO insert rating

def downgrade():
    op.drop_constraint(constraint_name='fk_clubname_for_games', table_name='games', type_="foreignkey")
    op.drop_constraint(constraint_name='fk_clubname_for_rating', table_name='rating', type_="foreignkey")
    op.drop_table('clubs')
    op.drop_column('rating', 'club')
    op.drop_column('games', 'calculated')
    op.drop_column('games', 'season')
    op.drop_column('seasons', 'prew_season')
