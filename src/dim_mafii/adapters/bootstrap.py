from functools import partial

import inject
import dim_mafii.domain.infrastructure as ports
from dim_mafii import config
from dim_mafii.adapters import orm
from dim_mafii.adapters.infrastructure import MessageBus
from dim_mafii.sheet_parser.client import SpreadSheetClient
from dim_mafii.domain.config import map_handlers
from dim_mafii.tests.fakes import FakeHouseCacheMemory


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
