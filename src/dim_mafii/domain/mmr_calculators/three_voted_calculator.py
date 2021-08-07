from typing import List, Optional
from collections import defaultdict


from dim_mafii.domain.model import Voted
from dim_mafii.domain.mmr_calculators.base_rule import BaseRuleMMR, Rating
from dim_mafii.domain.utils import get_houses_from_list_of_house_ids, get_house_from_list_by_house_id, is_mafia, is_citizen
from dim_mafii.domain.mmr_calculators.constants import (
    BONUS_FOR_VOTED_THREE_CITIZEN_TO_MAFIA,
    CORRELATION_FOR_VOTED_THREE_CITIZEN_TO_CITIZEN
)


class ThreeVotedRule(BaseRuleMMR):

    plus_bonus_mmr = BONUS_FOR_VOTED_THREE_CITIZEN_TO_MAFIA
    correlation_mmr = CORRELATION_FOR_VOTED_THREE_CITIZEN_TO_CITIZEN

    def calculate_mmr(self, rating: Optional[Rating] = None):
        result = defaultdict(int)

        votes_for_game_first_night: List[Voted] = [
            voted for voted in self.game_info.votes
            if voted.day == 2
        ]

        if len(votes_for_game_first_night) != 3:
            return {}

        citizens = [house for house in self.game_info.houses if is_citizen(house)]
        mafias = [house for house in self.game_info.houses if is_mafia(house)]

        houses_ids_for_voted_players = [voted.house_id for voted in votes_for_game_first_night]
        voted = get_houses_from_list_of_house_ids(self.game_info.houses, houses_ids_for_voted_players)

        if not (set(voted) < set(citizens)):
            return {}

        for house in citizens:
            result[house.player_id] += self.correlation_mmr

        for house in mafias:
            result[house.player_id] += self.plus_bonus_mmr

        first_night_kill = next(filter(lambda k: k.circle_number == 1, self.game_info.kills), None)
        if first_night_kill and first_night_kill.killed_house_id in [house.house_id for house in citizens]:
            house = get_house_from_list_by_house_id(citizens, first_night_kill.killed_house_id)
            result.pop(house.player_id)

        return result
