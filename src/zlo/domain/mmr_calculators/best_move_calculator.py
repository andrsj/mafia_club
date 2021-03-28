from collections import defaultdict
from typing import Optional


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from zlo.domain.utils import get_houses_from_list_of_house_ids, get_house_from_list_by_house_id, is_mafia
from zlo.domain.mmr_calculators.constants import (
    BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE,
    BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE
)


class BestMoveRule(BaseRuleMMR):

    bonus_mmr_2 = BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE
    bonus_mmr_3 = BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE

    def calculate_mmr(self, rating: Optional[Rating] = None):

        if not self.game_info.best_move:
            return {}

        result = defaultdict(int)

        houses_from_best_move = get_houses_from_list_of_house_ids(
            self.game_info.houses, self.game_info.best_move.choosen_houses)

        first_killed_house = get_house_from_list_by_house_id(
            self.game_info.houses, self.game_info.best_move.killed_house)

        if len([house for house in houses_from_best_move if is_mafia(house)]) == 2:
            result[first_killed_house.player_id] += self.bonus_mmr_2

        if len([house for house in houses_from_best_move if is_mafia(house)]) == 3:
            result[first_killed_house.player_id] += self.bonus_mmr_3

        return result
