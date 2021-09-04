import os
from datetime import datetime

from gspread.exceptions import APIError

from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database
from dim_mafii.domain.blank_worker import check_spreadsheets_for_errors
from dim_mafii.domain.config import DATE_FORMAT
from dim_mafii.domain.utils import create_parser_for_blanks_checker, date_range_in_month, daterange
from dim_mafii.sheet_parser.client2 import SpreadSheetManager


def main():
    my_parser = create_parser_for_blanks_checker()
    arguments = my_parser.parse_args()

    names_spreadsheets = []

    if arguments.name:
        names_spreadsheets = [arguments.name]

    if arguments.year and arguments.month:
        names_spreadsheets = [
            single_date.strftime(DATE_FORMAT)
            for single_date in date_range_in_month(arguments.year, arguments.month)
        ]

    start_date, end_date = None, None
    if arguments.end_date_of_day and arguments.start_date_of_day:
        start_date = datetime.strptime(arguments.start_date_of_day, DATE_FORMAT)
        end_date = datetime.strptime(arguments.end_date_of_day, DATE_FORMAT)
        names_spreadsheets = [
            single_date.strftime(DATE_FORMAT)
            for single_date in daterange(
                start_date,
                end_date
            )
        ]

    date = None
    if arguments.date:
        date = datetime.strptime(arguments.date, DATE_FORMAT)
        names_spreadsheets = [date.strftime(DATE_FORMAT)]

    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    status = 'No status'
    if arguments.year and arguments.month:
        status = f'{arguments.year} {arguments.month}'
    if arguments.end_date_of_day and arguments.start_date_of_day:
        status = f"From {start_date.strftime('%d.%m.%Y')} to {end_date.strftime('%d.%m.%Y')}"
    if arguments.date:
        status = f"Only {date.strftime('%d.%m.%Y')}"
    if arguments.name:
        status = f'Only {arguments.name}'

    manager = SpreadSheetManager()
    new_url = None
    try:
        new_url = check_spreadsheets_for_errors(manager, names_spreadsheets, status)
    except APIError:
        print('Ooops, problem with Google API, plz rerun this script a little bit later')
        return

    if new_url:
        print(new_url)
    else:
        print('\nNO ERRORS!')


if __name__ == '__main__':
    main()
