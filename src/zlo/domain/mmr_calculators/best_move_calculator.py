from collections import defaultdict


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain import types
from zlo.domain.mmr_calculators.constants import (
    BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE,
    BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE
)


class BestMoveRule(BaseRuleMMR):

    bonus_mmr_2 = BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE
    bonus_mmr_3 = BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE

    def calculate_mmr(self):
        result = defaultdict(int)

        if self.game_info.best_move:
            houses_from_best_move = [
                house for house in self.game_info.houses
                if house.house_id in (
                    self.game_info.best_move.best_1,
                    self.game_info.best_move.best_2,
                    self.game_info.best_move.best_3,
                )
            ]

            best_house = next(
                house for house in self.game_info.houses
                if house.house_id == self.game_info.best_move.killed_house
            )
            if len([
                house for house in houses_from_best_move
                if house.role in (types.ClassicRole.don.value, types.ClassicRole.mafia.value)
            ]) == 2:
                result[best_house.player_id] += self.bonus_mmr_2

            if len([
                house for house in houses_from_best_move
                if house.role in (types.ClassicRole.don.value, types.ClassicRole.mafia.value)
            ]) == 3:
                result[best_house.player_id] += self.bonus_mmr_3

        return result
