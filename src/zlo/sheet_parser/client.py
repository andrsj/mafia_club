import json
from os.path import dirname
from typing import Dict, List

import gspread
from gspread.models import Worksheet, Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials

from zlo import credentials
from zlo.domain.utils import get_absolute_range


class SpreadSheetClient:

    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            dirname(credentials.__file__) + "/zlomafiaclub-bf747a844d45.json", scope)
        self.client = gspread.authorize(creds)

    @staticmethod
    def get_matrix_for_one_worksheet(worksheet: Worksheet):
        all_values = worksheet.get_all_values()
        return [row[1:12] for row in all_values[1:46]]

    @staticmethod
    def get_matrixs_from_sheet(sheet: Spreadsheet, worksheets: List[Worksheet]) -> Dict[str, List[List]]:
        """
        Return dictionary, when keys - absolute names of worksheets,
        values - matrix from all values in this worksheet
        """
        ranges = [get_absolute_range(worksheet.title) for worksheet in worksheets]
        response = sheet.values_batch_get(ranges)
        """
        response = {
            spreadsheet: '***',
            valueRanges: [
                {
                    ranges: '***',
                    majorDimension: 'ROWS',
                    values: [
                        [],
                        [],
                        [],
                        ...
                    ]
                }
            ]
        }
        """
        worksheets_values = {}

        # TODO rewrite this code down below to find normal RANGE ['NAME!A1:AC1000']
        # TODO OR rewrite code on upper level to use FULL range name

        # worksheet_range['range'] ?

        # worksheet_range -> 'AAA!A1:AC1001'
        # sheet -> 'TestBlankForEndToEnd'  [id: '14RY4cbKMFtzKw10gxaFnwBnO8_8favFLULRGnZqU8Rw']

        # worksheet_range -> 'Стіл1Гра1'A1:AC1000'
        # sheet -> '30_04_2021'

        for worksheet_range in response['valueRanges']:
            if 'values' in worksheet_range:
                worksheets_values[worksheet_range['range'].split("'")[1]] = worksheet_range['values']

        return worksheets_values

    @staticmethod
    def store_data_in_json_file(game_data, path_to_file):
        with open(path_to_file, 'w') as f:
            json.dump(game_data, f, indent=4)
