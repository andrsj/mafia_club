from collections import defaultdict


from zlo.domain import mmr_calculators as mmr
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.game_info_builder import GameInfoBuilder
from zlo.domain.model import Game


class GameMMRCalculator:
    rules = [
        mmr.BestMoveRule,
        mmr.MissRule,
        mmr.SheriffVersionRule,
        mmr.ThreeVotedRule
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

    def calculate_mmr(self, game: Game):
        delta_rating = defaultdict(int)

        game_info = self.get_game_info(game)

        for rule in self.rules:
            delta_by_one_rule = rule(game_info).calculate_mmr()

            for uuid in delta_by_one_rule:
                delta_rating[uuid] += delta_by_one_rule[uuid]

        return delta_rating
