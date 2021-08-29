import retrying
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm.exc
from sqlalchemy import (Table, Column, Integer, String, create_engine,
                        MetaData, DateTime, func, ForeignKey, Float, Boolean)
from sqlalchemy.orm import mapper, scoped_session, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from dim_mafii.domain.infrastructure import UnitOfWork, UnitOfWorkManager
from dim_mafii.domain import model
from dim_mafii.adapters import repositories

def isretryable(exn):
    """
    Return true is this is a retryable sqlalchemy error.
    Right now we retry connection issues and concurrent modification problems.
    Integrity errors, data errors etc. are not recoverable, so we return false.
    """

    if (
            isinstance(exn, sqlalchemy.exc.DisconnectionError)
            or isinstance(exn, sqlalchemy.exc.TimeoutError)
            or isinstance(exn, sqlalchemy.orm.exc.ConcurrentModificationError)
    ):
        return True
    return False


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: sqlalchemy.orm.Session = self.session_factory()
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    @retrying.retry(
        wait_exponential_multiplier=200,
        wait_exponential_max=3000,
        stop_max_delay=15000,
        retry_on_exception=isretryable,
    )
    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def flush(self):
        self.session.flush()

    @property
    def players(self):
        return repositories.PlayerRepository(self.session)

    @property
    def houses(self):
        return repositories.HouseRepository(self.session)

    @property
    def games(self):
        return repositories.GameRepository(self.session)

    @property
    def best_moves(self):
        return repositories.BestMoveRepository(self.session)

    @property
    def sheriff_versions(self):
        return repositories.SheriffVersionRepository(self.session)

    @property
    def disqualifieds(self):
        return repositories.DisqualifiedRepository(self.session)

    @property
    def nominated_for_best(self):
        return repositories.NominatedForBestRepository(self.session)

    @property
    def voted(self):
        return repositories.VotedRepository(self.session)

    @property
    def hand_of_mafia(self):
        return repositories.HandOfMafiaRepository(self.session)

    @property
    def kills(self):
        return repositories.KillsRepository(self.session)

    @property
    def misses(self):
        return repositories.MissesRepository(self.session)

    @property
    def don_checks(self):
        return repositories.DonChecksRepository(self.session)

    @property
    def sheriff_checks(self):
        return repositories.SheriffChecksRepository(self.session)

    @property
    def bonuses_tolerant(self):
        return repositories.BonusTolerantRepository(self.session)

    @property
    def bonuses_from_players(self):
        return repositories.BonusFromPlayersRepository(self.session)

    @property
    def bonuses_from_heading(self):
        return repositories.BonusHeadingRepository(self.session)

    @property
    def devises(self):
        return repositories.DeviseRepository(self.session)

    @property
    def breaks(self):
        return repositories.BreakRepository(self.session)

    @property
    def season(self):
        return repositories.SeasonRepository(self.session)

    @property
    def rating(self):
        return repositories.RatingRepository(self.session)


class SqlAlchemyUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self, session_maker):
        self.session_maker = session_maker

    def start(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_maker)


class DatabaseSchema:

    def __init__(self):
        self._configured = False

    def create_all(self):
        assert self._configured
        self._metadata.create_all()

    def configure(self, metadata):
        assert not self._configured
        self._configured = True
        self._metadata = metadata
        self.players = Table(
            "players",
            self._metadata,
            Column(
                "player_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("nickname", String(40), unique=True, nullable=False),
            Column("displayname", String(40)),
            Column("name", String(40)),
            Column("club", String(40)),
        )
        self.games = Table(
            "games",
            self._metadata,
            Column(
                "game_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("date", DateTime, default=func.now()),
            Column("result", Integer, default=0),
            Column('advance_result', Integer),
            # Column("club", String(40)),
            Column("club",  ForeignKey('clubs.name', name='fk_clubname_for_games'), nullable=False),
            Column("season", ForeignKey('seasons.season_id', name='fk_season_game')),
            Column("calculated", Boolean, nullable=False, default=False),
            Column("table", Integer, default=None),
            Column("heading", ForeignKey("players.player_id")),
            Column("tournament", String(40))
        )
        self.houses = Table(
            "houses",
            self._metadata,
            Column(
                "house_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("player_id", ForeignKey("players.player_id")),
            Column("game_id", ForeignKey("games.game_id")),
            Column("slot", Integer),
            Column("role", Integer),
            Column("bonus_mark", Float),
            Column("fouls", Integer)
        )
        self.best_moves = Table(
            "best_moves",
            self._metadata,
            Column(
                "best_move_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id"), unique=True),
            Column("killed_house", ForeignKey("houses.house_id")),
            Column("best_1", ForeignKey("houses.house_id")),
            Column("best_2", ForeignKey("houses.house_id")),
            Column("best_3", ForeignKey("houses.house_id")),
        )
        self.disqualifieds = Table(
            "disqualifieds",
            self._metadata,
            Column(
                "disqualified_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house", ForeignKey("houses.house_id")),
        )
        self.sheriff_versions = Table(
            "sheriff_versions",
            self._metadata,
            Column(
                "sheriff_version_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house", ForeignKey("houses.house_id")),
        )
        self.nominated_for_best = Table(
            "nominated_for_best",
            self._metadata,
            Column(
                "nominated_for_best_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house", ForeignKey("houses.house_id")),
        )
        self.votes = Table(
            "voted",
            self._metadata,
            Column(
                "voted_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house_id", ForeignKey("houses.house_id")),
            Column("day", Integer)
        )
        self.hand_of_mafia = Table(
            "hand_of_mafia",
            self._metadata,
            Column(
                "hand_of_mafia_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house_hand_id", ForeignKey("houses.house_id")),
            Column("victim_id", ForeignKey("houses.house_id"))
        )
        self.kills = Table(
            "kills",
            self._metadata,
            Column(
                "kill_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("killed_house_id", ForeignKey("houses.house_id")),
            Column("circle_number", Integer)
        )
        self.misses = Table(
            "misses",
            self._metadata,
            Column(
                "miss_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house_id", ForeignKey("houses.house_id")),
            Column("circle_number", Integer)
        )
        self.don_checks = Table(
            "don_checks",
            self._metadata,
            Column(
                "don_check_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("checked_house_id", ForeignKey("houses.house_id")),
            Column("circle_number", Integer)
        )
        self.sheriff_checks = Table(
            "sheriff_checks",
            self._metadata,
            Column(
                "sheriff_check_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("checked_house_id", ForeignKey("houses.house_id")),
            Column("circle_number", Integer)
        )
        self.bonuses_tolerant = Table(
            "bonuses_tolerant",
            self._metadata,
            Column(
                "bonus_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house_from_id", ForeignKey("houses.house_id")),
            Column("house_to_id", ForeignKey("houses.house_id")),
        )
        self.bonuses_from_players = Table(
            "bonuses_from_players",
            self._metadata,
            Column(
                "bonus_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("bonus_from", ForeignKey("houses.house_id")),
            Column("bonus_to", ForeignKey("houses.house_id")),
        )
        self.bonuses_from_heading = Table(
            "bonuses_from_heading",
            self._metadata,
            Column(
                "bonus_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house_id", ForeignKey("houses.house_id")),
            Column("value", Float)
        )
        self.devises = Table(
            "devises",
            self._metadata,
            Column(
                "devise_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("killed_house", ForeignKey("houses.house_id")),
            Column("house_1", ForeignKey("houses.house_id")),
            Column("house_2", ForeignKey("houses.house_id")),
            Column("house_3", ForeignKey("houses.house_id")),
        )
        self.breaks = Table(
            "breaks",
            self._metadata,
            Column(
                "break_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", ForeignKey("games.game_id")),
            Column("house_from", ForeignKey("houses.house_id")),
            Column("house_to", ForeignKey("houses.house_id")),
            Column("count", Integer),
        )

        self.season = Table(
            'seasons',
            self._metadata,
            Column(
                'season_id',
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column('name', String),
            Column('start', DateTime, default=func.now()),
            Column('end', DateTime, default=func.now()),
            Column('prew_season', ForeignKey("seasons.season_id"))
        )
        self.rating = Table(
            'rating',
            self._metadata,
            Column(
                'rating_id',
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("player", ForeignKey("players.player_id")),
            Column("mmr", Integer),
            Column("season", ForeignKey("seasons.season_id")),
            Column("club", ForeignKey("clubs.name", name='fk_clubname_for_rating'), nullable=False)
        )
        self.clubs = Table(
            'clubs',
            self._metadata,
            Column(
                'name',
                String,
                unique=True,
                nullable=False
            )
        )


def _configure_mappings(metadata):
    meta = DatabaseSchema()
    meta.configure(metadata)

    mapper(model.Player, meta.players)

    mapper(model.Game, meta.games)
    mapper(model.House, meta.houses)
    mapper(model.BestMove, meta.best_moves)
    mapper(model.SheriffVersion, meta.sheriff_versions)
    mapper(model.Disqualified, meta.disqualifieds)
    mapper(model.Voted, meta.votes)
    mapper(model.NominatedForBest, meta.nominated_for_best)
    mapper(model.HandOfMafia, meta.hand_of_mafia)
    mapper(model.Kills, meta.kills)
    mapper(model.Misses, meta.misses)
    mapper(model.DonChecks, meta.don_checks)
    mapper(model.SheriffChecks, meta.sheriff_checks)
    mapper(model.BonusTolerantFromPlayers, meta.bonuses_tolerant)
    mapper(model.BonusFromPlayers, meta.bonuses_from_players)
    mapper(model.Devise, meta.devises)
    mapper(model.BonusHeading, meta.bonuses_from_heading)
    mapper(model.Break, meta.breaks)

    mapper(model.Season, meta.season)
    mapper(model.Rating, meta.rating)

    return metadata


class SqlAlchemy:
    def __init__(self, db_engine):
        self.db_engine = db_engine
        self._session_maker = scoped_session(sessionmaker(self.db_engine, expire_on_commit=False))

    def unit_of_work_manager(self):
        return SqlAlchemyUnitOfWorkManager(self._session_maker)

    def configure_mappings(self):
        metadata = MetaData(self.db_engine)
        return _configure_mappings(metadata)

    def session(self):
        return SqlAlchemySessionContext(self._session_maker)


class SqlAlchemySessionContext:
    def __init__(self, session_maker):
        self._session_maker = session_maker

    def __enter__(self):
        self._session = self._session_maker()

    def __exit__(self, type, value, traceback):
        self._session_maker.remove()


def make_sqlalchemy(url):
    postgres_engine = create_engine(url)
    return SqlAlchemy(postgres_engine)
