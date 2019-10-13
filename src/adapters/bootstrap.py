from functools import partial

import inject
import src.domain.infrastructure as ports
from src import config
from src.adapters import orm


def bootstrap(env):
    binder_config = partial(configure_binder, env)
    inject.configure(binder_config)


def configure_binder(env, binder):

    postgres_url = config.get_postgres_url(env)
    dal = orm.make_sqlalchemy(postgres_url)

    dal.configure_mappings()
    binder.bind(ports.UnitOfWorkManager, dal.unit_of_work_manager())
    binder.bind("orm", dal)


