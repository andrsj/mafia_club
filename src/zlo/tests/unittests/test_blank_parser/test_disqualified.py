from expects import expect, equal, have_len, be_empty
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenDisqualifiedParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('Дискваліфікації')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.disqualified_events = self.blank_parser.parse_disqualified()

    def it_should_get_proper_values(self):
        expect(self.disqualified_events.disqualified_slots).to(have_len(2))
        expect(self.disqualified_events.disqualified_slots[0]).to(equal(6))
        expect(self.disqualified_events.disqualified_slots[1]).to(equal(2))


class WhenDisqualifiedParsedAndNoData(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.disqualified_events = self.blank_parser.parse_disqualified()

    def it_should_get_proper_values(self):
        expect(self.disqualified_events.disqualified_slots).to(be_empty)
