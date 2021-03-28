from typing import Optional
from collections import defaultdict


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from zlo.domain.utils import get_house_from_list_by_house_id, is_mafia, is_citizen, is_citizen_win, is_mafia_win
from zlo.domain.mmr_calculators.constants import CORRELATION_FOR_WRONG_BREAK


class WrongBreakRule(BaseRuleMMR):

    correlation_mmr = CORRELATION_FOR_WRONG_BREAK

    def calculate_mmr(self, rating: Optional[Rating] = None):
        result = defaultdict(int)

        if not self.game_info.breaks:
            return {}

        for break_ in self.game_info.breaks:
            house_to = get_house_from_list_by_house_id(self.game_info.houses, break_.house_to)
            house_from = get_house_from_list_by_house_id(self.game_info.houses, break_.house_from)
            # Break mafia into mafia when mafia lost
            if is_citizen_win(self.game_info.game) and is_mafia(house_to) and is_mafia(house_from):
                result[house_from.player_id] += self.correlation_mmr

            # Break citizen into citizen when citizen lost
            if is_mafia_win(self.game_info.game) and is_citizen(house_to) and is_citizen(house_from):
                result[house_from.player_id] += self.correlation_mmr

        return result

