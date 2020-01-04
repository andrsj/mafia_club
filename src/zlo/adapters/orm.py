import retrying
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm.exc
from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData
from sqlalchemy.orm import mapper, scoped_session, sessionmaker

from src.zlo.domain.infrastructure import UnitOfWork, UnitOfWorkManager
from src.zlo.domain.model import Player, Game, House


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


class PlayerRepository:

    def __init__(self, session):
        self._session = session

    def get_default_player(self):
        return Player("Lutik", "Denis", "Zlo")

    def get_by_nickname(self, nick):
        return self._session.query(Player).filter_by(nickname=nick).first()

    def get_by_id(self, player_id):
        return self._session.query(Player).filter_by(id=player_id).first()

    def add(self, player):
        self._session.add(player)


class GameRepository:

    def __init__(self, session):
        self._session = session

    def get_by_id(self, game_id):
        return self._session.query(Game).filter_by(id=game_id).first()

    def add(self, player):
        self._session.add(player)


class HouseRepository:

    def __init__(self, session):
        self._session = session

    def get_by_id(self, slot_id):
        return self._session.query(House).filter_by(id=slot_id).first()

    def get_by_game_id(self, game_id):
        return self._session.query(House).filter_by(game_id=game_id).all()

    def add(self, slot):
        self._session.add(slot)


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
            Column("id", Integer, primary_key=True),
            Column("nickname", String(40), unique=True),
            Column("name", String(40)),
            Column("club", String(40)),
        )

        # self.checks = Table(
        #     "cheks",
        #     self._metadata,
        #     Column("id", Integer, primary_key=True)
        # )


def _configure_mappings(metadata):
    meta = DatabaseSchema()
    meta.configure(metadata)

    mapper(Player, meta.players)

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
