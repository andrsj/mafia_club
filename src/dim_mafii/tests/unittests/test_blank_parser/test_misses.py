from expects import expect, equal, be_empty, have_len
from dim_mafii.sheet_parser.blank_version_2 import BlankParser
from dim_mafii.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenMissesParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.misses_event = self.blank_parser.parse_misses()

    def it_should_get_proper_values(self):
        expect(self.misses_event.misses_slots).to(have_len(2))
        for i, value in zip(self.misses_event.misses_slots, [0, 4]):
            expect(i).to(equal(value))


class WhenMissesIsEmpty(BlankParserMixin):
    
    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.misses_event = self.blank_parser.parse_misses()

    def it_should_get_proper_values(self):
        expect(self.misses_event.misses_slots).to(be_empty)
