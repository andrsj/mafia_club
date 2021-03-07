from expects import expect, equal, be_empty
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenDevisesParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.devises_event = self.blank_parser.parse_devises()
        print(self.devises_event)

    def it_should_get_proper_values(self):
        expect(self.devises_event).to_not(be_empty)
        for devise, expected_value in zip(
            self.devises_event,
            (
                {'killed': 2, 'first': 1, 'second': 7, 'third': 3},
                {'killed': 8, 'first': 3, 'second': 6, 'third': 0},
                {'killed': 7, 'first': 4, 'second': 0, 'third': 0},
            )
        ):
            expect(devise.killed_slot).to(equal(expected_value['killed']))
            expect(devise.first_slot).to(equal(expected_value['first']))
            expect(devise.second_slot).to(equal(expected_value['second']))
            expect(devise.third_slot).to(equal(expected_value['third']))
