from collections import defaultdict
from typing import Optional


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from zlo.domain.mmr_calculators.constants import BONUS_FOR_BEST_PLAYER


class BestPlayerRule(BaseRuleMMR):

    bonus_mmr = BONUS_FOR_BEST_PLAYER

    def calculate_mmr(self, rating: Optional[Rating] = None):
        result = defaultdict(int)

        for house in self.game_info.houses:
            bonuses_for_house = [bonus for bonus in self.game_info.bonuses_from_players
                                 if bonus.bonus_to == house.house_id]
            if len(bonuses_for_house) >= 3:
                result[house.player_id] += self.bonus_mmr

        return result
