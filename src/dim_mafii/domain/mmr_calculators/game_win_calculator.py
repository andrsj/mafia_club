from uuid import UUID
from typing import Optional
from collections import defaultdict

from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.utils import is_citizen_win, is_citizen, is_mafia, is_mafia_win
from dim_mafii.domain.mmr_calculators.constants import (
    START_BONUS_MMR_CORRELATION_FOR_LOSE,  # -6
    START_BONUS_MMR_FOR_WIN,  # 9
    LOSE_CORRELATION_STEP,  # 100
    WIN_CORRELATION_STEP,  # 50
    START_LIMIT_MMR,  # 1600
)


class GameWinnerRule(BaseRuleMMR):

    @staticmethod
    def get_mmr_for_win(current_mmr: int):
        """
        1600: START_BONUS_MMR_FOR_WIN
        1650: START_BONUS_MMR_FOR_WIN - START LIMIT MMR // WIN CORRELATION STEP
        ...
        1900: 3
        1950: 2
        2000: 1
        """
        if current_mmr <= START_LIMIT_MMR:
            return START_BONUS_MMR_FOR_WIN
        return max(1, START_BONUS_MMR_FOR_WIN + -1 * ((current_mmr - START_LIMIT_MMR) // WIN_CORRELATION_STEP))

    @staticmethod
    def get_mmr_for_lose(current_mmr: int):
        """
        1600: -6
        1700: -7
        1800: -8
        1900: -9
        ...
        """
        if current_mmr <= START_LIMIT_MMR:
            return START_BONUS_MMR_CORRELATION_FOR_LOSE
        return max(-15, START_BONUS_MMR_CORRELATION_FOR_LOSE + -1 *
                   ((current_mmr - START_LIMIT_MMR) // LOSE_CORRELATION_STEP))

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
