from expects import have_len, expect, equal, be_empty
from dim_mafii.sheet_parser.blank_version_2 import BlankParser
from dim_mafii.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenSheriffCheckParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('СухаПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_sheriff_checks_parsed(self):
        self.sherriff_checks_event = self.blank_parser.parse_sheriff_checks()

    def it_should_parse_correct_values(self):
        expect(self.sherriff_checks_event.sheriff_checks).to(have_len(3))
        for i, value in zip(self.sherriff_checks_event.sheriff_checks, [1, 2, 10]):
            expect(i).to(equal(value))


class WhenSheriffCheckHasEmptyValues(BlankParserMixin):
    """Suppose that sheriff was thinking about something and skip check"""

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_sheriff_checks_parsed(self):
        self.sherriff_checks_event = self.blank_parser.parse_sheriff_checks()

    def it_should_parse_correct_values(self):
        expect(self.sherriff_checks_event.sheriff_checks).to(be_empty)


class WhenSheriffCheckHasMisses(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('Промахи')
        self.blank_parser = BlankParser(matrix)

    def because_sheriff_checks_parsed(self):
        self.sherriff_checks_event = self.blank_parser.parse_sheriff_checks()

    def it_should_parse_correct_values(self):
        expect(self.sherriff_checks_event.sheriff_checks).to(have_len(4))
        for i, value in zip(self.sherriff_checks_event.sheriff_checks, [2, 0, 3, 4]):
            expect(i).to(equal(value))
