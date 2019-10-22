import retrying
import sqlalchemy.exc
import sqlalchemy.orm

from src.adapters.repositories import PlayerRepository
from src.domain.infrastructure import UnitOfWork, UnitOfWorkManager


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
        # logging.warn("Retrying retryable error %s", exn)
        return True
    # logging.error("Can't retry %s error %s", type(exn), exn)
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


class SqlAlchemyUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self, session_maker):
        self.session_maker = session_maker

    def start(self):
        return SqlAlchemyUnitOfWork(self.session_maker)
