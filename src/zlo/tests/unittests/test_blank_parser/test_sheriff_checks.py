import contexts
from expects import have_len, expect, equal
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenSheriffCheckParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_sheriff_checks_parsed(self):
        self.sherriff_checks_event = self.blank_parser.parse_sheriff_checks()

    def it_should_parse_correct_values(self):
        expect(self.sherriff_checks_event.sheriff_checks).to(have_len(3))
        expect(self.sherriff_checks_event.sheriff_checks[1]).to(equal(1))
        expect(self.sherriff_checks_event.sheriff_checks[2]).to(equal(2))
        expect(self.sherriff_checks_event.sheriff_checks[3]).to(equal(10))


class WhenSheriffCheckHasEmptyValues(BlankParserMixin):
    "Suppose that sheriff was thinking about something and skip check"

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_sheriff_checks_parsed(self):
        self.sherriff_checks_event = self.blank_parser.parse_sheriff_checks()

    def it_should_parse_correct_values(self):
        expect(self.sherriff_checks_event.sheriff_checks).to(have_len(3))
        expect(self.sherriff_checks_event.sheriff_checks[1]).to(equal(1))
        expect(self.sherriff_checks_event.sheriff_checks[2]).to(equal(2))
        expect(self.sherriff_checks_event.sheriff_checks[3]).to(equal(10))


if __name__ == "__main__":
    contexts.main()
