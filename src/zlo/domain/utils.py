from dataclasses import dataclass
from datetime import timedelta, date, datetime
from calendar import monthrange
from typing import List
import argparse

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

def create_parser_for_blank_generation():
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


    return parser
