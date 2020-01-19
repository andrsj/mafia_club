import contexts
from expects import expect, equal
from zlo.cli.auth import auth
from zlo.domain.types import GameResult, AdvancedGameResult
from zlo.sheet_parser.blank_version_2 import BlankParser


class BlankParserMixin:

    def given_sheet_client(self):
        self.client = auth()
        self.sheet = self.client.open("ТестовийБланкНеДляПротоколуІРейтингу")


class WhenGameDataParsedAndCitizenWin(BlankParserMixin):

    def given_blank_parser(self):
        self.worksheet = self.sheet.get_worksheet(1)
        expect(self.worksheet.title).to(equal('ПеремогаМирних'))
        self.blank_parser = BlankParser(self.worksheet)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.citizen))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.guessing_game))


class WhenGameDataParsedAndCitizenClearWin(BlankParserMixin):

    def given_blank_parser(self):
        self.worksheet = self.sheet.get_worksheet(0)
        expect(self.worksheet.title).to(equal('СухаПеремогаМирних'))
        self.blank_parser = BlankParser(self.worksheet)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.citizen))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.clear_citizen))


class WhenGameDataParsedAndMafia3x3Win(BlankParserMixin):

    def given_blank_parser(self):
        self.worksheet = self.sheet.get_worksheet(2)
        expect(self.worksheet.title).to(equal('ПеремогаМафії3в3'))
        self.blank_parser = BlankParser(self.worksheet)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.mafia))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.three_on_three))


class WhenGameDataParsedAndMafia2x2Win(BlankParserMixin):

    def given_blank_parser(self):
        self.worksheet = self.sheet.get_worksheet(3)
        expect(self.worksheet.title).to(equal('ПеремогаМафії2в2'))
        self.blank_parser = BlankParser(self.worksheet)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.mafia))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.two_on_two))


class WhenGameDataParsedAndMafia1x1Win(BlankParserMixin):

    def given_blank_parser(self):
        self.worksheet = self.sheet.get_worksheet(4)
        expect(self.worksheet.title).to(equal('ПеремогаМафії1в1'))
        self.blank_parser = BlankParser(self.worksheet)

    def because_we_parse_game_info(self):
        self.game_result, self.advanced_game_result = self.blank_parser.parse_game_result()

    def it_should_get_proper_values(self):
        expect(self.game_result).to(equal(GameResult.mafia))
        expect(self.advanced_game_result).to(equal(AdvancedGameResult.one_on_one))


if __name__ == "__main__":
    contexts.main()
