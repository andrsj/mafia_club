from typing import List, Optional
from collections import defaultdict


from dim_mafii.domain import model
from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.utils import is_mafia_win, is_mafia
from dim_mafii.domain.mmr_calculators.constants import CORRELATION_FOR_MISS_FROM_MAFIA


class MissRule(BaseRuleMMR):

    correlation_mmr = CORRELATION_FOR_MISS_FROM_MAFIA

    def calculate_mmr(self, rating: Optional[Rating] = None):
        if is_mafia_win(self.game_info.game):
            return {}

        if not self.game_info.misses:
            return {}

        result = defaultdict(int)

        black_houses: List[model.House] = [house for house in self.game_info.houses if is_mafia(house)]

        for house in black_houses:
            result[house.player_id] += self.correlation_mmr

        return result
