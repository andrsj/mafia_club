import contexts
from expects import expect, equal
from zlo.sheet_parser.client import SpreadSheetClient


class When_auth_to_google_sheets:

    def given_client(self):
        self.client = SpreadSheetClient()

    def because_we_get_test_spreadsheet(self):
        self.sheet = self.client.client.open("ТестовийБланкНеДляПротоколуІРейтингу")

    def if_should_see_worksheet(self):
        expect(self.sheet.title).to(equal("ТестовийБланкНеДляПротоколуІРейтингу"))
