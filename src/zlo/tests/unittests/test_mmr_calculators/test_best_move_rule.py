from expects import expect, equal


from zlo.domain.model import BestMove
from zlo.domain.mmr_calculators import BestMoveRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenBestMoveHasThreeMafiaIsCalculating(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        best_move = BestMove(
            game_id=self.game.game_id,
            best_move_id=generate_uuid(),
            best_1=self.houses[1].house_id,
            best_2=self.houses[2].house_id,
            best_3=self.houses[3].house_id,
            killed_house=self.houses[4].house_id,
        )

        self.game_builder.with_best_move(best_move=best_move)

        self.rule = BestMoveRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_calculate_rating(self):
        expect(self.new_rating[self.houses[4].player_id]).to(equal(BestMoveRule.bonus_mmr_3))


class WhenBestMoveHasTwoMafiaIsCalculating(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        best_move = BestMove(
            game_id=self.game.game_id,
            best_move_id=generate_uuid(),
            best_1=self.houses[1].house_id,
            best_2=self.houses[2].house_id,
            best_3=self.houses[5].house_id,
            killed_house=self.houses[4].house_id,
        )
        self.game_builder.with_best_move(best_move=best_move)

        self.rule = BestMoveRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_calculate_rating(self):
        expect(self.new_rating[self.houses[4].player_id]).to(equal(BestMoveRule.bonus_mmr_2))


class WhenBestMoveHasOneEmptyIsCalculating(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        best_move = BestMove(
            game_id=self.game.game_id,
            best_move_id=generate_uuid(),
            best_1=self.houses[1].house_id,
            best_2=self.houses[2].house_id,
            best_3=None,
            killed_house=self.houses[4].house_id,
        )
        self.game_builder.with_best_move(best_move=best_move)

        self.rule = BestMoveRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_calculate_rating(self):
        expect(self.new_rating[self.houses[4].player_id]).to(equal(BestMoveRule.bonus_mmr_2))


class WhenBestMoveNoOneGuessedIsCalculating(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        best_move = BestMove(
            game_id=self.game.game_id,
            best_move_id=generate_uuid(),
            best_1=self.houses[7].house_id,
            best_2=self.houses[6].house_id,  # Both citizens
            best_3=None,
            killed_house=self.houses[4].house_id,
        )
        self.game_builder.with_best_move(best_move=best_move)

        self.rule = BestMoveRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_calculate_rating(self):
        expect(self.new_rating).to(equal({}))


class WhenBestMoveOnlyOneGuessedIsCalculating(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        best_move = BestMove(
            game_id=self.game.game_id,
            best_move_id=generate_uuid(),
            best_1=self.houses[2].house_id,  # Mafia
            best_2=self.houses[6].house_id,  # Citizen
            best_3=self.houses[7].house_id,  # Citizen
            killed_house=self.houses[4].house_id,
        )
        self.game_builder.with_best_move(best_move=best_move)

        self.rule = BestMoveRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_calculate_rating(self):
        expect(self.new_rating).to(equal({}))
