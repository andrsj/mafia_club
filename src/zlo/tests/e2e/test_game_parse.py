from zlo.sheet_parser.client import SpreadSheetClient


class When_game_parsed_from_sheet:

    def given_auth_client_and_worksheet(self):
        self.client = SpreadSheetClient()
        self.sheet = self.client.client.open("ТестовийБланкНеДляПротоколуІРейтингу")

    def because_we_run_game_parse(self):
        pass

    def it_should_save_game_results(self):
        pass