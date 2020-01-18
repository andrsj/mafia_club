import datetime
import os

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.statistic import generate_statistic_by_date, generate_statistic_for_game
from pprint import pprint

if __name__ == "__main__":

    cfg = os.environ.copy()
    bootstrap(cfg)

    start_date = datetime.datetime.today() - datetime.timedelta(days=300)
    end_date = datetime.datetime.today() + datetime.timedelta(days=300)

    uowm = inject.instance(UnitOfWorkManager)

    result = generate_statistic_by_date(uowm, start_date, end_date)
    for player_nick, player_result in result.items():
        player_result.calculate_win_rate()

    players_results = list(result.values())
    players_results = sorted(players_results, key=lambda x: x.games_number, reverse=True)

    for player_result in players_results:
        # if player_result.nickname == "Ред":
        #     print("egc")
        print(player_result.get_repr_of_stats())



