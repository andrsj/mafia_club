import argparse
import os

from zlo.adapters.bootstrap import bootstrap
from zlo.cli.auth import auth
from zlo.sheet_parser.blank_version_2 import BlankParser


if __name__ == "__main__":
    cfg = os.environ.copy()
    bootstrap(cfg)

    client = auth()

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

    sheet = client.open(args.sheet_title)
    for work_sheet in sheet.worksheets():
        blank_parser = BlankParser(work_sheet)
        game_data = work_sheet.range('A2:K46')
        # game_data = blank_parser.parse_game_info()
        print(game_data)

    # game_data = blank_parser



