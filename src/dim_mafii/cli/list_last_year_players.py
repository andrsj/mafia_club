import os
import argparse
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta

import inject
from gspread.models import Cell

from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.sheet_parser.client import SpreadSheetClient
from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.domain import model
from dim_mafii.domain.config import DATE_FORMAT

from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database


if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    uowm = inject.instance(UnitOfWorkManager)
    client = inject.instance(SpreadSheetClient)

    parser = argparse.ArgumentParser(description='Generate spreadsheets for new game in date range')

    parser.add_argument(
        '--day',
        dest='start_date_of_day',
        help='Start date (format: DD/MM/YYYY)'
    )

    arguments = parser.parse_args()
    day = datetime.strptime(arguments.start_date_of_day, DATE_FORMAT)

    with uowm.start() as tx:
        players: List[model.Player] = tx.players.all()

        players_date_dict = {player.nickname: None for player in players}

        games: List[model.Game] = sorted(tx.games.get_by_datetime_range(
            day - relativedelta(years=1), day
        ), key=lambda g: g.date)
        houses: List[model.House] = tx.houses.get_all_houses()

        for game in games:
            houses_per_game = [h for h in houses if h.game_id == game.game_id]
            for house in houses_per_game:
                player = [p for p in players if p.player_id == house.player_id][0]
                if players_date_dict[player.nickname] is None or players_date_dict[player.nickname] < game.date:
                    players_date_dict[player.nickname] = game.date

    sheet = client.client.open_by_key('1gTW1-KIYN_xGAFUa8oFEuO616NGyTyn6dNGDRwi1PfE')
    worksheet = sheet.sheet1

    cells = [
        Cell(
            row=1,
            col=1,
            value='Nicknames',
        ),
        Cell(
            row=1,
            col=2,
            value='Last game'
        )
    ]
    for i, info in enumerate(
        ((nickname, date) for nickname, date in players_date_dict.items() if date), start=2
    ):
        cells.append(
            Cell(
                row=i,
                col=1,
                value=info[0].capitalize(),
            )
        )
        cells.append(
            Cell(
                row=i,
                col=2,
                value=info[1].strftime(DATE_FORMAT),
            )
        )

    worksheet.update_cells(cells)

    print(sheet.url)
