import datetime
from typing import Dict, Type

import inject
from zlo.adapters.orm import SqlAlchemyUnitOfWork
from zlo.domain.infrastructure import UnitOfWorkManager, UnitOfWork
from zlo.domain.model import Game, Player
from zlo.domain.types import check_winner


@inject.params(
    uowm=UnitOfWorkManager,
)
def generate_statistic_by_date(uowm, start_date: datetime.datetime, end_date: datetime.datetime) -> \
        Dict[str, float]:
    """
    Get all games in this range
    Get result for each game
    Get Slots for each game
    For each Slot get player
    Add player to result or update existing number of marks
    Add bonus marks to the player based on slot

    """
    result = {}
    with uowm.start() as tx:
        games = tx.games.get_by_datetime_range(start_date, end_date)
        for game in games:
            game_stats = generate_statistic_for_game(tx, game)
            for player_nick, mark in game_stats.items():
                if player_nick in result:
                    result[player_nick] += mark
                else:
                    result[player_nick] = mark
    return result


def generate_statistic_for_game(uow: SqlAlchemyUnitOfWork, game: Game):
    result = {}
    houses = uow.houses.get_by_game_id(game.id)
    for house in houses:
        player: Player = uow.players.get_by_id(house.player_id)
        if check_winner(game.result, house.role):
            result[player.nickname] = 1 + house.bonus_mark
        else:
            result[player.nickname] = house.bonus_mark
    return result
