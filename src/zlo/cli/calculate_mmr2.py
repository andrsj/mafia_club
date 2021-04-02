import os
from uuid import UUID
from typing import Dict
from datetime import datetime
from pprint import pprint

import inject

from zlo.domain.utils import create_parser_for_date_range
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.mmr_calculators.general_calculator import GameMMRCalculator
from zlo.adapters.bootstrap import bootstrap
from zlo.domain.config import DATE_FORMAT


from zlo.cli.setup_env_for_test import setup_env_with_test_database

@inject.params(
    uowm=UnitOfWorkManager
)
def get_mmr(uowm: UnitOfWorkManager, start_date: datetime, end_date: datetime, clubname: str):
    with uowm.start() as tx:
        players = tx.players.all()
        games = tx.games.get_by_datetime_range(start_date=start_date, end_date=end_date)

    mmr = 1500 if clubname == 'ZLO' else 1000
    final_result: Dict[UUID, int] = {player.player_id: mmr for player in players}

    gameMMRcalculator = GameMMRCalculator(uowm=uowm)
    for game in filter(lambda g: g.club == clubname, games):

        delta_rating = gameMMRcalculator.calculate_mmr(game, final_result)

        for uuid in delta_rating:
            final_result[uuid] += delta_rating[uuid]

    return final_result


if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    # parser = create_parser_for_date_range()
    # args = parser.parse_args()

    # start = datetime.strptime(args.start_date_of_day, DATA_FORMAT)
    start = datetime(2021, 1, 1)

    # end = datetime.strptime(args.end_date_of_day, DATA_FORMAT)
    end = datetime(2021, 1, 31)

    uowm = inject.instance(UnitOfWorkManager)
    rating = get_mmr(
        uowm,
        # start_date=datetime.strptime(args.start_date_of_day, DATA_FORMAT),
        start_date=start,
        # end_date=datetime.strptime(args.end_date_of_day, DATA_FORMAT),
        end_date=end,
        clubname='Школа Зло'  # ZLO | Школа Зло
    )

    for i, j in sorted(rating.items(), key=lambda x: x[1]):
        print(i, j)
