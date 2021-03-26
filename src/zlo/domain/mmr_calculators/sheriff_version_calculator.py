from typing import List
from collections import defaultdict

from zlo.domain import model, types
from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain.mmr_calculators.constants import BONUS_FOR_PLAYING_LIKE_SHERIFF


class SheriffVersionRule(BaseRuleMMR):

    bonus_mmr = BONUS_FOR_PLAYING_LIKE_SHERIFF

    def calculate_mmr(self):
        if self.game_info.game.result != types.GameResult.mafia.value:
            return {}

        if not self.game_info.sheriff_versions:
            return {}

        result = defaultdict(int)

        # Get all mafias
        black_houses_for_game: List[model.House] = [
            house for house in self.game_info.houses
            if house.role in (
                types.ClassicRole.mafia.value,
                types.ClassicRole.don.value
            )
        ]

        for house in black_houses_for_game:
            # Check if mafia house was in sheriff version
            if house.house_id in [version.house for version in self.game_info.sheriff_versions]:
                result[house.player_id] += self.bonus_mmr

        return result
