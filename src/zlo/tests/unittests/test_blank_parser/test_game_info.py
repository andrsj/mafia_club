from datetime import datetime

from expects import expect, equal, be_none
from zlo.domain.types import GameResult, AdvancedGameResult
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenGameWasParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.game_event = self.blank_parser.parse_game_info()

    def it_should_get_game_info(self):
        assert self.game_event.date == datetime(2020, 1, 18, 0, 0)  # 2020-01-18
        expect(self.game_event.result).to(equal(GameResult.citizen.value))
        expect(self.game_event.table).to(equal(1))
        expect(self.game_event.club).to(equal('TEST_ZLO'))
        expect(self.game_event.tournament).to(be_none)
        expect(self.game_event.advance_result).to(equal(AdvancedGameResult.guessing_game.value))
        expect(self.game_event.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
