import uuid
from functools import partial

import inject

import src.zlo.domain.infrastructure as ports
from src.zlo import config
from src.zlo.adapters import orm
from zlo.domain.model import Player


def bootstrap(env):
    binder_config = partial(configure_binder, env)
    inject.configure(binder_config)


def configure_binder(env, binder):

    postgres_url = config.get_postgres_url(env)
    dal = orm.make_sqlalchemy(postgres_url)

    dal.configure_mappings()
    binder.bind(ports.UnitOfWorkManager, dal.unit_of_work_manager())
    binder.bind("orm", dal)
    uowm = dal.unit_of_work_manager()
    # debug code remove after fix bug
    with uowm.start() as tx:
        player = Player(nickname="Дюймовочка2", name="Dima", club="ZLO")
        tx.players.add(player)
        tx.commit()


