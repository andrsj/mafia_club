from collections import defaultdict
from typing import Optional


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from zlo.domain.utils import (
    get_houses_from_list_of_house_ids,
    is_mafia, is_citizen,
    is_citizen_win, is_mafia_win,
    get_house_from_list_by_house_id
)
from zlo.domain.mmr_calculators.constants import (
    LOW_BONUS_FOR_CORRECT_DEVISE_FOR_1,
    LOW_BONUS_FOR_CORRECT_DEVISE_FOR_2,
    LOW_BONUS_FOR_CORRECT_DEVISE_FOR_3,
    BIG_BONUS_FOR_CORRECT_DEVISE_FOR_1,
    BIG_BONUS_FOR_CORRECT_DEVISE_FOR_2,
    BIG_BONUS_FOR_CORRECT_DEVISE_FOR_3,
    LOW_CORRELATION_FOR_WRONG_DEVISE_FOR_1,
    LOW_CORRELATION_FOR_WRONG_DEVISE_FOR_2,
    LOW_CORRELATION_FOR_WRONG_DEVISE_FOR_3,
    BIG_CORRELATION_FOR_WRONG_DEVISE_FOR_1,
    BIG_CORRELATION_FOR_WRONG_DEVISE_FOR_2,
    BIG_CORRELATION_FOR_WRONG_DEVISE_FOR_3,
)


class DeviseRule(BaseRuleMMR):

    low_bonuses = {
        1: LOW_BONUS_FOR_CORRECT_DEVISE_FOR_1,
        2: LOW_BONUS_FOR_CORRECT_DEVISE_FOR_2,
        3: LOW_BONUS_FOR_CORRECT_DEVISE_FOR_3,
    }
    big_bonuses = {
        1: BIG_BONUS_FOR_CORRECT_DEVISE_FOR_1,
        2: BIG_BONUS_FOR_CORRECT_DEVISE_FOR_2,
        3: BIG_BONUS_FOR_CORRECT_DEVISE_FOR_3,
    }
    low_correlation = {
        1: LOW_CORRELATION_FOR_WRONG_DEVISE_FOR_1,
        2: LOW_CORRELATION_FOR_WRONG_DEVISE_FOR_2,
        3: LOW_CORRELATION_FOR_WRONG_DEVISE_FOR_3,
    }
    big_correlation = {
        1: BIG_CORRELATION_FOR_WRONG_DEVISE_FOR_1,
        2: BIG_CORRELATION_FOR_WRONG_DEVISE_FOR_2,
        3: BIG_CORRELATION_FOR_WRONG_DEVISE_FOR_3,
    }

    def calculate_mmr(self, rating: Optional[Rating] = None):
        result = defaultdict(int)

        for devise in self.game_info.devises:
            choosed_houses = get_houses_from_list_of_house_ids(self.game_info.houses, devise.choosen_houses)
            killed_house = get_house_from_list_by_house_id(self.game_info.houses, devise.killed_house)
            if is_mafia(killed_house):
                continue

            amount_of_houses_in_devise = len(choosed_houses)
            if not amount_of_houses_in_devise:
                continue
            # If all houses is Mafia or Don and Won citizen
            # If device is right and team win -> big bonus
            if all(map(is_mafia, choosed_houses)) and is_citizen_win(self.game_info.game):
                result[killed_house.player_id] += self.big_bonuses[amount_of_houses_in_devise]

            # If all houses is Mafia or Don and Won mafia
            # If device is right and team loose -> small bonus
            elif all(map(is_mafia, choosed_houses)) and is_mafia_win(self.game_info.game):
                result[killed_house.player_id] += self.low_bonuses[amount_of_houses_in_devise]

            # If any house Citizen or Sheriff and Won mafia
            # if device is wrong and team loose -> big minus
            elif any(map(is_citizen, choosed_houses)) and is_mafia_win(self.game_info.game):
                result[killed_house.player_id] += self.big_correlation[amount_of_houses_in_devise]

            # If any house Citizen or Sheriff and Won citizen
            # If device is wrong and team win -> small minus
            elif any(map(is_citizen, choosed_houses)) and is_citizen_win(self.game_info.game):
                result[killed_house.player_id] += self.low_correlation[amount_of_houses_in_devise]

        return result
