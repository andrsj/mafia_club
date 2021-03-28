from expects import expect, equal, have_keys


from zlo.domain.model import Disqualified
from zlo.domain.mmr_calculators import DisqualifieldRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenPlayerWasDisqualified(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        disqualifieds = [
            Disqualified(
                game_id=self.game.game_id,
                disqualified_id=generate_uuid(),
                house=self.houses[i].house_id
            )
            for i in range(3)
        ]

        self.game_builder.with_disqualifieds(disqualifieds=disqualifieds)

        self.rule = DisqualifieldRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_remove_points_from_disqualified_players(self):
        for i in range(3):
            expect(self.new_rating[self.houses[i].player_id]).to(equal(DisqualifieldRule.correlation_mmr))

    def it_should_miss_other_players(self):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if self.houses.index(house) not in range(3))
        ))
