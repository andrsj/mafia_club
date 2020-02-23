import contexts
from expects import expect, equal, be_none
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenBestMoveParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.best_move_event = self.blank_parser.parse_best_move()

    def it_should_get_proper_values(self):
        expect(self.best_move_event).to_not(be_none)
        expect(self.best_move_event.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(self.best_move_event.killed_player_slot).to(equal(9))
        expect(self.best_move_event.best_1_slot).to(equal(4))
        expect(self.best_move_event.best_2_slot).to(equal(5))
        expect(self.best_move_event.best_3_slot).to(equal(10))


class WhenBestMoveParsedAndNoData(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії1в1')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.best_move_event = self.blank_parser.parse_best_move()

    def it_should_get_proper_values(self):
        expect(self.best_move_event).to(be_none)


class WhenBestMoveParsedAndDataIsNotValid(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії2в2')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.best_move_event = self.blank_parser.parse_best_move()

    def it_should_get_proper_values(self):
        expect(self.best_move_event).to(be_none)

if __name__ == "__main__":
    contexts.main()