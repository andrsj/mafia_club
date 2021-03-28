from collections import defaultdict
from typing import Optional


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from zlo.domain.utils import is_mafia_win, get_house_from_list_by_house_id
from zlo.domain.mmr_calculators.constants import CORRELATION_FOR_BEING_HAND_OF_MAFIA


class HandOfMafiaRule(BaseRuleMMR):

    correlation_mmr = CORRELATION_FOR_BEING_HAND_OF_MAFIA

    def calculate_mmr(self, rating: Optional[Rating] = None):
        if not is_mafia_win(self.game_info.game):
            return {}

        if not self.game_info.hand_of_mafia:
            return {}

        result = defaultdict(int)

        house_hand_of_mafia = get_house_from_list_by_house_id(
            self.game_info.houses, self.game_info.hand_of_mafia.house_hand_id)

        result[house_hand_of_mafia.player_id] += self.correlation_mmr

        return result
