import logging
import os
import time
import uuid
from typing import List

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.cli.auth import auth
from zlo.cli.exceptions import UnknownPlayer
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Game, House
from zlo.domain.types import GameResult, ClassicRole
from dateutil import parser


def parse_game(work_sheet):
    if work_sheet.cell(4, 4).value:
        game_result = GameResult.mafia
    elif work_sheet.cell(5, 4).value:
        game_result = GameResult.citizen
    else:
        game_result = GameResult.unfinished

    game_result = game_result.value

    heading_nickname = work_sheet.cell(4, 11).value
    table = work_sheet.cell(5, 13).value
    date = parser.parse(work_sheet.cell(2, 17).value)
    club = "ZLO" if work_sheet.cell(4, 22).value else "ZLO_CORPORATION"
    tournament = work_sheet.cell(5, 26).value
    game_id = work_sheet.cell(27, 4).value
    if not game_id:
        game_id = str(uuid.uuid4())
        work_sheet.update_cell(27, 4, game_id)
    game_data = {
        "date": date,
        "heading": heading_nickname,
        "table": table,
        "club": club,
        "tournament": tournament,
        "game_id": game_id,
        "result": game_result
    }
    return game_data


def parse_worksheet_for_game_data(work_sheet):
    game = parse_game(work_sheet)
    return game


def get_role(role_short_name: str) -> ClassicRole:
    role_short_name = role_short_name.strip().upper()
    if role_short_name == "Д":
        role = ClassicRole.don
    elif role_short_name == "М":
        role = ClassicRole.mafia
    elif role_short_name == "Ш":
        role = ClassicRole.sheriff
    else:
        role = ClassicRole.citizen
    return role


@inject.params(
    uowm=UnitOfWorkManager
)
def save_game_and_house(uowm, game_data: dict, houses_datas: List[dict]):

    with uowm.start() as tx:
        # Create ot update game
        player = tx.players.get_by_nickname(game_data["heading"])
        game_data["heading"] = player.player_id
        game = tx.games.get_by_id(game_data["game_id"])
        if game is None:
            game = Game(**game_data)
        else:
            game.tournament = game_data["tournament"]
            game.heading = game_data["heading"]
            game.date = game_data["date"]
            game.club = game_data["club"]
            game.result = game_data["result"]

        tx.games.add(game)
        tx.commit()

        for house_data in houses_datas:
            player = tx.players.get_by_nickname(house_data["nickname"])
            if not player:
                raise UnknownPlayer(f"Could not find acc for this nickname {house_data['nickname']}")
            house = tx.houses.get_by_game_id_and_player_id(game.game_id, player.player_id)
            if house:
                house.bonus_mark = house_data["bonus_mark"]
                house.slot = house_data["slot"]
                house.fouls = house_data["fouls"]
                house.role = house_data["role"].value
            else:
                house = House(
                    house_id=str(uuid.uuid4()),
                    game_id=game.game_id,
                    player_id=player.player_id,
                    slot=house_data["slot"],
                    fouls=house_data["fouls"],
                    role=house_data["role"].value,
                    bonus_mark=house_data["bonus_mark"],
                )
            tx.houses.add(house)
        tx.commit()


def parse_houses_from_sheet(work_sheet):
    houses = []
    for i in range(1, 11):
        house_row = [c.value for c in work_sheet.range("B{row}:L{row}".format(row=i + 7))]
        houses.append({
            "role": get_role(house_row[6]),
            "nickname": house_row[1],
            "slot": int(house_row[0]),
            "fouls": sum([bool(f) for f in house_row[2:5]]),
            "bonus_mark": float(house_row[9].replace(",", ".") or 0),
        })
    return houses


if __name__ == "__main__":

    cfg = os.environ.copy()
    bootstrap(cfg)

    client = auth()
    sheet = client.open('20/09/2019')

    results = []
    for work_sheet in sheet.worksheets():
        game_data = parse_game(work_sheet)
        houses = parse_houses_from_sheet(work_sheet)
        try:
            save_game_and_house(game_data=game_data, houses_datas=houses)
        except UnknownPlayer as e:
            logging.error(f"Could not save game {game_data} player unknown player; {e}")
            continue
        except Exception as e:
            logging.error(f"Some shit happens; Take care of that game -> {game_data}")
            raise e
        print("Successfully create game ", game_data)
        time.sleep(20)