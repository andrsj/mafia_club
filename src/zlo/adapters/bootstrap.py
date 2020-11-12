from functools import partial

import inject
import zlo.domain.infrastructure as ports
from zlo import config
from zlo.adapters import orm
from zlo.adapters.infrastructure import MessageBus
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.config import map_handlers
from zlo.tests.fakes import FakeHouseCacheMemory


def bootstrap(env):
    binder_config = partial(configure_binder, env)
    inject.configure(binder_config)


def configure_binder(env, binder):

    postgres_url = config.get_postgres_url(env)
    dal = orm.make_sqlalchemy(postgres_url)

    dal.configure_mappings()
    binder.bind(ports.UnitOfWorkManager, dal.unit_of_work_manager())
    binder.bind(ports.HouseCacheMemory, FakeHouseCacheMemory())
    binder.bind("orm", dal)

    client = SpreadSheetClient()
    binder.bind(SpreadSheetClient, client)

    bus = MessageBus()
    map_handlers(bus)

    binder.bind(MessageBus, bus)
