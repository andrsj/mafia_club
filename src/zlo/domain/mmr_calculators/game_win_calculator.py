from uuid import UUID
from typing import Optional
from collections import defaultdict


from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from zlo.domain.utils import is_citizen_win, is_citizen, is_mafia, is_mafia_win


class GameWinnerRule(BaseRuleMMR):

    @staticmethod
    def get_mmr_for_win(current_mmr: int):
        if current_mmr <= 1700:
            return 9
        return max(1, 9 + -1 * ((current_mmr - 1600) // 100))

    @staticmethod
    def get_mmr_for_lose(current_mmr: int):
        if current_mmr < 1700:
            return -6
        return max(-15, -6 + -1 * ((current_mmr - 1600) // 200))

    def calculate_mmr(self, rating: Optional[Rating] = None):

        result = defaultdict(int)

        for house in self.game_info.houses:

            player_id: UUID = house.player_id

            if is_citizen(house) and is_citizen_win(self.game_info.game):
                mmr = self.get_mmr_for_win(rating[player_id])
                result[player_id] += mmr

            elif is_mafia(house) and is_mafia_win(self.game_info.game):
                mmr = self.get_mmr_for_win(rating[player_id])
                result[player_id] += mmr

            else:
                mmr = self.get_mmr_for_lose(rating[player_id])
                result[player_id] += mmr

        return result
