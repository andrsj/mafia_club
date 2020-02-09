import json

import gspread
import numpy
from oauth2client.service_account import ServiceAccountCredentials


class SpreadSheetClient:

    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            '/home/dvasilov/Projects/zlo/guiding/credentials/ZloMafiaClub-655c0c73f071.json', scope)
        self.client = gspread.authorize(creds)

    def parse_worksheet(self, worksheet):
        game_data = [cell.value for cell in worksheet.range('B2:L46')]
        return numpy.asarray(game_data).reshape(45, 11).tolist()

    def store_data_in_json_file(self, game_data, path_to_file):
        with open(path_to_file, 'w') as f:
            json.dump(game_data, f, indent=4)
