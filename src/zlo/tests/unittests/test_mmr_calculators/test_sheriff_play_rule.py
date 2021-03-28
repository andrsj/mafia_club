from expects import expect, equal, have_key, have_keys


from zlo.domain.mmr_calculators import SheriffPlayRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator


class WhenSheriffWon(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 1
        self.rule = SheriffPlayRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_add_mmr_points_to_sheriff(self):
        expect(self.new_rating[self.houses[0].player_id]).to(equal(SheriffPlayRule.bonus_mmr))

    def it_should_miss_other_players(self):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if self.houses.index(house) != 0)
        ))


class WhenSheriffLost(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2
        self.rule = SheriffPlayRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_skip_sheriff_player(self):
        expect(self.new_rating).not_to(have_key(self.houses[0].player_id))

    def it_should_skip_game(self):
        expect(self.new_rating).to(equal({}))
