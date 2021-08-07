from collections import defaultdict
from typing import Optional


from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.utils import is_citizen_win, is_sheriff
from dim_mafii.domain.mmr_calculators.constants import BONUS_FOR_SHERIFF_PLAY


class SheriffPlayRule(BaseRuleMMR):

    bonus_mmr = BONUS_FOR_SHERIFF_PLAY

    def calculate_mmr(self, rating: Optional[Rating] = None):
        if not is_citizen_win(self.game_info.game):
            return {}

        result = defaultdict(int)

        if not any(map(is_sheriff, self.game_info.houses)):
            print('Strange game', self.game_info.game.game_id)
            return {}

        [sheriff] = [house for house in self.game_info.houses if is_sheriff(house)]
        result[sheriff.player_id] += self.bonus_mmr

        return result
