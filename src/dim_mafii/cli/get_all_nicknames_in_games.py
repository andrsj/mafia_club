import argparse


from gspread.models import Cell
from gspread.exceptions import SpreadsheetNotFound
from dim_mafii.sheet_parser.client import SpreadSheetClient
from dim_mafii.domain.utils import date_range_in_month, get_url
from dim_mafii.domain.config import DATE_FORMAT


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get all nicknames in blanks from all game spreadsheets')

    parser.add_argument(
        '--month',
        dest='month',
        help='Read all games for this month'
    )
    parser.add_argument(
        '--year',
        dest='year',
        type=int,
        help='Specify a right year'
    )

    # args.year [int], args.month [str (example: 'Жовтень')]
    arguments = parser.parse_args()

    name_sheets = [
        single_date.strftime(DATE_FORMAT)
        for single_date in date_range_in_month(arguments.year, arguments.month)
    ]

    client = SpreadSheetClient()

    # Dictionary -> url blank: worksheet [title + nicknames(heading + players)]
    all_blanks = {}

    for name in name_sheets:
        try:
            spreadsheet = client.client.open(name)

            for worksheet in spreadsheet.worksheets():
                matrix = client.get_matrix_for_one_worksheet(worksheet)

                # Heading [1] [2], other players: [10-19] [2]
                nicknames = [matrix[1][2]] + [matrix[i][2] for i in range(10, 20)]

                all_blanks[get_url(worksheet.url)] = {
                    'spreadsheet name': spreadsheet.title,
                    'worksheet name': worksheet.title,
                    'nicknames': nicknames
                }

        # Not found sheet by title 'DD/MM/YYYY'
        except SpreadsheetNotFound:
            continue

    # Generate cells with nicknames and url to blanks
    cells = []
    for column, url in enumerate(all_blanks, start=1):
        cells.append(Cell(
            row=1,
            col=column,
            value=url
        ))
        cells.append(Cell(
            row=2,
            col=column,
            value=all_blanks[url]['spreadsheet name']
        ))
        cells.append(Cell(
            row=3,
            col=column,
            value=all_blanks[url]['worksheet name']
        ))
        cells.append(Cell(
            row=4,
            col=column,
            value=all_blanks[url]['nicknames'][0]
        ))
        cells.append(Cell(
            row=5,
            col=column,
            value='Players:'
        ))
        for row, nickname in enumerate(all_blanks[url]['nicknames'][1:], start=6):
            cells.append(Cell(
                row=row,
                col=column,
                value=nickname
            ))

    spreadsheet_nicknames = client.client.open('Nicknames')
    worksheet_nicknames = spreadsheet_nicknames.add_worksheet(
        title=f'{arguments.month} - {arguments.year}',
        cols=100,
        rows=20
    )
    worksheet_nicknames.update_cells(cells)
    print('New list with nicknames by url:', get_url(worksheet_nicknames.url))
