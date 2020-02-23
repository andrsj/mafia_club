from expects import expect, equal, have_len, be_empty
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenNominatedForBestParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.nominated_for_best_event = self.blank_parser.parse_nominated_for_best()

    def it_should_get_proper_values(self):
        expect(self.nominated_for_best_event.nominated_slots).to(have_len(5))
        expect(self.nominated_for_best_event.nominated_slots[0]).to(equal(1))
        expect(self.nominated_for_best_event.nominated_slots[1]).to(equal(2))
        expect(self.nominated_for_best_event.nominated_slots[2]).to(equal(3))
        expect(self.nominated_for_best_event.nominated_slots[3]).to(equal(6))
        expect(self.nominated_for_best_event.nominated_slots[4]).to(equal(7))


class WhenNominatedForBestParsedAndNoData(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('Дискваліфікації')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.nominated_for_best_event = self.blank_parser.parse_nominated_for_best()

    def it_should_get_proper_values(self):
        expect(self.nominated_for_best_event.nominated_slots).to(be_empty)
