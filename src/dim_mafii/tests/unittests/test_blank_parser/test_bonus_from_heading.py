from expects import expect, equal, be_empty
from dim_mafii.sheet_parser.blank_version_2 import BlankParser
from dim_mafii.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenBonusFromHeadingParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('АндрійБланк')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_points_from_heading = self.blank_parser.get_bonus_points_from_heading()

    def it_should_get_proper_values(self):
        expect(self.bonus_points_from_heading[0].house_slot).to(equal(6))
        expect(self.bonus_points_from_heading[0].value).to(equal(0.3))

        expect(self.bonus_points_from_heading[1].house_slot).to(equal(7))
        expect(self.bonus_points_from_heading[1].value).to(equal(0.2))


class WhenBonusFromPlayersFromHeadingIsEmpty(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМафії3в3')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.bonus_points_from_heading = self.blank_parser.get_bonus_points_from_heading()

    def it_should_get_proper_values(self):
        expect(self.bonus_points_from_heading).to(be_empty)
