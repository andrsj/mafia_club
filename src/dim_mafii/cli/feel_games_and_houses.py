import logging
import os
import time
import uuid
from pprint import pprint
from typing import List

import inject
from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.sheet_parser.client import SpreadSheetClient
from dim_mafii.cli.exceptions import UnknownPlayer
from dim_mafii.cli.zlo_logger import get_logger
from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.domain.model import Game, House, BestMove
from dim_mafii.domain.types import GameResult, ClassicRole
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

    heading_nickname = work_sheet.cell(4, 11).value.strip()
    table = work_sheet.cell(5, 13).value
    date = work_sheet.cell(2, 17).value
    if not date:
        logging.warning(f"Not valid date in {work_sheet.id}")
    else:
        date = parser.parse(date)
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

    def is_value_player_number(value):
        return value is not None and value.strip() in [str(i) for i in range(1, 11)]

    best_move_data = {
        "killed_player": None,
        "best_1": None,
        "best_2": None,
        "best_3": None
    }
    killed_player = work_sheet.cell(20, 4).value
    best_move_1 = work_sheet.cell(20, 8).value
    best_move_2 = work_sheet.cell(20, 9).value
    best_move_3 = work_sheet.cell(20, 10).value

    if killed_player not in [str(i) for i in range(1, 11)]:
        return best_move_data
    else:
        best_move_data["killed_player"] = killed_player

    if is_value_player_number(best_move_1):
        best_move_data["best_1"] = best_move_1

    if is_value_player_number(best_move_2):
        best_move_data["best_2"] = best_move_2

    if is_value_player_number(best_move_3):
        best_move_data["best_3"] = best_move_3

    return best_move_data


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
            logger.info(f"Create new game {game_data}")
            game = Game(**game_data)
            tx.games.add(game)
        else:
            logger.info(f"Update existing game {game_data}")
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
        best_move_killed = tx.houses.get_by_game_id_and_slot(game_id, best_move_data["killed_player"])
        best_move_1_player = tx.houses.get_by_game_id_and_slot(game_id, best_move_data["best_1"])
        best_move_2_player = tx.houses.get_by_game_id_and_slot(game_id, best_move_data["best_2"])
        best_move_3_player = tx.houses.get_by_game_id_and_slot(game_id, best_move_data["best_3"])

        if best_move:
            best_move.killed = best_move_killed.house_id if best_move_killed is not None else None
            best_move.best_1 = best_move_1_player.house_id if best_move_1_player is not None else None
            best_move.best_2 = best_move_2_player.house_id if best_move_2_player is not None else None
            best_move.best_3 = best_move_3_player.house_id if best_move_3_player is not None else None
        else:
            best_move = BestMove(
                best_move_id=str(uuid.uuid4()),
                game_id=game_id,
                killed_house=best_move_killed.house_id if best_move_killed is not None else None,
                best_1=best_move_1_player.house_id if best_move_1_player is not None else None,
                best_2=best_move_2_player.house_id if best_move_2_player is not None else None,
                best_3=best_move_3_player.house_id if best_move_3_player is not None else None
            )
        tx.best_moves.add(best_move)
        tx.commit()


@inject.params(
    uowm=UnitOfWorkManager
)
def save_houses(uowm, game_id, houses_datas: List[dict]):
    with uowm.start() as tx:
        for house_data in houses_datas:
            player = tx.players.get_by_nickname(house_data["nickname"])
            if not player:
                logging.error(f"Could not find acc for this nickname {house_data['nickname']}")
                raise UnknownPlayer(f"Could not find acc for this nickname {house_data['nickname']}")
            house = tx.houses.get_by_game_id_and_player_id(game_id, player.player_id)
            if house:
                logger.info(f"Update existing house {house.house_id}; with values {house_data}")
                house.bonus_mark = house_data["bonus_mark"]
                house.slot = house_data["slot"]
                house.fouls = house_data["fouls"]
                house.role = house_data["role"].value
            else:
                logger.info(f"Create new house with data {house_data}")
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


def parse_sheet(sheet):
    for i, work_sheet in enumerate(sheet.worksheets(), start=1):
        if i <= 4:
            continue
        print(f" {i} Worksheet {work_sheet.title}")
        game_data = parse_game(work_sheet)
        time.sleep(10)
        if args.games:
            save_game(game_data)
        try:
            if args.houses:
                houses = parse_houses_from_sheet(work_sheet)
                save_houses(game_id=game_data["game_id"], houses_datas=houses)
        except UnknownPlayer as e:
            logger.error(f"Could not save game {game_data} player unknown player; {e}")
            raise UnknownPlayer
        except Exception as e:
                logger.error(f"Some shit happens; Take care of that game -> {game_data}")
                raise e
        if args.best_moves:
            best_moves = parse_best_moves(work_sheet)
            save_best_move(game_data["game_id"], best_moves)
        time.sleep(10)
    logger.info(f"Successfuly download {sheet_title}")

def parse_houses_from_sheet(work_sheet):
    houses = []
    for i in range(1, 11):
        house_row = [c.value for c in work_sheet.range("B{row}:L{row}".format(row=i + 7))]
        houses.append({
            "role": get_role(house_row[6]),
            "nickname": house_row[1].strip(),
            "slot": int(house_row[0]),
            "fouls": sum([bool(f) for f in house_row[2:5]]),
            "bonus_mark": float(house_row[9].replace(",", ".") or 0),
        })
    return houses


if __name__ == "__main__":

    my_parser = argparse.ArgumentParser(description='Parse data from spreadsheet and fill tables')
    my_parser.add_argument('--spreadsheet_title',
                           dest='spreadsheet_title',
                           action='store_true',
                           required=False,
                           help='')
    my_parser.add_argument('--games',
                           default=False,
                           dest='games',
                           action='store_true',
                           required=False,
                           help="Parse and update game info"
                           )
    my_parser.add_argument('--houses',
                           default=False,
                           dest='houses',
                           action='store_true',
                           required=False,
                           help="Parse and update houses info; Slot number. PLayer nick fouls and bonus marks"
                           )
    my_parser.add_argument("--best_moves", dest='best_moves', action='store_true', required=False, help="Parse and update best moves")

    args = my_parser.parse_args()

    cfg = os.environ.copy()
    bootstrap(cfg)

    client = SpreadSheetClient().client
    # time.sleep(40)
    sheets = [
        # '13/12/2019',
        # '14/08/2019',
        # '15/08/2019',
        # '15/10/2019',
        # '15/11/2019',
        # '16/08/2019',
        # '18/10/2019',
        # '19/11/2019',
        # '20/09/2019',
        # '20/12/2019',
        # '22/10/2019',
        # '22/11/2019',
        # '24.12.2019',
        # '25/10/2019',
        # '26/12/2019',
        # '27.12.2019',
        # '27/12/2019',
        # '29/11/2019',
        # '30/11/2019',
    ]
    for i, sheet_title in enumerate(sheets, start=1):
        print(f" {i} Sheet  {sheet_title}")
        sheet = client.open(sheet_title)
        logger = get_logger(sheet_title)
        parse_sheet(sheet)
        print(f" {i} Finish Sheet  {sheet_title}")

        time.sleep(15)

