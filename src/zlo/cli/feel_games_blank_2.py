import os
from datetime import datetime
import inject
from time import sleep

from gspread.exceptions import SpreadsheetNotFound
from googleapiclient.discovery import build

from zlo.adapters.bootstrap import bootstrap
from zlo.adapters.infrastructure import MessageBus
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.utils import (
    create_parser_for_blank_feeling,
    date_range_in_month,
    drive_file_list,
    get_submatrix,
    daterange,
)
from zlo.domain.config import DATE_FORMAT
from zlo.cli.blanks_checker import BlankChecker, make_request_for_marking_blank
from zlo.credentials.config import credentials, API_VERSION, API_NAME
from zlo.cli.setup_env_for_test import setup_env_with_test_database


def update_game_id(worksheet, game_id):
    worksheet.update_cell(8, 4, game_id)


def parse_and_write_in_db(client_parser, args, list_files):
    handlers = (
        (args.houses, "parse_houses"),
        (args.voted, "parse_voted"),
        (args.kills, "parse_kills"),
        (args.breaks, "parse_breaks"),
        (args.misses, "parse_misses"),
        (args.devises, "parse_devises"),
        (args.best_moves, "parse_best_move"),
        (args.don_checks, "parse_don_checks"),
        (args.disqualifieds, "parse_disqualified"),
        (args.hand_of_mafia, "parse_hand_of_mafia"),
        (args.sheriff_checks, "parse_sheriff_checks"),
        (args.sheriff_versions, "parse_sheriff_versions"),
        (args.nominated_for_best, "parse_nominated_for_best"),
        (args.bonus_from_heading, "get_bonus_points_from_heading"),
        (args.bonus_from_players, "get_bonus_points_from_houses_data"),
        (args.bonus_tolerant, "get_bonus_tolerant_points_from_houses_data"),
    )
    bus = inject.instance(MessageBus)
    # Open spreadsheet by key, filter by name
    sheet = client_parser.client.open_by_key([file['id'] for file in list_files if file['name'] == args.sheet_title][0])

    # list of additional requests for batch update cells from one spreadsheet
    additional_requests = []

    worksheets = sheet.worksheets()
    worksheets_values = client.get_matrixs_from_sheet(sheet, worksheets)
    for worksheet in sorted(worksheets, key=lambda w: w.title):

        # if the blank was specified in parser
        if args.blank_title and worksheet.title != args.blank_title:
            continue

        rows = worksheets_values[worksheet.title]

        blank_matrix = get_submatrix(rows)

        if args.check:
            blank_checker = BlankChecker(blank_matrix)
            errors = blank_checker.check_blank()

            if errors is None:
                # if blank is empty
                continue

            additional_requests.append(make_request_for_marking_blank(
                    worksheet,
                    column=1,
                    row_=1,
                    value='Перевірено'
                )
            )
            if errors:
                print('\t', worksheet.title, 'has errors!')
                additional_requests.append(make_request_for_marking_blank(
                        worksheet,
                        column=1,
                        row_=2,
                        value='Виявлено помилки'
                    )
                )
                continue

        blank_parser = BlankParser(blank_matrix)
        game_info = blank_parser.parse_game_info(sheet.title)
        if blank_parser.if_game_is_new():
            update_game_id(worksheet, game_info.game_id)
        else:
            if args.ready:
                # Skip game if is already have GameID
                continue

        if args.games or args.full:
            bus.publish(game_info)

        for arg, method_name in handlers:
            if arg or args.full:
                method = getattr(blank_parser, method_name)
                event = method()
                if not isinstance(event, list) and event is not None:
                    bus.publish(event)
                elif isinstance(event, list):
                    for event_ in event:
                        bus.publish(event_)

        print('\t', worksheet.title, 'saved')

        if args.blank_title:
            # Stop iteration, if script was runned by only one title worksheet
            break
        continue

    if additional_requests:
        sheet.batch_update(body={
            'requests': additional_requests
        })

    sleep(5)


if __name__ == "__main__":
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)
    my_parser = create_parser_for_blank_feeling()
    arguments = my_parser.parse_args()

    client = inject.instance(SpreadSheetClient)
    drive = build(API_NAME, API_VERSION, credentials=credentials)
    files = drive.files()

    # Get all files from DRIVE, that visible for bot
    file_list = drive_file_list(files)

    # Filter files by permisions and type of file
    filtered_spreadsheets = [
        file for file in file_list
        if len(file['permissions']) > 1
        and file['mimeType'] == 'application/vnd.google-apps.spreadsheet'
    ]

    if arguments.sheet_title:
        # Example for this branch IF:
        # --sheet="16/10/2020" --full
        print(arguments.sheet_title)

        if arguments.sheet_title not in [file['name'] for file in filtered_spreadsheets]:
            print(f'Not found spreadsheet by title {arguments.sheet_title}')
        else:
            try:
                parse_and_write_in_db(client, arguments, filtered_spreadsheets)

            except SpreadsheetNotFound:
                print(f'Not found spreadsheet by title {arguments.sheet_title}')

    if (arguments.month and arguments.year) or (arguments.start_date_of_day and arguments.end_date_of_day):

        name_sheets = None

        # Example for this branch IF:
        # --year=2020 --month="Жовтень" --full
        if arguments.month and arguments.year:
            name_sheets = [
                single_date.strftime(DATE_FORMAT)
                for single_date in date_range_in_month(arguments.year, arguments.month)
            ]

        # Example for this branch IF:
        # --start="01/01/2020" --end="31/12/2020"
        if arguments.start_date_of_day and arguments.end_date_of_day:
            name_sheets = [
                date.strftime(DATE_FORMAT) for date in daterange(
                    datetime.strptime(arguments.start_date_of_day, DATE_FORMAT),
                    datetime.strptime(arguments.end_date_of_day, DATE_FORMAT)
                )
            ]

        # For all data names like DD/MM/YYYY
        for name in name_sheets:

            # If spreadsheet not found in filtered sheets
            if name not in [file['name'] for file in filtered_spreadsheets]:
                # Skip
                continue

            print(name)
            arguments.sheet_title = name
            try:
                parse_and_write_in_db(client, arguments, filtered_spreadsheets)

            # Not found sheet by title 'DD/MM/YYYY'
            except SpreadsheetNotFound:
                continue
