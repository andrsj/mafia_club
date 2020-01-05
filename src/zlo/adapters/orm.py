import retrying
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm.exc
from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData, DateTime, func, ForeignKey
from sqlalchemy.orm import mapper, scoped_session, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from zlo.domain.infrastructure import UnitOfWork, UnitOfWorkManager
from zlo.domain.model import Player, Game, House
from zlo.adapters.repositories import PlayerRepository, HouseRepository, GameRepository


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
        self.session = self.session_factory()
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
        return PlayerRepository(self.session)

    @property
    def houses(self):
        return HouseRepository(self.session)

    @property
    def games(self):
        return GameRepository(self.session)


class SqlAlchemyUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self, session_maker):
        self.session_maker = session_maker

    def start(self):
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
            Column("club", String(40)),
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
            Column("role", Integer)
        )


def _configure_mappings(metadata):
    meta = DatabaseSchema()
    meta.configure(metadata)

    mapper(Player, meta.players)

    mapper(Game, meta.games)
    mapper(House, meta.houses)

    return metadata


class SqlAlchemy:
    def __init__(self, db_engine):
        self.db_engine = db_engine
        self._session_maker = scoped_session(sessionmaker(self.db_engine))

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
