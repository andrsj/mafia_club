import os
from datetime import datetime
from time import sleep
from typing import Dict, List

from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database
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

    manager = SpreadSheetManager()

    map_spreadsheets_name_ids = manager.get_map_spreadsheets_id_by_names(names_spreadsheets)
    if not map_spreadsheets_name_ids:
        print('Not found ANY of these spreadsheets')

    for spreadsheet_title in map_spreadsheets_name_ids:
        print(spreadsheet_title, '\n')

        spreadsheet_id = map_spreadsheets_name_ids[spreadsheet_title]
        spreadsheet = manager.get_spreadsheet_by_id(spreadsheet_id)
        worksheets = spreadsheet.worksheets()

        map_title_worksheet = {worksheet.title: worksheet for worksheet in worksheets}

        all_matrix: Dict[str: List[List]] = manager.get_matrix_from_sheet(spreadsheet)

        requests = []

        for blank_title in all_matrix:
            print(blank_title)
            print(all_matrix[blank_title][4][3])

            if all_matrix[blank_title][4][3] in ('Зло', 'ZLO'):
                print('Change', all_matrix[blank_title][4][3], 'on Дім Мафії')
                requests.append(manager.create_body_request_for_marking_blank(
                    worksheet=map_title_worksheet[blank_title],
                    column=4,
                    row=5,
                    value='Дім Мафії'
                ))
            elif all_matrix[blank_title][4][3] in ('Школа Дім Мафії', 'Школа Зло', 'Школа Дому Мафії'):
                print('Change', all_matrix[blank_title][4][3], 'on Школа Мафії')
                requests.append(manager.create_body_request_for_marking_blank(
                    worksheet=map_title_worksheet[blank_title],
                    column=4,
                    row=5,
                    value='Школа Мафії'
                ))
            else:
                print('Nothing:', all_matrix[blank_title][4][3])

        if requests:
            spreadsheet.batch_update(body={'requests': requests})


if __name__ == '__main__':
    main()
