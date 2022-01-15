from typing import Optional
from collections import defaultdict


from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.mmr_calculators.constants import CORRELATION_FOR_DISQUALIFIELD_PLAYER
from dim_mafii.domain.utils import get_house_from_list_by_house_id


class DisqualifieldRule(BaseRuleMMR):

    correlation_mmr = CORRELATION_FOR_DISQUALIFIELD_PLAYER

    def calculate_mmr(self, rating: Optional[Rating] = None):
        result = defaultdict(int)

        for disqualified in self.game_info.disqualifieds:
            house = get_house_from_list_by_house_id(self.game_info.houses, disqualified.house)
            result[house.player_id] += self.correlation_mmr

        return result
