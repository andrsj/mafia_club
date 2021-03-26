from expects import expect, equal


from zlo.domain.model import Misses
from zlo.domain.mmr_calculators import MissRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenMafiaLose(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 1  # Citizen
        misses = [
            Misses(
                game_id=self.game.game_id,
                miss_id=generate_uuid(),
                circle_number=1,
                house_id=self.houses[2].house_id
            )
        ]
        self.game_builder.with_misses(misses=misses)
        self.rule = MissRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_remove_mmr_points_from_mafias(self):
        for i in range(1, 4):  # 1, 2, 3 - mafias players
            expect(self.new_rating[self.houses[i].player_id]).to(equal(MissRule.bonus_mmr))


class WhenMafiaWin(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Citizen
        misses = [
            Misses(
                game_id=self.game.game_id,
                miss_id=generate_uuid(),
                circle_number=1,
                house_id=self.houses[2].house_id
            )
        ]

        self.game_builder.with_misses(misses=misses)

        self.rule = MissRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_skip_game(self):
        expect(self.new_rating).to(equal({}))
