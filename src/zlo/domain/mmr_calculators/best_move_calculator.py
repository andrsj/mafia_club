from uuid import UUID
from typing import Dict
from collections import defaultdict


from zlo.domain import model
from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain.mmr_calculators.constants import (
    BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE,
    BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE
)


class BestMoveRule(BaseRuleMMR):

    bonus_mmr_2 = BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE
    bonus_mmr_3 = BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE

    def get_additional_data(self, best_move: model.BestMove):
        self.best_move = best_move

    def calculate_mmr(self):
        result = defaultdict(int)

        if self.best_move:
            houses_from_best_move = [
                house for house in self.houses
                if house.house_id in (
                    self.best_move.best_1,
                    self.best_move.best_2,
                    self.best_move.best_3,
                )
            ]

            best_house = next(house for house in self.houses if house.house_id == self.best_move.killed_house)
            if len([house for house in houses_from_best_move if house.role in (1, 3)]) == 2:
                result[best_house.player_id] += self.bonus_mmr_2

            if len([house for house in houses_from_best_move if house.role in (1, 3)]) == 3:
                result[best_house.player_id] += self.bonus_mmr_3

        return result

    def get_mmr(self, best_move: model.BestMove) -> Dict[UUID, int]:
        self.get_additional_data(best_move)
        rating = self.calculate_mmr()
        return rating
