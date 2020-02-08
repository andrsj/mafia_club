import json
import os

import contexts
from expects import expect, equal
from zlo.domain.types import GameResult, AdvancedGameResult
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests import fixtures


class BlankParserMixin:
    def get_matrix_data(self, file_name):
        file_path = os.path.join(os.path.dirname(fixtures.__file__), file_name + '.json')
        with open(file_path, 'r') as f:
            matrix = json.load(f)
        return matrix


class WhenGameDataParsedAndCitizenWin(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.citizen))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.guessing_game))


class WhenGameDataParsedAndCitizenClearWin(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('СухаПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.citizen))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.clear_citizen))


class WhenGameDataParsedAndMafia3x3Win(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії3в3')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.mafia))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.three_on_three))


class WhenGameDataParsedAndMafia2x2Win(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії2в2')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.mafia))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.two_on_two))


class WhenGameDataParsedAndMafia1x1Win(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії1в1')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.mafia))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.one_on_one))


if __name__ == "__main__":
    contexts.main()
