from uuid import UUID
from typing import Dict
from datetime import datetime
from collections import defaultdict


import inject


from dim_mafii.domain import mmr_calculators as mmr
from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.domain.game_info_builder import GameInfoBuilder
from dim_mafii.domain.model import Game


class GameMMRCalculator:
    rules = [
        mmr.GameWinnerRule,  # First RULE!
        mmr.MissRule,
        mmr.DeviseRule,
        mmr.BestMoveRule,
        mmr.ThreeVotedRule,
        mmr.WrongBreakRule,
        mmr.BestPlayerRule,
        mmr.HandOfMafiaRule,
        mmr.SheriffPlayRule,
        mmr.DisqualifieldRule,
        mmr.SheriffVersionRule,
        mmr.BonusFromHeadingRule,
    ]

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def get_game_info(self, game: Game):
        with self.uowm.start() as tx:

            return GameInfoBuilder().\
                with_game(game=game).\
                with_houses(houses=tx.houses.get_by_game_id(game.game_id)).\
                with_kills(kills=tx.kills.get_by_game_id(game.game_id)).\
                with_votes(votes=tx.voted.get_by_game_id(game.game_id)).\
                with_breaks(breaks=tx.breaks.get_by_game_id(game.game_id)).\
                with_misses(misses=tx.misses.get_by_game_id(game.game_id)).\
                with_devises(devises=tx.devises.get_by_game_id(game.game_id)).\
                with_don_checks(don_checks=tx.don_checks.get_by_game_id(game.game_id)).\
                with_best_move(best_move=tx.best_moves.get_by_game_id(game.game_id)).\
                with_disqualifieds(disqualifieds=tx.disqualifieds.get_by_game_id(game.game_id)).\
                with_sheriff_checks(sheriff_checks=tx.sheriff_checks.get_by_game_id(game.game_id)).\
                with_hand_of_mafia(hand_of_mafia=tx.hand_of_mafia.get_by_game_id(game.game_id)).\
                with_sheriff_versions(sheriff_versions=tx.sheriff_versions.get_by_game_id(game.game_id)).\
                with_nominated_for_best(nominated_for_best=tx.nominated_for_best.get_by_game_id(game.game_id)).\
                with_bonuses_from_player(bonuses=tx.bonuses_from_players.get_by_game_id(game.game_id)).\
                with_bonuses_from_heading(bonuses=tx.bonuses_from_heading.get_by_game_id(game.game_id)).\
                with_bonuses_for_tolerant(bonuses=tx.bonuses_tolerant.get_by_game_id(game.game_id)).\
                build()

    def calculate_mmr(self, game: Game, rating: Dict[UUID, int]):
        delta_rating = defaultdict(int)

        game_info = self.get_game_info(game)

        for rule in self.rules:
            delta_by_one_rule = rule(game_info).calculate_mmr(rating)

            for uuid in delta_by_one_rule:
                delta_rating[uuid] += delta_by_one_rule[uuid]

        return delta_rating


@inject.params(
    uowm=UnitOfWorkManager
)
def get_mmr(uowm: UnitOfWorkManager, start_date: datetime, end_date: datetime, club_name: str):
    with uowm.start() as tx:
        players = tx.players.all()
        games = tx.games.get_by_datetime_range(start_date=start_date, end_date=end_date)
        houses = tx.houses.get_all_houses()

    mmr = 1500 if club_name == '?????? ??????????' else 1000
    houses = [house for house in houses if house.game_id in (game.game_id for game in games)]
    players = [player for player in players if player.player_id in (house.player_id for house in houses)]
    final_result: Dict[UUID, int] = {player.player_id: mmr for player in players}
    detail_rating = defaultdict(list)

    gameMMRcalculator = GameMMRCalculator(uowm=uowm)
    for game in filter(lambda g: g.club == club_name, games):

        delta_rating = gameMMRcalculator.calculate_mmr(game, final_result)

        for uuid in delta_rating:
            detail_rating[uuid].append(delta_rating[uuid])
            final_result[uuid] += delta_rating[uuid]

    return final_result, detail_rating