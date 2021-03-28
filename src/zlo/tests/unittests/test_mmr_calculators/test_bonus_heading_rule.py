from expects import expect, equal, have_keys


from zlo.domain.model import BonusHeading
from zlo.domain.mmr_calculators import BonusFromHeadingRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenHeadingGiveSomeBonuses(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        bonuses = [
            BonusHeading(
                game_id=self.game.game_id,
                value=value,
                house_id=self.houses[i].house_id,
                bonus_id=generate_uuid()
            )
            for i, value in zip(range(3), [0.2, 0.3, 0.5])
        ]

        self.game_builder.with_bonuses_from_heading(bonuses=bonuses)

        self.rule = BonusFromHeadingRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_add_mmr_for_selected_players_by_heading(self):
        expect(self.new_rating[self.houses[0].player_id]).to(equal(BonusFromHeadingRule.low_bonus_mmr))
        expect(self.new_rating[self.houses[1].player_id]).to(equal(BonusFromHeadingRule.middle_bonus_mmr))
        expect(self.new_rating[self.houses[2].player_id]).to(equal(BonusFromHeadingRule.high_bonus_mmr))

    def it_should_miss_other_players(self):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if self.houses.index(house) not in (0, 1, 2))
        ))
