from expects import expect, equal, have_key


from zlo.domain.model import Voted, Kills
from zlo.domain.mmr_calculators import ThreeVotedRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator


class WhenMafiaWinWithFirstNightKill(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Mafia
        first_night_kill = Kills(
            game_id=self.game.game_id,
            kill_id='kill_id_1',
            circle_number=1,
            killed_house_id=self.houses[5].house_id
        )
        votes = [
            Voted(
                game_id=self.game.game_id,
                voted_id=f'voted_id_{i}',
                day=2,
                house_id=self.houses[i].house_id
            )
            for i in range(5, 8)
        ]

        self.game_builder.\
            with_kills(kills=[first_night_kill]).\
            with_votes(votes=votes)

        self.rule = ThreeVotedRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_skip_first_killed_player(self):
        expect(self.new_rating).not_to(have_key(self.houses[5].player_id))

    def it_should_remove_points_to_citizens_players(self):
        for house in filter(lambda h: h.slot != 6 and h.role in (0, 2), self.houses):  # Citizen
            expect(self.new_rating[house.player_id]).to(equal(ThreeVotedRule.minus_bonus_mmr))

    def it_should_add_points_to_mafias_players(self):
        for house in filter(lambda h: h.role in (1, 3), self.houses):  # Mafia
            expect(self.new_rating[house.player_id]).to(equal(ThreeVotedRule.plus_bonus_mmr))


class WhenMafiaWinWithoutFirstNightKill(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Mafia
        votes = [
            Voted(
                game_id=self.game.game_id,
                voted_id=f'voted_id_{i}',
                day=2,
                house_id=self.houses[i].house_id
            )
            for i in range(5, 8)
        ]

        self.game_builder.with_votes(votes=votes)

        self.rule = ThreeVotedRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_remove_points_to_citizens_players(self):
        for house in filter(lambda h: h.slot != 6 and h.role in (0, 2), self.houses):  # Citizen
            expect(self.new_rating[house.player_id]).to(equal(ThreeVotedRule.minus_bonus_mmr))

    def it_should_add_points_to_mafias_players(self):
        for house in filter(lambda h: h.role in (1, 3), self.houses):  # Mafia
            expect(self.new_rating[house.player_id]).to(equal(ThreeVotedRule.plus_bonus_mmr))


class WhenCitizenWin(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 1  # Citizen
        votes = [
            Voted(
                game_id=self.game.game_id,
                voted_id=f'voted_id_{i}',
                day=2,
                house_id=self.houses[i].house_id
            )
            for i in range(2, 5)
        ]

        self.game_builder.with_votes(votes=votes)

        self.rule = ThreeVotedRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_not_change_rating(self):
        expect(self.new_rating).to(equal({}))
