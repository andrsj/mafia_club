import contexts
from expects import expect, equal
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenHandOfMafiaParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.hand_of_mafia_event = self.blank_parser.parse_hand_of_mafia()

    def it_should_get_proper_values(self):
        expect(self.hand_of_mafia_event.slot_from).to(equal(2))
        expect(self.hand_of_mafia_event.slot_to).to(equal(3))


class WhenHandOfMafiaIsEmpty(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.hand_of_mafia_event = self.blank_parser.parse_hand_of_mafia()

    def it_should_get_proper_values(self):
        expect(self.hand_of_mafia_event.slot_from).to(equal(0))
        expect(self.hand_of_mafia_event.slot_to).to(equal(0))
