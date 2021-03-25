from typing import List
from collections import defaultdict


from zlo.domain import model
from zlo.domain.mmr_calculators.base_rule import BaseRuleMMR
from zlo.domain import types
from zlo.domain.mmr_calculators.constants import (
    BONUS_FOR_VOTED_THREE_CITIZEN_TO_MAFIA,
    BONUS_FOR_VOTED_THREE_CITIZEN_TO_CITIZEN
)


class ThreeVotedRule(BaseRuleMMR):

    plus_bonus_mmr = BONUS_FOR_VOTED_THREE_CITIZEN_TO_MAFIA
    minus_bonus_mmr = BONUS_FOR_VOTED_THREE_CITIZEN_TO_CITIZEN

    def calculate_mmr(self):
        result = defaultdict(int)

        votes_for_game_first_night: List[model.Voted] = [
            voted for voted in self.game_info.votes
            if voted.day == 2
        ]

        if len(votes_for_game_first_night) != 3:
            return {}

        citizens = [house for house in self.game_info.houses if house.role in (
            types.ClassicRole.citizen.value, types.ClassicRole.sheriff.value)]

        mafias = [house for house in self.game_info.houses if house.role in (
            types.ClassicRole.mafia.value, types.ClassicRole.don.value)]

        houses_ids_for_voted_players = [voted.house_id for voted in votes_for_game_first_night]
        voted = [house for house in self.game_info.houses if house.house_id in houses_ids_for_voted_players]

        if not (set(voted) < set(citizens)):
            return {}

        for house in citizens:
            result[house.player_id] += self.minus_bonus_mmr

        for house in mafias:
            result[house.player_id] += self.plus_bonus_mmr

        first_night_kill = next(filter(lambda k: k.circle_number == 1, self.game_info.kills), None)
        if first_night_kill and first_night_kill.killed_house_id in [house.house_id for house in citizens]:
            house = next(filter(lambda h: h.house_id == first_night_kill.killed_house_id, citizens))
            result.pop(house.player_id)

        return result
