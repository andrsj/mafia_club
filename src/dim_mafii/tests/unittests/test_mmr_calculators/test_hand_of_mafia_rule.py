from expects import expect, equal, have_keys


from dim_mafii.domain.model import HandOfMafia
from dim_mafii.domain.mmr_calculators import HandOfMafiaRule
from dim_mafii.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator, generate_uuid


class WhenMafiaWinWithHandPlayer(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Mafia
        hand_of_mafia = HandOfMafia(
            game_id=self.game.game_id,
            hand_of_mafia_id=generate_uuid(),
            house_hand_id=self.houses[4].house_id,
            victim_id=self.houses[5].house_id
        )

        self.game_builder.with_hand_of_mafia(hand_of_mafia)

        self.rule = HandOfMafiaRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_remove_points_from_hand_player(self):
        expect(self.new_rating[self.houses[4].player_id]).to(equal(HandOfMafiaRule.correlation_mmr))

    def it_should_miss_other_players(self):
        expect(self.new_rating).not_to(have_keys(
            (house.player_id for house in self.houses if self.houses.index(house) != 4)
        ))
