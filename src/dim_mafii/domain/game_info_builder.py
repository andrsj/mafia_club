from copy import deepcopy
from typing import List


from dim_mafii.domain import model


class GameInfoBuilder:
    GAME = model.GameInfo()

    def __init__(self):
        self.game_info: model.GameInfo = deepcopy(GameInfoBuilder.GAME)

    def build(self):
        return self.game_info

    def with_game(self, game: model.Game):
        self.game_info.game = game
        return self

    def with_kills(self, kills: List[model.Kills]):
        self.game_info.kills = kills
        return self

    def with_votes(self, votes: List[model.Voted]):
        self.game_info.votes = votes
        return self

    def with_houses(self, houses: List[model.House]):
        self.game_info.houses = houses
        return self

    def with_breaks(self, breaks: List[model.Break]):
        self.game_info.breaks = breaks
        return self

    def with_misses(self, misses: List[model.Misses]):
        self.game_info.misses = misses
        return self

    def with_devises(self, devises: List[model.Devise]):
        self.game_info.devises = devises
        return self

    def with_don_checks(self, don_checks: List[model.DonChecks]):
        self.game_info.don_checks = don_checks
        return self

    def with_best_move(self, best_move: model.BestMove):
        self.game_info.best_move = best_move
        return self

    def with_disqualifieds(self, disqualifieds: List[model.Disqualified]):
        self.game_info.disqualifieds = disqualifieds
        return self

    def with_sheriff_checks(self, sheriff_checks: List[model.SheriffChecks]):
        self.game_info.sheriff_checks = sheriff_checks
        return self

    def with_hand_of_mafia(self, hand_of_mafia: model.HandOfMafia):
        self.game_info.hand_of_mafia = hand_of_mafia
        return self

    def with_sheriff_versions(self, sheriff_versions: List[model.SheriffVersion]):
        self.game_info.sheriff_versions = sheriff_versions
        return self

    def with_nominated_for_best(self, nominated_for_best: List[model.NominatedForBest]):
        self.game_info.nominated_for_best = nominated_for_best
        return self

    def with_bonuses_from_player(self, bonuses: List[model.BonusFromPlayers]):
        self.game_info.bonuses_from_players = bonuses
        return self

    def with_bonuses_from_heading(self, bonuses: List[model.BonusHeading]):
        self.game_info.bonuses_from_heading = bonuses
        return self

    def with_bonuses_for_tolerant(self, bonuses: List[model.BonusTolerantFromPlayers]):
        self.game_info.bonuses_for_tolerant = bonuses
        return self
