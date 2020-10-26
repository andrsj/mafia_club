import argparse
import os
import uuid

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.adapters.infrastructure import MessageBus
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.cli.setup_env_for_test import setup_env_with_test_database


def update_game_id(worksheet, game_id):
    worksheet.update_cell(8, 4, game_id)


if __name__ == "__main__":
    cfg = os.environ.copy()
    """
        return {
        'host': env.get('DB_HOST', 'localhost'),
        'port': env.get('DB_PORT', 5432),
        'user': env.get('SECRET_DB_USER', 'test_zlo'),
        'password': env.get('SECRET_DB_PASSWORD', 'test_zlo'),
        'db_name': env.get('DB_NAME', 'test_zlo'),
    }
    """
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    my_parser = argparse.ArgumentParser(description='Parse data from spreadsheet and fill tables')
    my_parser.add_argument(
        '--games',
        default=False,
        dest='games',
        action='store_true',
        required=False,
        help="Parse and update game info"
    )
    my_parser.add_argument(
        '--houses',
        default=False,
        dest='houses',
        action='store_true',
        required=False,
        help="Parse and update houses info; Slot number. PLayer nick fouls and bonus marks"
    )
    my_parser.add_argument(
        "--best_moves",
        dest='best_moves',
        action='store_true',
        required=False,
        help="Parse and update best moves"
    )
    my_parser.add_argument(
        '--sheriff_versions',
        dest='sheriff_versions',
        action='store_true',
        required=False,
        help="Parse and update sheriff versions"
    )
    my_parser.add_argument(
        '--disqualifieds',
        dest='disqualifieds',
        action='store_true',
        required=False,
        help="Pase and update disqualifieds"
    )
    my_parser.add_argument(
        '--nominated_for_best',
        dest='nominated_for_best',
        action='store_true',
        required=False,
        help="Parse and update nominated for best"
    )
    my_parser.add_argument(
        '--voted',
        dest='voted',
        action='store_true',
        required=False,
        help="Pase and update voted"
    )

    my_parser.add_argument(
        "--sheet",
        dest='sheet_title',
        type=str,
        required=True
    )

    my_parser.add_argument(
        "--blank",
        dest='blank_title',
        type=str,
        required=True
    )

    args = my_parser.parse_args()

    handlers = [
        (args.houses, "parse_houses"),
        (args.best_moves, "parse_best_move"),
        (args.sheriff_versions, "parse_sheriff_versions"),
        (args.disqualifieds, "parse_disqualified"),
        (args.nominated_for_best, "parse_nominated_for_best"),
        (args.voted, "parse_voted_list"),
        # ("parse_sheriff_checks")
        # ("parse_kills")
        # ("parse_devise")
        # ("parse_hand_of_mafia")
        # ("get_bonus_points_from_houses_data")
        # ("get_bonus_tolerant_points_from_houses_data")
        # ("get_bonus_points_from_heading")
        # ("parse_don_checks")
        # ("parse_breaks")
        # ("parse_misses")
    ]

    client = inject.instance(SpreadSheetClient)
    bus = inject.instance(MessageBus)
    sheet = client.client.open(args.sheet_title)
    for work_sheet in sheet.worksheets():

        if work_sheet.title != args.blank_title:
            continue

        matrix = client.parse_worksheet(work_sheet)
        blank_parser = BlankParser(matrix)

        game_info = blank_parser.parse_game_info()
        if blank_parser.if_game_is_new():
            game_info.game_id = str(uuid.uuid4())
            update_game_id(work_sheet, game_info.game_id)
        if args.games:
            bus.publish(game_info)

        for arg, method_name in handlers:
            if arg:
                method = getattr(blank_parser, method_name)
                event = method()
                if not isinstance(event, list) and event is not None:
                    bus.publish(event)
                elif isinstance(event, list):
                    for event_ in event:
                        bus.publish(event_)
        break
