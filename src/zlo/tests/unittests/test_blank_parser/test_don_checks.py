from expects import expect, equal, be_empty, have_len
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenDonChecksParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.don_checks_event = self.blank_parser.parse_don_checks()

    def it_should_get_proper_values(self):
        expect(self.don_checks_event.don_checks).to(have_len(2))
        for i, value in zip(self.don_checks_event.don_checks, [3, 4]):
            expect(i).to(equal(value))


class WhenDonChecksIsEmpty(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.don_checks_event = self.blank_parser.parse_don_checks()

    def it_should_get_proper_values(self):
        expect(self.don_checks_event.don_checks).to(be_empty)


class WhenDonChecksHaveMisses(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('Промахи')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.don_checks_event = self.blank_parser.parse_don_checks()

    def it_should_get_proper_values(self):
        expect(self.don_checks_event.don_checks).to(have_len(3))
        for i, value in zip(self.don_checks_event.don_checks, [0, 1, 7]):
            expect(i).to(equal(value))
