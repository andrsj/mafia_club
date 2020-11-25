import contexts
from expects import expect, equal, have_keys
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenBonusTolerantPointsFromPlayersParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_tolerant_point_from_players = self.blank_parser.get_bonus_tolerant_points_from_houses_data()

    def it_should_get_proper_values(self):
        expect(self.bonus_tolerant_point_from_players.bonuses).to(have_keys(4, 5, 8))
        expect(self.bonus_tolerant_point_from_players.bonuses[4]).to(equal(1))
        expect(self.bonus_tolerant_point_from_players.bonuses[5]).to(equal(2))
        expect(self.bonus_tolerant_point_from_players.bonuses[8]).to(equal(5))


class WhenBonusTolerantPointsFromPlayersIsEmpty(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_tolerant_point_from_players = self.blank_parser.get_bonus_tolerant_points_from_houses_data()

    def it_should_get_proper_values(self):
        expect(self.bonus_tolerant_point_from_players.bonuses).to(equal({}))
