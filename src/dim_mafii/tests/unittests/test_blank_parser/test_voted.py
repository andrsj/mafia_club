from expects import expect, equal, have_len, be_none
from dim_mafii.sheet_parser.blank_version_2 import BlankParser
from dim_mafii.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenVotedParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії1в1')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.voted = self.blank_parser.parse_voted()

    def it_should_get_proper_values(self):
        expect(self.voted.voted_slots[1][0]).to(equal(1))
        expect(self.voted.voted_slots[2][0]).to(equal(4))
        expect(self.voted.voted_slots[3][0]).to(equal(5))
        expect(self.voted.voted_slots[4][0]).to(equal(7))


class WhenVotedHaveEmptyValues(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('Дискваліфікації')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.voted_event = self.blank_parser.parse_voted()

    def it_should_get_proper_values(self):
        expect(self.voted_event).to(be_none)


class WhenVotedHaveMultipleValuesInOneCircle(BlankParserMixin):
    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії3в3')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.voted_event = self.blank_parser.parse_voted()

    def it_should_correct_parse_first_vote(self):
        expect(self.voted_event.voted_slots[1]).to(have_len(2))
        expect(self.voted_event.voted_slots[1][0]).to(equal(1))
        expect(self.voted_event.voted_slots[1][1]).to(equal(2))

    def it_should_correct_parse_second_vote(self):
        expect(self.voted_event.voted_slots[2]).to(have_len(1))
        expect(self.voted_event.voted_slots[2][0]).to(equal(3))


class WhenVotedHaveEmptyValuesWithSuccessfulVotes(BlankParserMixin):
    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.voted_event = self.blank_parser.parse_voted()

    def it_should_correct_parse_0_round_votes(self):
        expect(self.voted_event.voted_slots[1]).to(have_len(1))
        expect(self.voted_event.voted_slots[1][0]).to(equal(0))

    def it_should_correct_parse_1_round_votes(self):
        expect(self.voted_event.voted_slots[2]).to(have_len(1))
        expect(self.voted_event.voted_slots[2][0]).to(equal(1))

    def it_should_correct_parse_2_round_votes(self):
        expect(self.voted_event.voted_slots[3]).to(have_len(1))
        expect(self.voted_event.voted_slots[3][0]).to(equal(5))

    def it_should_correct_parse_3_round_votes(self):
        expect(self.voted_event.voted_slots[4]).to(have_len(1))
        expect(self.voted_event.voted_slots[4][0]).to(equal(6))

    def it_should_correct_parse_4_round_votes(self):
        expect(self.voted_event.voted_slots[5][0]).to(equal(0))

    def it_should_correct_parse_5_round_votes(self):
        expect(self.voted_event.voted_slots[6]).to(have_len(1))
        expect(self.voted_event.voted_slots[6][0]).to(equal(10))
