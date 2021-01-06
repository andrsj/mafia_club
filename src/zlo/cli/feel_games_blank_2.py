import os


import inject

from gspread.exceptions import SpreadsheetNotFound
from zlo.sheet_parser.blank_version_2 import NotFinishedBlank

from zlo.adapters.bootstrap import bootstrap
from zlo.adapters.infrastructure import MessageBus
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.utils import create_parser_for_blank_feeling, date_range_in_month
from zlo.domain.handlers import MissedPlayerError, MissedHouseError


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

        print(args.sheet_title, work_sheet.title)

        # if the blank was specified in parser
        if args.blank_title and work_sheet.title != args.blank_title:
            continue

        try:
            matrix = client_parser.parse_worksheet(work_sheet)
            blank_parser = BlankParser(matrix)

            game_info = blank_parser.parse_game_info()
            if blank_parser.if_game_is_new():
                update_game_id(work_sheet, game_info.game_id)
            else:
                if args.ready:
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

        except MissedPlayerError:
            # todo Missed player info
            print('Miss player')

        except MissedHouseError:
            # todo Missed info about house
            print('Miss house')

        except NotFinishedBlank:
            # todo Not finished blanks
            print('Not finished')

        except ValueError:
            # todo Check correct input blank
            print('Value error')

        if args.blank_title:
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
        parse_and_write_in_db(client, arguments)

    if arguments.month and arguments.year:
        name_sheets = [
            single_date.strftime('%d/%m/%Y')
            for single_date in date_range_in_month(arguments.year, arguments.month)
        ]

        for name in name_sheets:
            arguments.sheet_title = name
            try:
                parse_and_write_in_db(client, arguments)
            except SpreadsheetNotFound:
                continue
