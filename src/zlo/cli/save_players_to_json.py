import json
import os

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.cli.setup_env_for_test import setup_env_with_test_database
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.tests import fixtures


if __name__ == "__main__":
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    uow = inject.instance(UnitOfWorkManager)

    with uow.start() as tx:
        players = tx.players.all()

    fixtures_path = os.path.dirname(fixtures.__file__)
    with open(os.path.join(fixtures_path, "players.json"), 'w') as f:
        json.dump([player.as_dict() for player in players], f, indent=4)
