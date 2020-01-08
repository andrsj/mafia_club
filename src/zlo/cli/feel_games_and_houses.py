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
from zlo.domain.model import Game, House, BestMove
from zlo.domain.types import GameResult, ClassicRole
from dateutil import parser
import argparse


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


def parse_best_moves(work_sheet):
    best_move_data = {
        "killed_player": None,
        "best_1": None,
        "best_2": None,
        "best_3": None
    }
    killed_player = work_sheet.cell(20, 4).value
    if killed_player not in [str(i) for i in range(1, 11)]:
        return best_move_data
    else:
        best_move_data["killed_player"] = killed_player
    return


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


def save_game(game_data):
    uowm = inject.instance(UnitOfWorkManager)

    with uowm.start() as tx:
        # Create ot update game
        player = tx.players.get_by_nickname(game_data["heading"])
        game_data["heading"] = player.player_id
        game = tx.games.get_by_id(game_data["game_id"])
        if game is None:
            game = Game(**game_data)
            tx.games.add(game)
        else:
            game.tournament = game_data["tournament"]
            game.heading = game_data["heading"]
            game.date = game_data["date"]
            game.club = game_data["club"]
            game.result = game_data["result"]
        tx.commit()


def save_best_move(game_id, best_move_data):
    uowm = inject.instance(UnitOfWorkManager)
    with uowm.start() as tx:
        best_move = tx.best_moves.get_by_game_id(game_id)
        if best_move:
            best_move.killed = best_move_data["killed"]
            best_move.best_1 = best_move_data["best_1"]
            best_move.best_2 = best_move_data["best_2"]
            best_move.best_3 = best_move_data["best_3"]
        else:
            best_move = BestMove(
                best_move_id=str(uuid.uuid4()),
                game_id=game_id,
                killed_house=best_move_data["killed_house"],
                best_1=best_move_data["best_1"],
                best_2=best_move_data["best_2"],
                best_3=best_move_data["best_3"]
            )
        tx.best_moves.add(best_move)


@inject.params(
    uowm=UnitOfWorkManager
)
def save_houses(uowm, game_id, houses_datas: List[dict]):
    with uowm.start() as tx:
        for house_data in houses_datas:
            player = tx.players.get_by_nickname(house_data["nickname"])
            if not player:
                raise UnknownPlayer(f"Could not find acc for this nickname {house_data['nickname']}")
            house = tx.houses.get_by_game_id_and_player_id(game_id, player.player_id)
            if house:
                house.bonus_mark = house_data["bonus_mark"]
                house.slot = house_data["slot"]
                house.fouls = house_data["fouls"]
                house.role = house_data["role"].value
            else:
                house = House(
                    house_id=str(uuid.uuid4()),
                    game_id=game_id,
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

    my_parser = argparse.ArgumentParser(description='Parse data from spreadsheet and fill tables')
    my_parser.add_argument('spreadsheet_title',
                           metavar='spreadsheet_title',
                           type=str,
                           help='')
    my_parser.add_argument('--games',
                           default=False,
                           type=bool,
                           help="Parse and update game info"
                           )
    my_parser.add_argument('--houses',
                           default=False,
                           type=bool,
                           help="Parse and update houses info; Slot number. PLayer nick fouls and bonus marks"
                           )
    my_parser.add_argument("--best_moves",
                           default=False,
                           type=bool,
                           help="Parse and update best moves"
                           )

    args = my_parser.parse_args()

    cfg = os.environ.copy()
    bootstrap(cfg)

    client = auth()
    sheet = client.open('20/09/2019')

    for work_sheet in sheet.worksheets():
        game_data = parse_game(work_sheet)
        if args.games:
            save_game(game_data)
        try:
            if args.houses:
                houses = parse_houses_from_sheet(work_sheet)
                save_houses(game_id=game_data["game_id"], houses_datas=houses)
        except UnknownPlayer as e:
            logging.error(f"Could not save game {game_data} player unknown player; {e}")
            continue
        except Exception as e:
                logging.error(f"Some shit happens; Take care of that game -> {game_data}")
                raise e
        if args.best_moves:
            best_moves = parse_best_moves(work_sheet)
        print("Successfully create game ", game_data)
        time.sleep(20)