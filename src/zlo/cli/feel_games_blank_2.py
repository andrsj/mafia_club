import os
from datetime import datetime
import inject

from gspread.exceptions import SpreadsheetNotFound
from zlo.adapters.bootstrap import bootstrap
from zlo.adapters.infrastructure import MessageBus
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.utils import create_parser_for_blank_feeling, date_range_in_month, daterange
from zlo.cli.blanks_checker import BlankChecker

from zlo.cli.setup_env_for_test import setup_env_with_test_database


def update_game_id(worksheet, game_id):
    worksheet.update_cell(8, 4, game_id)

def parse_and_write_in_db(client_parser, args):
    handlers = (
        (args.houses, "parse_houses"),
        (args.voted, "parse_voted"),
        (args.kills, "parse_kills"),
        (args.misses, "parse_misses"),
        (args.best_moves, "parse_best_move"),
        (args.don_checks, "parse_don_checks"),
        (args.disqualifieds, "parse_disqualified"),
        (args.hand_of_mafia, "parse_hand_of_mafia"),
        (args.sheriff_checks, "parse_sheriff_checks"),
        (args.sheriff_versions, "parse_sheriff_versions"),
        (args.nominated_for_best, "parse_nominated_for_best"),
        (args.bonus_from_players, "get_bonus_points_from_houses_data"),
        (args.bonus_tolerant, "get_bonus_tolerant_points_from_houses_data"),
    )
    bus = inject.instance(MessageBus)
    sheet = client_parser.client.open(args.sheet_title)

    for work_sheet in sheet.worksheets():

        print('\t', work_sheet.title)

        # if the blank was specified in parser
        if args.blank_title and work_sheet.title != args.blank_title:
            continue

        matrix = client_parser.parse_worksheet(work_sheet)
        if args.check:
            blank_checker = BlankChecker(matrix)
            errors = blank_checker.check_blank()
            work_sheet.update_cell(1, 1, 'Перевірено')
            if errors:
                work_sheet.update_cell(2, 1, 'Виявлено помилки')
                continue

        blank_parser = BlankParser(matrix)
        game_info = blank_parser.parse_game_info()
        if blank_parser.if_game_is_new():
            update_game_id(work_sheet, game_info.game_id)
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

        if args.blank_title:
            # Stop iteration, if script was runned by only one title worksheet
            break
        continue


if __name__ == "__main__":
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)
    my_parser = create_parser_for_blank_feeling()
    arguments = my_parser.parse_args()

    client = inject.instance(SpreadSheetClient)

    if arguments.sheet_title:
        # Example for this branch IF:
        # --sheet="16/10/2020" --full
        parse_and_write_in_db(client, arguments)

    if (arguments.month and arguments.year) or (arguments.start_date_of_day and arguments.end_date_of_day):
        # Example for this branch IF:
        # --year=2020 --month="Жовтень" --full

        name_sheets = None
        if arguments.month and arguments.year:
            name_sheets = [
                single_date.strftime('%d/%m/%Y')
                for single_date in date_range_in_month(arguments.year, arguments.month)
            ]
        if arguments.start_date_of_day and arguments.end_date_of_day:
            name_sheets = [
                date.strftime('%d/%m/%Y') for date in daterange(
                    datetime.strptime(arguments.start_date_of_day, '%d/%m/%Y'),
                    datetime.strptime(arguments.end_date_of_day, '%d/%m/%Y')
                )
            ]

        # For all data names like DD/MM/YYYY
        for name in name_sheets:
            print(name)
            arguments.sheet_title = name
            try:
                parse_and_write_in_db(client, arguments)

            # Not found sheet by title 'DD/MM/YYYY'
            except SpreadsheetNotFound:
                continue
