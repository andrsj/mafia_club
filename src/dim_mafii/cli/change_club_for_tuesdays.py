import os
from datetime import date

from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database
from dim_mafii.sheet_parser.client2 import SpreadSheetManager
from dim_mafii.domain.utils import daterange
from dim_mafii.domain.config import DATE_FORMAT

def main():
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)
    manager = SpreadSheetManager()

    start = date(day=1, month=1, year=2021)
    end = date(day=31, month=8, year=2021)
    dates = daterange(start, end)
    tuesdays = [d for d in dates if d.weekday() == 1]
    tuesdays_names = [d.strftime(DATE_FORMAT) for d in tuesdays]

    map_titles_id = manager.get_map_spreadsheets_id_by_names(tuesdays_names)

    if not map_titles_id:
        print('Not found ANY of these spreadsheets')

    for title in map_titles_id:
        spreadsheet = manager.get_spreadsheet_by_id(map_titles_id[title])
        print(title, '\n')

        spreadsheet_id = map_titles_id[title]
        spreadsheet = manager.get_spreadsheet_by_id(spreadsheet_id)
        worksheets = spreadsheet.worksheets()

        map_title_worksheet = {worksheet.title: worksheet for worksheet in worksheets}

        all_matrix: Dict[str: List[List]] = manager.get_matrix_from_sheet(spreadsheet)

        requests = []

        for blank_title in all_matrix:
            print(blank_title)
            print(all_matrix[blank_title][4][3])

            if all_matrix[blank_title][4][3] != 'Школа Мафії':
                print('Wrong club name will changed')
                requests.append(manager.create_body_request_for_marking_blank(
                    worksheet=map_title_worksheet[blank_title],
                    column=4,
                    row=5,
                    value='Школа Мафії'
                ))
            else:
                print('All ok')


        if requests:
            spreadsheet.batch_update(body={'requests': requests})


if __name__ == "__main__":
    main()