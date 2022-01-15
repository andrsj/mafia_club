from typing import List, Optional
from collections import defaultdict

from dim_mafii.domain.model import House
from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.mmr_calculators.constants import BONUS_FOR_PLAYING_LIKE_SHERIFF
from dim_mafii.domain.utils import is_mafia_win, is_mafia


class SheriffVersionRule(BaseRuleMMR):

    bonus_mmr = BONUS_FOR_PLAYING_LIKE_SHERIFF

    def calculate_mmr(self, rating: Optional[Rating] = None):
        if not is_mafia_win(self.game_info.game):
            return {}

        if not self.game_info.sheriff_versions:
            return {}

        result = defaultdict(int)

        # Get all mafias
        black_houses: List[House] = [house for house in self.game_info.houses if is_mafia(house)]

        for house in black_houses:
            # Check if mafia house was in sheriff version
            if house.house_id in [version.house for version in self.game_info.sheriff_versions]:
                result[house.player_id] += self.bonus_mmr

        return result
