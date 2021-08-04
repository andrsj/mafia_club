from collections import defaultdict
from typing import Optional


from dim_mafii.domain.utils import get_house_from_list_by_house_id
from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.mmr_calculators.constants import (
    HIGH_BONUS_FROM_HEADING,
    MIDDLE_BONUS_FROM_HEADING,
    LOW_BONUS_FROM_HEADING
)


class BonusFromHeadingRule(BaseRuleMMR):

    low_bonus_mmr = LOW_BONUS_FROM_HEADING
    middle_bonus_mmr = MIDDLE_BONUS_FROM_HEADING
    high_bonus_mmr = HIGH_BONUS_FROM_HEADING

    def calculate_mmr(self, rating: Optional[Rating] = None):
        result = defaultdict(int)

        for bonus in self.game_info.bonuses_from_heading:
            house = get_house_from_list_by_house_id(self.game_info.houses, bonus.house_id)
            if 0.1 <= bonus.value <= 0.2:
                result[house.player_id] += self.low_bonus_mmr
            elif 0.3 <= bonus.value <= 0.4:
                result[house.player_id] += self.middle_bonus_mmr
            elif bonus.value >= 0.5:
                result[house.player_id] += self.high_bonus_mmr

        return result
