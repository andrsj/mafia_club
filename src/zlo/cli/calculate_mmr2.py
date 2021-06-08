import os
from uuid import UUID
from typing import Dict
from datetime import datetime
from collections import defaultdict

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
        houses = tx.houses.get_all_houses()

    mmr = 1500 if clubname == 'ZLO' else 1000
    houses = [house for house in houses if house.game_id in (game.game_id for game in games)]
    players = [player for player in players if player.player_id in (house.player_id for house in houses)]
    final_result: Dict[UUID, int] = {player.player_id: mmr for player in players}
    detail_rating = defaultdict(list)

    gameMMRcalculator = GameMMRCalculator(uowm=uowm)
    for game in filter(lambda g: g.club == clubname, games):

        delta_rating = gameMMRcalculator.calculate_mmr(game, final_result)

        for uuid in delta_rating:
            detail_rating[uuid].append(delta_rating[uuid])
            final_result[uuid] += delta_rating[uuid]

    return final_result, detail_rating


if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    # parser = create_parser_for_date_range()
    # args = parser.parse_args()

    # start = datetime.strptime(args.start_date_of_day, DATA_FORMAT)
    start = datetime(2021, 1, 1)

    # end = datetime.strptime(args.end_date_of_day, DATA_FORMAT)
    end = datetime(2021, 5, 8)
    # 4.4.21
    # 8.5.21

    uowm = inject.instance(UnitOfWorkManager)
    with uowm.start() as tx:
        players = tx.players.all()

    rating, detail_rating = get_mmr(
        uowm,
        # start_date=datetime.strptime(args.start_date_of_day, DATA_FORMAT),
        start_date=start,
        # end_date=datetime.strptime(args.end_date_of_day, DATA_FORMAT),
        end_date=end,
        # clubname='ZLO'  # ZLO | Школа Зло
        clubname='Школа Зло'
    )

    rating = {next(filter(lambda p: p.player_id == i, players)).displayname: j
              for i, j in sorted(rating.items(), key=lambda x: x[1])}

    detail_rating = {next(filter(lambda p: p.player_id == i, players)).displayname: j
                     for i, j in detail_rating.items()}

    rating = {i: j for i, j in rating.items() if detail_rating.get(i)}

    for i, j in sorted(rating.items(), key=lambda x: x[1], reverse=True):
        print(i, j, len(detail_rating.get(i)))

    import csv
    with open('rating_school.csv', 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Nickname', 'MMR', 'Games'])
        writer.writeheader()
        for i, j in sorted(rating.items(), key=lambda x: x[1], reverse=True):
            writer.writerow({
                'Nickname': i.capitalize(),
                'MMR': j,
                'Games': len(detail_rating.get(i, []))
            })

    with open('rating_school-15.csv', 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Nickname', 'MMR', 'Games'])
        writer.writeheader()
        for i, j in sorted(rating.items(), key=lambda x: x[1], reverse=True):
            if len(detail_rating.get(i, [])) >= 15:
                writer.writerow({
                    'Nickname': i.capitalize(),
                    'MMR': j,
                    'Games': len(detail_rating.get(i, []))
                })
