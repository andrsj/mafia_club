from typing import List
from collections import defaultdict


from zlo.domain import model
from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain import types
from zlo.domain.mmr_calculators.constants import BONUS_FOR_MISS_FROM_MAFIA


class MissRule(BaseRuleMMR):

    bonus_mmr = BONUS_FOR_MISS_FROM_MAFIA

    def calculate_mmr(self):
        if self.game_info.game.result == types.GameResult.mafia.value:
            return {}

        if not self.game_info.misses:
            return {}

        result = defaultdict(int)

        black_houses: List[model.House] = [
            house for house in self.game_info.houses
            if house.role in (types.ClassicRole.mafia.value, types.ClassicRole.don.value)
        ]

        for house in black_houses:
            result[house.player_id] += self.bonus_mmr

        return result
