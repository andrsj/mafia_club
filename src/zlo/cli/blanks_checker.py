import os
from time import sleep
from typing import List
from datetime import datetime
import inject

from gspread.exceptions import SpreadsheetNotFound
from gspread.models import Cell
from googleapiclient.discovery import build

from zlo.adapters.bootstrap import bootstrap
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.utils import get_url, get_submatrix, drive_file_list
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.config import DATE_FORMAT
from zlo.credentials.config import credentials, API_VERSION, API_NAME
from zlo.domain.utils import date_range_in_month, create_parser_for_blanks_checker, daterange

from zlo.cli.setup_env_for_test import setup_env_with_test_database


def make_request_for_marking_blank(work_sheet, column: int, row_: int, value: str):
    return {
        # Automatically write value in the appropriate field
        'updateCells': {
            'fields': 'userEnteredValue',
            # Cell:
            'range': {
                # Column:
                "startColumnIndex": column - 1,
                "endColumnIndex": column,
                # Row:
                "startRowIndex": row_ - 1,
                "endRowIndex": row_,
                "sheetId": work_sheet.id
            },
            'rows': [{
                'values': {
                    # Finally we enter this value
                    'userEnteredValue': {
                        'stringValue': value
                    }
                }
            }],
        }
    }

def check_empty_blank(matrix) -> bool:
    nicknames = [matrix[i][2] for i in range(10, 20)]
    # if all was empty - return True
    return not any(nicknames)

def check_heading(matrix, tx):
    players = tx.players.all()
    heading_player = matrix[1][2].strip().lower()
    player = next((p for p in players if p.nickname == heading_player), None)
    if player is None:
        return [f"[Ведучий] Відсутній гравець в базі з ніком '{matrix[1][2]}'"]

def check_club(matrix):
    if not matrix[3][2]:
        return ['Не вказаний клуб гри']
    clubs = ['ZLO', 'Школа Зло']
    if matrix[3][2].lower() not in [club.lower() for club in clubs]:
        return [f"Не вірна назва клубу '{matrix[3][2]}'"]

def check_winner(matrix):
    if matrix[0][9] or matrix[1][9]:
        return
    return ['Не вказано переможця ігри']

def check_correct_game(matrix):
    kills = [BlankParser.get_slot_or_count_number_from_string(value) for value in matrix[33][2:] if value]
    voted = [BlankParser.get_voted_from_string(value) for value in matrix[44][2:] if value]

    errors = []
    for votes in voted:
        if votes is not None:
            for vote in votes:
                if vote and vote in kills:
                    errors.append(f'Заголосований і вбитий мають один і той же слот {vote}')

    return errors

def check_players(matrix, tx) -> List[str]:
    errors = []

    players = tx.players.all()

    for i in range(1, 11):
        row_number = i + 9
        try:
            BlankParser.get_role_from_string(matrix[row_number][0])
        except ValueError:
            errors.append(f"Не вірна роль '{matrix[row_number][0]}' в гравця під слотом {i}")

        player = next((p for p in players if p.nickname == matrix[row_number][2].lower().strip()), None)
        if player is None:
            errors.append(f"Відсутній гравець в базі з ніком '{matrix[row_number][2]}' за слотом {i}")

    if not any([matrix[i + 9][0] for i in range(1, 11)]):
        errors.append('Відсутні ролі для гравців')

    return errors

def check_bonuses(matrix) -> List[str]:
    errors = []

    for i in range(1, 11):
        row_number = i + 9
        try:
            BlankParser.get_bonus_mark(matrix[row_number][7])
            BlankParser.get_bonus_mark(matrix[row_number][9])
        except ValueError:
            errors.append(f'Не вірна оцінка від ведучого для слоту {i}')

    return errors


class BlankChecker:

    __checkers_with_db = [
        check_players,
        check_heading,
    ]

    __checkers_without_db = [
        # check_club,  # Club name checker removed
        check_winner,
        check_correct_game,
        check_bonuses
    ]

    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, matrix, uowm):
        self.matrix = matrix
        self._uowm = uowm

    def check_blank(self):
        """
        Return list of errors for blank
        If blank was empty - return None
        (Useful for handling such exceptions)
        """
        if check_empty_blank(self.matrix):
            # Return None if blank was empty for game
            return

        all_errors = []
        with self._uowm.start() as tx:
            # Checkers with DB utils
            for checker in self.__checkers_with_db:
                errors = checker(self.matrix, tx)
                if errors is not None:
                    all_errors.extend(errors)

        # Checkers only correct filling of the blank
        for checker in self.__checkers_without_db:
            errors = checker(self.matrix)
            if errors is not None:
                all_errors.extend(errors)

        return all_errors


if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    my_parser = create_parser_for_blanks_checker()
    arguments = my_parser.parse_args()

    client = inject.instance(SpreadSheetClient)
    drive = build(API_NAME, API_VERSION, credentials=credentials)
    files = drive.files()

    file_list = drive_file_list(files)

    filtered_spreadsheet = [
        file for file in file_list
        if len(file['permissions']) > 1
        and file['mimeType'] == 'application/vnd.google-apps.spreadsheet'
    ]

    name_sheets = None
    if arguments.year and arguments.month:
        name_sheets = [
            single_date.strftime(DATE_FORMAT)
            for single_date in date_range_in_month(arguments.year, arguments.month)
        ]

    if arguments.end_date_of_day and arguments.start_date_of_day:
        name_sheets = [
            single_date.strftime(DATE_FORMAT)
            for single_date in daterange(
                datetime.strptime(arguments.start_date_of_day, DATE_FORMAT),
                datetime.strptime(arguments.end_date_of_day, DATE_FORMAT)
            )
        ]

    if arguments.data:
        name_sheets = [arguments.data]

    all_sheets_errors = []
    for name_sheet in name_sheets:
        # list of additional requests for batch update cells from one spreadsheet
        additional_requests = []

        if name_sheet not in [file['name'] for file in filtered_spreadsheet]:
            continue

        try:
            sheet = client.client.open_by_key(
                [file['id'] for file in filtered_spreadsheet if file['name'] == name_sheet][0]
            )

        except SpreadsheetNotFound:
            continue

        print(name_sheet)
        worksheets = sheet.worksheets()

        worksheets_values = client.get_matrixs_from_sheet(sheet, worksheets)

        for worksheet in sorted(worksheets, key=lambda w: w.title):
            rows = worksheets_values[worksheet.title]
            blank_matrix = get_submatrix(rows)
            blank_checker = BlankChecker(blank_matrix)
            blank_errors = blank_checker.check_blank()

            if blank_errors is None:
                print(f'Empty worksheet: \'{worksheet.title}\'')
                continue

            for blank_error in blank_errors:
                all_sheets_errors.append((
                    name_sheet,
                    worksheet.title,
                    blank_error,
                    get_url(worksheet.url)
                ))

            print('\t', worksheet.title)

            additional_requests.append(make_request_for_marking_blank(
                    worksheet,
                    column=1,
                    row_=1,
                    value='Перевірено'
                )
            )
            if blank_errors:
                additional_requests.append(make_request_for_marking_blank(
                        worksheet,
                        column=1,
                        row_=2,
                        value='Виявлено помилки'
                    )
                )

        if additional_requests:
            sheet.batch_update(body={
                'requests': additional_requests
            })

        if arguments.end_date_of_day and arguments.start_date_of_day:
            sleep(10)

    errors_sheet = client.client.open_by_key('1rNX_PVdrTVr2z9N5jCcxoVWLGamByzz18lO6yyg33jQ')
    time_now = datetime.now()

    cells = []
    for row, error in enumerate(all_sheets_errors, start=1):
        for col, info in enumerate(error, start=1):
            cells.append(Cell(
                row, col, info
            ))

    if cells:

        title = f'{time_now.strftime("%d-%m-%Y %H:%M:%S")}'
        if arguments.year and arguments.month:
            title = f'{arguments.year} {arguments.month} {time_now.strftime("%d-%m-%Y %H:%M:%S")}'
        if arguments.end_date_of_day and arguments.start_date_of_day:
            title = f'From {arguments.start_date_of_day} to {arguments.end_date_of_day}'
        if arguments.data:
            title = f'{arguments.data} {time_now.strftime("%d-%m-%Y %H:%M:%S")}'
        errors_worksheet = errors_sheet.add_worksheet(
            title,
            rows=len(all_sheets_errors),
            cols=4
        )

        errors_worksheet.update_cells(cells)

        errors_sheet.batch_update(body={
            'requests': [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": errors_worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 4
                        }
                    }
                }
            ]
        })

        print(get_url(errors_worksheet.url))

    else:
        print('No errors')
