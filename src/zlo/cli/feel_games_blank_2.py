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
        "--sheet",
        dest='sheet_title',
        type=str,
        required=True
    )

    args = my_parser.parse_args()

    client = inject.instance(SpreadSheetClient)
    bus = inject.instance(MessageBus)
    sheet = client.client.open(args.sheet_title)
    for work_sheet in sheet.worksheets():
        matrix = client.parse_worksheet(work_sheet)
        blank_parser = BlankParser(matrix)
        game_info = blank_parser.parse_game_info()
        if not blank_parser.if_game_is_new():
            game_info.game_id = str(uuid.uuid4())
            update_game_id(work_sheet, game_info.game_id)
        if args.games:
            bus.publish(game_info)
        break
