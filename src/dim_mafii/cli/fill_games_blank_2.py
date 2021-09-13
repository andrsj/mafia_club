import os
from datetime import datetime

from gspread.exceptions import APIError

from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database
from dim_mafii.domain.blank_worker import parse_and_write_in_db_games
from dim_mafii.domain.config import DATE_FORMAT
from dim_mafii.domain.utils import create_parser_for_blank_feeling, daterange, date_range_in_month
from dim_mafii.sheet_parser.client2 import SpreadSheetManager


def main():
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    my_parser = create_parser_for_blank_feeling()
    arguments = my_parser.parse_args()

    # --sheet="**_**_20**" --full
    # --date="**_**_20** --full"
    # --year=20** --month="******" --full
    # --start="**_**_20**" --end="**_**_20**" --full

    spreadsheet_names = []

    if arguments.date:
        spreadsheet_names = [arguments.date]

    if arguments.sheet_title:
        spreadsheet_names = [arguments.sheet_title]

    if arguments.year and arguments.month:
        spreadsheet_names = [
            single_date.strftime(DATE_FORMAT)
            for single_date in date_range_in_month(arguments.year, arguments.month)
        ]

    if arguments.end_date_of_day and arguments.start_date_of_day:
        start_date = datetime.strptime(arguments.start_date_of_day, DATE_FORMAT)
        end_date = datetime.strptime(arguments.end_date_of_day, DATE_FORMAT)
        spreadsheet_names = [
            single_date.strftime(DATE_FORMAT)
            for single_date in daterange(
                start_date,
                end_date
            )
        ]

    manager = SpreadSheetManager()

    try:
        parse_and_write_in_db_games(manager, spreadsheet_names, arguments)
    except APIError as e:
        print(f'Oooops, API Error [{e.response}], plz rerun script a little bit later')


if __name__ == '__main__':
    main()
