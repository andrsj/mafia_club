import contexts
from expects import expect, equal, be_empty
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenBonusTolerantPointsFromPlayersParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_tolerant_point_from_players = self.blank_parser.get_bonus_tolerant_points_from_houses_data()

    def it_should_get_proper_values(self):
        expect(self.bonus_tolerant_point_from_players[0].slot_to).to(equal(1))
        expect(self.bonus_tolerant_point_from_players[0].slot_from).to(equal(4))

        expect(self.bonus_tolerant_point_from_players[1].slot_to).to(equal(2))
        expect(self.bonus_tolerant_point_from_players[1].slot_from).to(equal(5))

        expect(self.bonus_tolerant_point_from_players[2].slot_to).to(equal(5))
        expect(self.bonus_tolerant_point_from_players[2].slot_from).to(equal(8))


class WhenBonusTolerantPointsFromPlayersIsEmpty(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_tolerant_point_from_players = self.blank_parser.get_bonus_tolerant_points_from_houses_data()

    def it_should_get_proper_values(self):
        expect(self.bonus_tolerant_point_from_players).to(be_empty)
