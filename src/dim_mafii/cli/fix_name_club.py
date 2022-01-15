import os
from typing import List

import inject

from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.domain.model import Game

from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database


if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    uowm = inject.instance(UnitOfWorkManager)

    with uowm.start() as tx:
        games: List[Game] = tx.games.get_all_games()

        for game in games:
            if game.date.weekday() == 1:  # Tuesday
                game.club = 'Школа Зло'
            elif game.date.weekday() == 4:  # Friday
                game.club = 'ZLO'

        tx.commit()
