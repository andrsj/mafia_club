from collections import defaultdict


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain import types
from zlo.domain.mmr_calculators.constants import BONUS_FOR_SHERIFF_PLAY


class SheriffPlayRule(BaseRuleMMR):

    bonus_mmr = BONUS_FOR_SHERIFF_PLAY

    def calculate_mmr(self):
        if self.game_info.game.result != types.GameResult.citizen.value:
            return {}

        result = defaultdict(int)

        sheriff = [house for house in self.game_info.houses if house.role == types.ClassicRole.sheriff.value].pop()
        result[sheriff.player_id] += self.bonus_mmr

        return result
