from expects import expect, equal, have_len, be_empty
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenSheriffVersionParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії1в1')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.sheriff_version_event = self.blank_parser.parse_sheriff_versions()

    def it_should_get_proper_values(self):
        expect(self.sheriff_version_event.sheriff_version_slots).to(have_len(2))
        expect(self.sheriff_version_event.sheriff_version_slots[0]).to(equal(10))
        expect(self.sheriff_version_event.sheriff_version_slots[1]).to(equal(5))


class WhenSheriffVersionParsedAndNoVersions(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.sheriff_version_event = self.blank_parser.parse_sheriff_versions()

    def it_should_get_proper_values(self):
        expect(self.sheriff_version_event.sheriff_version_slots).to(be_empty)
