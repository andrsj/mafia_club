from dataclasses import dataclass
from datetime import timedelta, date, datetime
from calendar import monthrange
from typing import List, Dict, Optional
import argparse


from googleapiclient.discovery import Resource


from dim_mafii.domain.model import House, Game
from dim_mafii.domain.types import GameResult, ClassicRole

months = [
    'Січень',
    'Лютий',
    'Березень',
    'Квітень',
    'Травень',
    'Червень',
    'Липень',
    'Серпень',
    'Вересень',
    'Жовтень',
    'Листопад',
    'Грудень'
]


def get_houses_from_list_of_house_ids(houses: List[House], ids: List[str]) -> List[House]:
    return list(filter(lambda h: h.house_id in ids, houses))


def get_house_from_list_by_house_id(houses: List[House], house_id: str) -> Optional[House]:
    return next(filter(lambda h: h.house_id == house_id, houses), None)


def is_sheriff(house: House) -> bool:
    return house.role == ClassicRole.sheriff.value


def is_citizen(house: House) -> bool:
    return house.role in (ClassicRole.citizen.value, ClassicRole.sheriff.value)


def is_mafia(house: House) -> bool:
    return house.role in (ClassicRole.don.value, ClassicRole.mafia.value)


def is_mafia_win(game: Game) -> bool:
    return game.result == GameResult.mafia.value


def is_citizen_win(game: Game) -> bool:
    return game.result == GameResult.citizen.value


def get_spreadsheet_url(sheet_id: str):
    return f'https://docs.google.com/spreadsheets/d/{sheet_id}'


def get_folder_url(folder_id: str):
    return f'https://drive.google.com/drive/folders/{folder_id}'


def get_all_files_in_folder(api_files: Resource, folder_id) -> List[Dict]:
    response = api_files.list(q=f"parents = '{folder_id}'").execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = api_files.list(q=f'parents = {folder_id}', pageToken=nextPageToken).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')

    return files


def drive_file_list(files: Resource, fields: str = "files(id, mimeType, name, permissions), nextPageToken"):
    """
    Get list of files (with metadata) from Google Drive API
    Default: we check files metadata: id, type, name, permissions
    For response we check only files and pageToken for search
    """
    response = files.list(
        orderBy='name, folder',
        fields=fields
    ).execute()

    files_list = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = files.list(
            orderBy='name, folder',
            fields=fields,
            pageToken=nextPageToken
        ).execute()
        files_list.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')

    return files_list


def get_absolute_range(title):
    return f"'{title}'!A1:AC1001"


def get_submatrix(rows: List[List]) -> List[List]:
    max_len = len(max(rows, key=len))
    all_values = [row + [''] * (max_len - len(row)) for row in rows]
    return [row[1:12] for row in all_values[1:46]]


def get_url(url: str):
    """
    Change URL from API to people-like url

    Url for people
    https://docs.google.com/spreadsheets/d/1ysIAPo7f8yaP72YWjGqz8lcSjRlODgMta0b7fJOFU6g/edit#gid=1583237302

    A URL that was auto-generated by gspread for ez connect with API
    https://sheets.googleapis.com/v4/spreadsheets/1FAuYFo0RVulE65RnSuvDpwiRIW8PDqY14cqw-RhWGIA#gid=853153179

    """
    id_sheet = url.split('/')[-1]
    return f'https://docs.google.com/spreadsheets/d/{id_sheet}'


@dataclass
class EventHouseModel:
    day: int
    house_id: str


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def date_range_in_month(year, month):
    month = months.index(month)
    month_days = monthrange(year, month + 1)
    start_date = date(year, month + 1, 1)
    end_date = date(year, month + 1, month_days[1])

    return daterange(start_date, end_date)


def get_month(date_: date) -> str:
    # Get string month from date
    return months[date_.month - 1]


def get_the_specified_days_by_dates(start_date: datetime, end_date: datetime) -> List[datetime]:
    dates = daterange(start_date, end_date)
    # 1 - Tuesday, 4 - Friday
    return [one_date for one_date in dates if one_date.weekday() in [1, 4]]


def create_parser_for_blanks_checker():
    parser = argparse.ArgumentParser(description='Generate spreadsheets for new game in date range')

    parser.add_argument(
        '--name',
        dest='name',
        help='Searching by name'
    )
    parser.add_argument(
        '--month',
        dest='month',
        help='Month of blanks'
    )
    parser.add_argument(
        '--year',
        dest='year',
        help='Year of blanks',
        type=int
    )
    parser.add_argument(
        '--start',
        dest='start_date_of_day',
        help='Start date (format: DD/MM/YYYY)'
    )
    parser.add_argument(
        '--end',
        dest='end_date_of_day',
        help='End date (format: DD/MM/YYYY)'
    )
    parser.add_argument(
        '--date',
        dest='date',
        help='Spreadsheet by date (Text format DD/MM/YYYY)'
    )

    return parser


def create_parser_for_date_range():
    parser = argparse.ArgumentParser(description='Generate spreadsheets for new game in date range')

    parser.add_argument(
        '--start',
        dest='start_date_of_day',
        help='Start date (format: DD/MM/YYYY)'
    )
    parser.add_argument(
        '--end',
        dest='end_date_of_day',
        help='End date (format: DD/MM/YYYY)'
    )

    return parser


def create_parser_for_blank_feeling():
    parser = argparse.ArgumentParser(description='Parse data from spreadsheet and fill tables')

    parser.add_argument(
        '--no-check',
        dest='check',
        help='Argument for skipping check blanks',
        action='store_false'
    )

    parser.add_argument(
        '--month',
        dest='month',
        help='Parse all blanks in month'
    )
    parser.add_argument(
        '--year',
        dest='year',
        type=int,
        help='Choose year for parser'
    )

    parser.add_argument(
        '--start',
        dest='start_date_of_day',
        help='Start date (format: DD/MM/YYYY)'
    )
    parser.add_argument(
        '--end',
        dest='end_date_of_day',
        help='End date (format: DD/MM/YYYY)'
    )

    parser.add_argument(
        '--skip-ready',
        dest='ready',
        action='store_true',
        required=False,
        help='Skip ready worksheets'
    )

    parser.add_argument(
        "--sheet",
        dest='sheet_title',
        type=str,
        required=False
    )

    parser.add_argument(
        "--blank",
        dest='blank_title',
        type=str,
        required=False
    )

    parser.add_argument(
        '--full',
        default=False,
        dest='full',
        action='store_true',
        required=False,
        help='Parse and update full game'
    )
    parser.add_argument(
        '--games',
        default=False,
        dest='games',
        action='store_true',
        required=False,
        help="Parse and update game info"
    )
    parser.add_argument(
        '--houses',
        default=False,
        dest='houses',
        action='store_true',
        required=False,
        help="Parse and update houses info; Slot number. PLayer nick fouls and bonus marks"
    )
    parser.add_argument(
        "--best_moves",
        default=False,
        dest='best_moves',
        action='store_true',
        required=False,
        help="Parse and update best moves"
    )
    parser.add_argument(
        '--sheriff_versions',
        default=False,
        dest='sheriff_versions',
        action='store_true',
        required=False,
        help="Parse and update sheriff versions"
    )
    parser.add_argument(
        '--disqualifieds',
        default=False,
        dest='disqualifieds',
        action='store_true',
        required=False,
        help="Parse and update disqualifieds"
    )
    parser.add_argument(
        '--nominated_for_best',
        default=False,
        dest='nominated_for_best',
        action='store_true',
        required=False,
        help="Parse and update nominated for best"
    )
    parser.add_argument(
        '--voted',
        default=False,
        dest='voted',
        action='store_true',
        required=False,
        help="Parse and update voted"
    )
    parser.add_argument(
        '--kills',
        default=False,
        dest='kills',
        action='store_true',
        required=False,
        help='Parse and update kills'
    )
    parser.add_argument(
        '--misses',
        default=False,
        dest='misses',
        action='store_true',
        required=False,
        help='Parse and update misses'
    )
    parser.add_argument(
        '--don_checks',
        default=False,
        dest='don_checks',
        action='store_true',
        required=False,
        help='Parse and update don checks'
    )
    parser.add_argument(
        '--hand_of_mafia',
        default=False,
        dest='hand_of_mafia',
        action='store_true',
        required=False,
        help='Parse and update hand of mafia'
    )
    parser.add_argument(
        '--bonus_tolerant',
        default=False,
        dest='bonus_tolerant',
        action='store_true',
        required=False,
        help='Parse and update tolerant bonuses'
    )
    parser.add_argument(
        '--sheriff_checks',
        default=False,
        dest='sheriff_checks',
        action='store_true',
        required=False,
        help='Parse and update sheriff checks'
    )
    parser.add_argument(
        '--bonus_from_players',
        default=False,
        dest='bonus_from_players',
        action='store_true',
        required=False,
        help='Parse and update bonus from players'
    )
    parser.add_argument(
        '--bonus_from_heading',
        default=False,
        dest='bonus_from_heading',
        action='store_true',
        required=False,
        help='Parse and update bonus from heading'
    )
    parser.add_argument(
        '--devises',
        default=False,
        dest='devises',
        action='store_true',
        required=False,
        help='Parse and update devises'
    )
    parser.add_argument(
        '--breaks',
        default=False,
        dest='breaks',
        action='store_true',
        required=False,
        help='Parse and update breaks'
    )

    return parser