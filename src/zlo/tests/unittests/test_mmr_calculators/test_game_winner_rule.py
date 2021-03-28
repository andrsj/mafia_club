from expects import expect, equal


from zlo.domain.mmr_calculators import GameWinnerRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator

class WhenGameFinished(BaseTestMMRCalculator):

    @classmethod
    def examples_data(cls):
        yield {  # Citizen won
            'result': 1,
            'rating': 1000,
            'points_lose': -6,
            'points_win': 9,
            'roles': (0, 2)
        }
        yield {  # Mafia won
            'result': 2,
            'rating': 1000,
            'points_lose': -6,
            'points_win': 9,
            'roles': (1, 3)
        }
        yield {
            'result': 1,
            'rating': 1750,
            'points_lose': -6,
            'points_win': 8,
            'roles': (0, 2)
        }
        yield {
            'result': 1,
            'rating': 1850,
            'points_lose': -7,
            'points_win': 7,
            'roles': (0, 2)
        }
        yield {
            'result': 1,
            'rating': 1950,
            'points_lose': -7,
            'points_win': 6,
            'roles': (0, 2)
        }
        yield {
            'result': 1,
            'rating': 2050,
            'points_lose': -8,
            'points_win': 5,
            'roles': (0, 2)
        }

    def given_game_for_rating(self, data):
        self.game.result = data['result']
        self.rating = {house.player_id: data['rating'] for house in self.houses}

        self.rule = GameWinnerRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr(self.rating)

    def it_should_calculate_rating(self, data):
        for house in self.houses:
            value = data['points_win'] if house.role in data['roles'] else data['points_lose']
            expect(self.new_rating[house.player_id]).to(equal(value))
