import contexts
from expects import expect, equal, have_keys
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenBonusPointsFromPlayersParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_points_from_players_event = self.blank_parser.get_bonus_points_from_houses_data()

    def it_should_get_proper_values(self):
        expect(self.bonus_points_from_players_event.bonus).to(have_keys(2, 4))
        expect(self.bonus_points_from_players_event.bonus[2]).to(equal(4))
        expect(self.bonus_points_from_players_event.bonus[4]).to(equal(5))


class WhenBonusPointsFromPlayersIsEmpty(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_points_from_players_event = self.blank_parser.get_bonus_points_from_houses_data()

    def it_should_get_proper_values(self):
        expect(self.bonus_points_from_players_event.bonus).to(equal({}))
