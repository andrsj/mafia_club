from expects import expect, equal


from zlo.domain.model import BonusFromPlayers
from zlo.domain.mmr_calculators import BestPlayerRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenPlayerGetThreeAndMoreBonuses(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        bonuses = [
            BonusFromPlayers(
                game_id=self.game.game_id,
                bonus_id=generate_uuid(),
                bonus_to=self.houses[4].house_id,
                bonus_from=self.houses[i].house_id,
            )
            for i in range(3)
        ]

        self.game_builder.with_bonuses_from_player(bonuses=bonuses)

        self.rule = BestPlayerRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_add_points_to_best_player(self):
        expect(self.new_rating[self.houses[4].player_id]).to(equal(BestPlayerRule.bonus_mmr))


class WhenBestPLayersWereTwo(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        bonuses = [
            BonusFromPlayers(
                game_id=self.game.game_id,
                bonus_id=generate_uuid(),
                bonus_to=self.houses[4].house_id,
                bonus_from=self.houses[i].house_id,
            )
            for i in range(3)
        ]
        bonuses.extend([
            BonusFromPlayers(
                game_id=self.game.game_id,
                bonus_id=generate_uuid(),
                bonus_to=self.houses[5].house_id,
                bonus_from=self.houses[i].house_id,
            )
            for i in range(6, 9)
        ])
        self.game_builder.with_bonuses_from_player(bonuses=bonuses)

        self.rule = BestPlayerRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_add_points_to_best_player(self):
        expect(self.new_rating[self.houses[4].player_id]).to(equal(BestPlayerRule.bonus_mmr))
        expect(self.new_rating[self.houses[5].player_id]).to(equal(BestPlayerRule.bonus_mmr))
