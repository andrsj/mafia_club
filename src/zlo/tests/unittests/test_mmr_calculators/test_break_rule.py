from expects import expect, equal, have_keys


from zlo.domain.model import Break
from zlo.domain.mmr_calculators import WrongBreakRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenCitizenWonAndMafiaBreaksToMafia(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 1  # Citizen
        breaks = [
            Break(
                game_id=self.game.game_id,
                break_id=generate_uuid(),
                house_to=self.houses[1].house_id,
                house_from=self.houses[2].house_id,
                count=10
            )
        ]

        self.game_builder.with_breaks(breaks=breaks)

        self.rule = WrongBreakRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_remove_points_from_mafia_player(self):
        expect(self.new_rating[self.houses[2].player_id]).to(equal(WrongBreakRule.correlation_mmr))

    def it_should_miss_other_players(self):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if self.houses.index(house) != 2)
        ))


class WhenMafianWonAndCitizenBreaksToCitizen(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Mafia
        breaks = [
            Break(
                game_id=self.game.game_id,
                break_id=generate_uuid(),
                house_to=self.houses[5].house_id,
                house_from=self.houses[6].house_id,
                count=10
            )
        ]

        self.game_builder.with_breaks(breaks=breaks)

        self.rule = WrongBreakRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_remove_points_from_citizen_player(self):
        expect(self.new_rating[self.houses[6].player_id]).to(equal(WrongBreakRule.correlation_mmr))

    def it_should_miss_other_players(self):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if self.houses.index(house) != 6)
        ))


class WhenMafiaBreaksInMafiaAndMafiaWon(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Mafia
        breaks = [
            Break(
                game_id=self.game.game_id,
                break_id=generate_uuid(),
                house_to=self.houses[1].house_id,
                house_from=self.houses[2].house_id,
                count=10
            )
        ]

        self.game_builder.with_breaks(breaks=breaks)

        self.rule = WrongBreakRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_miss_game(self):
        expect(self.new_rating).to(equal({}))


class WhenCitizenBreaksInCitizenAndCitizenWon(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 1  # Citizen
        breaks = [
            Break(
                game_id=self.game.game_id,
                break_id=generate_uuid(),
                house_to=self.houses[5].house_id,
                house_from=self.houses[6].house_id,
                count=10
            )
        ]

        self.game_builder.with_breaks(breaks=breaks)

        self.rule = WrongBreakRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_miss_game(self):
        expect(self.new_rating).to(equal({}))
