from expects import expect, equal, be_empty
from dim_mafii.sheet_parser.blank_version_2 import BlankParser
from dim_mafii.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenBreaksParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.breaks_event = self.blank_parser.parse_breaks()

    def it_should_get_proper_values(self):
        expect(self.breaks_event).to_not(be_empty)
        for break_, expected_value in zip(
            self.breaks_event,
            (
                {"count": 8, "who_break_slot": 4, "into_slot": 1},
                {"count": 6, "who_break_slot": 5, "into_slot": 2},
            )
        ):
            expect(break_.count).to(equal(expected_value['count']))
            expect(break_.slot_from).to(equal(expected_value['who_break_slot']))
            expect(break_.slot_to).to(equal(expected_value['into_slot']))
