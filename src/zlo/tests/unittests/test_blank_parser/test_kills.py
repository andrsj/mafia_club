from expects import expect, equal
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenKillsParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.kills_event = self.blank_parser.parse_kills()

    def it_should_get_proper_values(self):
        for i, value in zip(self.kills_event.kills_slots, [9, 2, 8, 7]):
            expect(i).to(equal(value))


class WhenKillsHaveMisses(BlankParserMixin):
    def given_blank_parser(self):
        matrix = self.get_matrix_data('Промахи')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.kills_event = self.blank_parser.parse_kills()

    def it_should_get_proper_values(self):
        for i, value in zip(self.kills_event.kills_slots, [10, 2, 0, 4]):
            expect(i).to(equal(value))
