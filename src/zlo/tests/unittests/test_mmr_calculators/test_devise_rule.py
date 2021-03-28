from expects import expect, equal, have_keys


from zlo.domain.model import Devise
from zlo.domain.mmr_calculators import DeviseRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


# class WhenCitizenWinWithCorrectDevise(BaseTestMMRCalculator):
#
#     @classmethod
#     def examples_data(cls):
#         # House 1, House 2, House 3, Killder house, Bonus
#         yield 1, 2, 3, 9, DeviseRule.big_bonuses[3]
#         yield 1, 2, None, 9, DeviseRule.big_bonuses[2]
#         yield 1, None, None, 9, DeviseRule.big_bonuses[1]
#
#     def given_game_for_rating(self, data):
#         self.game.result = 1  # Citizen
#         devises = [
#             Devise(
#                 game_id=self.game.game_id,
#                 devise_id=generate_uuid(),
#                 house_1=self.houses[data[0]].house_id,
#                 house_2=self.houses[data[1]].house_id if data[1] else None,
#                 house_3=self.houses[data[2]].house_id if data[2] else None,
#                 killed_house=self.houses[data[3]].house_id,
#             )
#         ]
#
#         self.game_builder.with_devises(devises=devises)
#
#         self.rule = DeviseRule(game=self.game_builder.build())
#
#     def because_rule_process_game(self):
#         self.new_rating = self.rule.calculate_mmr()
#
#     def it_should_add_points_to_killed_player(self, data):
#         expect(self.new_rating[self.houses[data[3]].player_id]).to(equal(data[4]))
#
#     def it_should_miss_other_players(self, data):
#         expect(self.new_rating).not_to(have_keys(
#             (house.player_id for house in self.houses if house != self.houses[data[3]])
#         ))
#

class WhenGameWasWithDevises(BaseTestMMRCalculator):

    @classmethod
    def examples_data(cls):
        # WRONG DEVISE WITH LOSE
        yield {
            'house_1': 1,
            'house_2': 4,
            'house_3': 5,
            'killed_house': 9,
            'correlation': DeviseRule.big_correlation[3],
            'game_result': 2
        }
        yield {
            'house_1': 1,
            'house_2': 4,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.big_correlation[2],
            'game_result': 2
        }
        yield {
            'house_1': 4,
            'house_2': None,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.big_correlation[1],
            'game_result': 2
        }
        # CORRECT DEVISE WITH WIN
        yield {
            'house_1': 1,
            'house_2': 2,
            'house_3': 3,
            'killed_house': 9,
            'correlation': DeviseRule.big_bonuses[3],
            'game_result': 1
        }
        yield {
            'house_1': 1,
            'house_2': 2,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.big_bonuses[2],
            'game_result': 1
        }
        yield {
            'house_1': 1,
            'house_2': None,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.big_bonuses[1],
            'game_result': 1
        }
        # WRONG DEVISE WITH WIN
        yield {
            'house_1': 1,
            'house_2': 4,
            'house_3': 5,
            'killed_house': 9,
            'correlation': DeviseRule.low_correlation[3],
            'game_result': 1
        }
        yield {
            'house_1': 1,
            'house_2': 4,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.low_correlation[2],
            'game_result': 1
        }
        yield {
            'house_1': 4,
            'house_2': None,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.low_correlation[1],
            'game_result': 1
        }
        # CORRECT DEVISE WITH LOSE
        yield {
            'house_1': 1,
            'house_2': 2,
            'house_3': 3,
            'killed_house': 9,
            'correlation': DeviseRule.low_bonuses[3],
            'game_result': 2
        }
        yield {
            'house_1': 1,
            'house_2': 2,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.low_bonuses[2],
            'game_result': 2
        }
        yield {
            'house_1': 1,
            'house_2': None,
            'house_3': None,
            'killed_house': 9,
            'correlation': DeviseRule.low_bonuses[1],
            'game_result': 2
        }

    def given_game_for_rating(self, data):
        self.game.result = data['game_result']
        devises = [
            Devise(
                game_id=self.game.game_id,
                devise_id=generate_uuid(),
                house_1=self.houses[data['house_1']].house_id,
                house_2=self.houses[data['house_2']].house_id if data['house_2'] else None,
                house_3=self.houses[data['house_3']].house_id if data['house_3'] else None,
                killed_house=self.houses[data['killed_house']].house_id,
            )
        ]

        self.game_builder.with_devises(devises=devises)

        self.rule = DeviseRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_add_points_to_killed_player(self, data):
        expect(self.new_rating[self.houses[data['killed_house']].player_id]).to(equal(data['correlation']))

    def it_should_miss_other_players(self, data):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if house != self.houses[data['killed_house']])
        ))
