import sqlalchemy
from sqlalchemy import (
    Table,
    Column,
    String,
    create_engine,
    MetaData,
    ForeignKey, Enum, Integer)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapper, scoped_session, sessionmaker

from src.adapters.unit_of_work import SqlAlchemyUnitOfWorkManager
from src.domain.model import Player
from src.domain.types import Role


class DatabaseSchema:

    def __init__(self):
        self._configured = False

    def create_all(self):
        assert self._configured
        self._metadata.create_all()

    def get_meta(self):
        return self._metadata

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
            Column("club", String(40))
        )

        self.positions = Table(
            "positions",
            self._metadata,
            Column(
                "position_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", String(50), nullable=False),
            Column("player_id", UUID(as_uuid=True), ForeignKey("players.id"), nullable=False),
            Column("role", Enum(Role), nullable=False),
            Column("position", Integer, nullable=False)
        )

        self.votes = Table(
            "votes",
            self._metadata,
            Column(
                "vote_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", String(50), nullable=False),
            Column("day", Integer, nullable=False, default=1),
            Column("revote", Integer, nullable=False, default=0),
            Column("source_pos", UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False),
            Column("target_pos", UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False)
        )

        self.votes_exposes = Table(
            "votes_exposes",
            self._metadata,
            Column(
                "vote_expose_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", String(50), nullable=False),
            Column("day", Integer, nullable=False, default=1),
            Column("revote", Integer, nullable=False, default=0),
            Column("source_pos", UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False),
            Column("target_pos", UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False)
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
            Column("game_id", String(50), nullable=False),
            Column("night", Integer, nullable=False, default=2),
            Column("target", UUID(as_uuid=True), ForeignKey("positions.id"))
        )

        self.don_checks = Table(
            "don_checks",
            self._metadata,
            Column(
                "vote_expose_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", String(50), nullable=False),
            Column("night", Integer, nullable=False, default=2),
            Column("target", UUID(as_uuid=True), ForeignKey("positions.id"))
        )

        self.shots = Table(
            "shots",
            self._metadata,
            Column(
                "shot_id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sqlalchemy.text("uuid_generate_v4()"),
            ),
            Column("game_id", String(50), nullable=False),
            Column("night", Integer, nullable=False, default=2),
            Column("shooter", UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False),
            Column("target", UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False)
        )


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
