import os
from typing import List
from datetime import datetime
import inject

from gspread.exceptions import SpreadsheetNotFound
from gspread.models import Cell
from zlo.adapters.bootstrap import bootstrap
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.utils import get_url, get_absolute_range, get_submatrix
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.cli.setup_env_for_test import setup_env_with_test_database
from zlo.domain.utils import date_range_in_month, create_parser_for_blanks_checker

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

def check_empty_blank(matrix):
    nicknames = [matrix[i][2] for i in range(10, 20)]
    heading = matrix[1][2]
    win = matrix[0][9] or matrix[1][9]
    return not any(nicknames + [heading, win])

def check_heading(matrix, tx):
    players = tx.players.all()
    heading_player = matrix[1][2].strip().lower()
    player = next((p for p in players if p.nickname == heading_player), None)
    if player is None:
        return [f"[Ведучий] Відсутній гравець в базі з ніком '{matrix[1][2]}'"]

def check_club(matrix):
    if not matrix[3][2]:
        return ['Не вказаний клуб гри']
    clubs = ['ZLO', 'Школа Зло', 'Зло']
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
        for vote in votes:
            if vote in kills:
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

def check_data(matrix):
    if not matrix[0][2]:
        return ['Відсутня дата в бланку']
    try:
        datetime.strptime(matrix[0][2], '%Y-%m-%d')
    except ValueError:
        return ['Не вірна дата в бланку']

class BlankChecker:

    __checkers_with_db = [
        check_players,
        check_heading,
    ]

    __checkers_without_db = [
        check_data,
        # check_club,  # Club name checker removed
        check_winner,
        check_correct_game
    ]

    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, matrix, uowm):
        self.matrix = matrix
        self._uowm = uowm

    def check_blank(self):
        if check_empty_blank(self.matrix):
            return

        all_errors = []
        with self._uowm.start() as tx:
            for checker in self.__checkers_with_db:
                errors = checker(self.matrix, tx)
                if errors is not None:
                    all_errors.extend(errors)

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

    name_sheets = None
    if arguments.year and arguments.month:
        name_sheets = [
            single_date.strftime('%d/%m/%Y')
            for single_date in date_range_in_month(arguments.year, arguments.month)
        ]

    if arguments.data:
        name_sheets = [arguments.data]

    all_sheets_errors = []
    for name_sheet in name_sheets:
        # list of additional requests for batch update cells from one spreadsheet
        additional_requests = []
        try:
            sheet = client.client.open(name_sheet)
        except SpreadsheetNotFound:
            continue

        print(name_sheet)
        worksheets = sheet.worksheets()

        worksheets_values = client.get_matrixs_from_sheet(sheet, worksheets)

        for worksheet, worksheet_range in zip(
                sorted(worksheets, key=lambda w: w.title),
                sorted([get_absolute_range(worksheet.title) for worksheet in worksheets])
        ):
            rows = worksheets_values[get_absolute_range(worksheet.title)]
            blank_matrix = get_submatrix(rows)
            blank_checker = BlankChecker(blank_matrix)
            blank_errors = blank_checker.check_blank()

            if blank_errors is None:
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
                        column=2,
                        row_=1,
                        value='Виявлено помилки'
                    )
                )

        if additional_requests:
            sheet.batch_update(body={
                'requests': additional_requests
            })

    errors_sheet = client.client.open('Errors')
    time_now = datetime.now()

    title = None
    if arguments.year and arguments.month:
        title = f'{arguments.year} {arguments.month} {time_now.strftime("%d-%m-%Y %H:%M:%S")}'
    if arguments.data:
        title = f'{arguments.data} {time_now.strftime("%d-%m-%Y %H:%M:%S")}'
    errors_worksheet = errors_sheet.add_worksheet(
        title,
        rows=len(all_sheets_errors),
        cols=4
    )

    cells = []
    for row, error in enumerate(all_sheets_errors, start=1):
        for col, info in enumerate(error, start=1):
            cells.append(Cell(
                row, col, info
            ))

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

    print(errors_sheet.url)
