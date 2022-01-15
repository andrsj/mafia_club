import datetime
from typing import Dict, Type, List

import inject
from dim_mafii.adapters.orm import SqlAlchemyUnitOfWork
from dim_mafii.domain.infrastructure import UnitOfWorkManager, UnitOfWork
from dim_mafii.domain.model import Game, Player, BestMove, House
from dim_mafii.domain.types import check_winner, ClassicRole, BonusForBestMove, PlayerResult


@inject.params(
    uowm=UnitOfWorkManager,
)
def generate_statistic_by_date(
        uowm,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        club=None,
        tournament=0

) -> \
        Dict[str, PlayerResult]:
    """
    Get all games in this range
    Get result for each game
    Get Slots for each game
    For each Slot get player
    Add player to result or update existing number of marks
    Add bonus marks to the player based on slot

    """
    result: Dict[str, PlayerResult] = {}
    with uowm.start() as tx:
        games = tx.games.get_by_datetime_range(start_date, end_date)
        for game in games:
            game_stats = generate_statistic_for_game(tx, game)
            for player_nick, player_result in game_stats.items():
                if player_nick in result:
                    result[player_nick].update_by_new_result(player_result)
                else:
                    result[player_nick] = player_result
    return result


def get_role_by_house_id(houses, house_id):
    for house in houses:
        if house.house_id == house_id:
            return ClassicRole(house.role)


def get_best_move_bonuses(houses: List[House], best_move: BestMove) -> dict:

    result = {
        "house_id": None,
        "bonus": 0
    }
    # Game does not have best move. Its okay
    if best_move is None:
        return result
    # Game has best move but killed player is empty.
    # Its still okay
    if best_move.killed_house is None:
        return result

    result["house_id"] = best_move.killed_house
    killed_role = get_role_by_house_id(houses, best_move.killed_house)
    if killed_role in [ClassicRole.mafia, ClassicRole.don]:
        return result

    mafia_number_in_best_move = 0
    for best_move_house_id in [best_move.best_1, best_move.best_2, best_move.best_3]:
        if best_move_house_id is None:
            continue
        if get_role_by_house_id(houses, best_move_house_id) in [ClassicRole.mafia, ClassicRole.don]:
            mafia_number_in_best_move += 1
    if mafia_number_in_best_move == 3:
        result["bonus"] = BonusForBestMove.full.value
    if mafia_number_in_best_move == 2:
        result["bonus"] = BonusForBestMove.half.value
    return result


def generate_statistic_for_game(uow: SqlAlchemyUnitOfWork, game: Game):
    result = {}
    houses = uow.houses.get_by_game_id(game.game_id)
    best_move = uow.best_moves.get_by_game_id(game.game_id)
    best_move_bonus = get_best_move_bonuses(houses, best_move)
    for house in houses:
        player: Player = uow.players.get_by_id(house.player_id)
        player_result = PlayerResult(
            nickname=player.nickname
        )
        if best_move_bonus["house_id"] is not None and best_move_bonus["house_id"] == house.house_id:
            if best_move_bonus["bonus"] > 0:
                player_result.best_moves_number += 1
                player_result.best_moves_marks += best_move_bonus["bonus"]

        if house.bonus_mark > 0:
            player_result.bonus_mark_number += 1
            player_result.bonus_marks += house.bonus_mark

        if check_winner(game.result, house.role):
            player_result.wins_count += 1
        result[player.nickname] = player_result
    return result
