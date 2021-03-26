from collections import defaultdict


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain.mmr_calculators.constants import (
    HIGH_BONUS_FROM_HEADING,
    MIDDLE_BONUS_FROM_HEADING,
    LOW_BONUS_FROM_HEADING
)


class BonusFromHeadingRule(BaseRuleMMR):

    low_bonus_mmr = LOW_BONUS_FROM_HEADING
    middle_bonus_mmr = MIDDLE_BONUS_FROM_HEADING
    high_bonus_mmr = HIGH_BONUS_FROM_HEADING

    def calculate_mmr(self):
        result = defaultdict(int)

        for bonus in self.game_info.bonuses_from_heading:
            house = next(filter(lambda h: h.house_id == bonus.house_id, self.game_info.houses))
            if 0.1 <= bonus.value <= 0.2:
                result[house.player_id] += self.low_bonus_mmr
            elif 0.3 <= bonus.value <= 0.4:
                result[house.player_id] += self.middle_bonus_mmr
            elif bonus.value >= 0.5:
                result[house.player_id] += self.high_bonus_mmr

        return result
