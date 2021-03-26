from expects import expect, equal, have_key


from zlo.domain.model import SheriffVersion
from zlo.domain.mmr_calculators import SheriffVersionRule
from zlo.tests.unittests.test_mmr_calculators.common import BaseTestMMRCalculator


class WhenMafiaWin(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 2  # Mafia
        sheriff_versions = [
            SheriffVersion(
                game_id=self.game.game_id,
                sheriff_version_id=f'sheriff_version_id_{i}',
                house=self.houses[i].house_id
            )
            for i in range(3)
        ]

        self.game_builder.with_sheriff_versions(sheriff_versions=sheriff_versions)

        self.rule = SheriffVersionRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_add_mmr_to_mafia(self):
        expect(self.new_rating[self.houses[1].player_id]).to(equal(SheriffVersionRule.bonus_mmr))
        expect(self.new_rating[self.houses[2].player_id]).to(equal(SheriffVersionRule.bonus_mmr))

    def it_should_skip_real_sheriff(self):
        expect(self.new_rating).not_to(have_key(self.houses[0].player_id))


class WhenCitizenWin(BaseTestMMRCalculator):

    def given_game_for_rating(self):
        self.game.result = 1  # Citizen
        sheriff_versions = [
            SheriffVersion(
                game_id=self.game.game_id,
                sheriff_version_id=f'sheriff_version_id_{i}',
                house=self.houses[i].house_id
            )
            for i in range(3)
        ]

        self.game_builder.with_sheriff_versions(sheriff_versions=sheriff_versions)

        self.rule = SheriffVersionRule(game=self.game_builder.build())

    def because_rule_process_game(self):
        self.new_rating = self.rule.calculate_mmr()

    def it_should_skip_this_game(self):
        expect(self.new_rating).to(equal({}))
