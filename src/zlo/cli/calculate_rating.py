import os
from typing import Dict, List
from datetime import datetime


import inject
from gspread.models import Cell


from zlo.adapters.bootstrap import bootstrap
from zlo.adapters.orm import SqlAlchemyUnitOfWork
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.domain.model import Game
from zlo.domain.types import Result
from zlo.domain.utils import create_parser_for_date_range
from zlo.domain.config import DATA_FORMAT
from zlo.cli.setup_env_for_test import setup_env_with_test_database


class RatingCalculator:

    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self.uow = uow

    def rating_for_all_games(self) -> Dict[str, Result]:
        all_games = self.uow.games.get_all_games()
        if not all_games:
            return {}
        rating = self._calculate_ratings_for_games(all_games)
        return rating

    def rating_in_daterange(self, start_date: datetime, end_date: datetime) -> Dict[str, Result]:
        filtered_games = self.uow.games.get_by_datetime_range(start_date, end_date)
        if not filtered_games:
            return {}
        rating = self._calculate_ratings_for_games(filtered_games)
        return rating

    def rating_by_club(self, nameclub) -> Dict[str, Result]:
        filtered_games_by_name_club = self.uow.games.get_by_name_club(nameclub)
        if not filtered_games_by_name_club:
            return {}
        rating = self._calculate_ratings_for_games(filtered_games_by_name_club)
        return rating

    def _calculate_ratings_for_games(self, games: List[Game]) -> Dict[str, Result]:
        statistic: Dict[str, Result] = {}
        for game in games:

            # Get results from one game
            result_per_game = self._calculate_rating_per_game(game)
            for player_id, result in result_per_game.items():

                # Push results in general result
                if player_id in statistic:
                    statistic[player_id].update(result)
                else:
                    statistic[player_id] = result

        return statistic

    def _calculate_rating_per_game(self, game: Game) -> Dict[str, Result]:
        game_stats: Dict[str, Result] = {}

        houses = self.uow.houses.get_by_game_id(game.game_id)

        # Additional info for statistic
        best_move = self.uow.best_moves.get_by_game_id(game.game_id)
        misses = self.uow.misses.get_by_game_id(game.game_id)

        # Code below: don's attempts to find the sheriff
        first_night_don_check, first_two_nights_don_check = False, False
        sheriff_house = next((house for house in houses if house.role == 2), None)

        if sheriff_house is not None:
            don_checks = self.uow.don_checks.get_by_game_id(game.game_id)
            for don_check in don_checks:
                # First night and find sheriff
                first_night_don_check = (
                    don_check.circle_number == 1
                    and don_check.checked_house_id == sheriff_house.house_id
                )
                # First two nights and find sheriff
                first_two_nights_don_check = (
                    don_check.circle_number in (1, 2)
                    and don_check.checked_house_id == sheriff_house.house_id
                )
            # End done checks code block

        # Generate resultats for every player in one game
        for house in houses:
            winner = Result.check_winner(game_result=game.result, game_role=house.role)
            game_stats[house.player_id] = Result(
                player_uuid=house.player_id,  # Nickname
                games_count=1,
                wins_count=int(winner),

                games_don=1 if house.role == 3 else 0,  # Games with done card
                games_mafia=1 if house.role == 1 else 0,  # mafia card
                games_sheriff=1 if house.role == 2 else 0,  # sheriff
                games_citizen=1 if house.role == 0 else 0,  # citizen

                wins_don=1 if house.role == 3 and winner else 0,  # Wins
                wins_mafia=1 if house.role == 1 and winner else 0,
                wins_sheriff=1 if house.role == 2 and winner else 0,
                wins_citizen=1 if house.role == 0 and winner else 0,

                win_one_on_one=1 if game.advance_result == 3 and winner else 0,  # Advanced results
                win_two_on_two=1 if game.advance_result == 2 and winner else 0,
                win_three_on_three=1 if game.advance_result == 1 and winner else 0,
                win_clear_citizen=1 if game.advance_result == 4 and winner else 0,
                win_guessing_game=1 if game.advance_result == 5 and winner else 0,

                first_death=1 if best_move and best_move.killed_house == house.house_id else 0,  # First death at game statistic
                first_death_sheriff=1 if best_move and best_move.killed_house == house.house_id and house.role == 2 else 0,

                don_find_sheriff_in_first_night=int(first_night_don_check),  # Don check sheriff
                don_find_sheriff_in_two_first_night=int(first_two_nights_don_check),

                misses_in_game=house.house_id in [miss.house_id for miss in misses]
                # One miss for one game from all games
            )

        return game_stats


if __name__ == '__main__':
    parser = create_parser_for_date_range()
    arguments = parser.parse_args()

    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    uowm = inject.instance(UnitOfWorkManager)
    client = inject.instance(SpreadSheetClient)

    with uowm.start() as tx:
        calculator = RatingCalculator(tx)
        results = None
        if not (arguments.start_date_of_day and arguments.end_date_of_day):
            results = calculator.rating_for_all_games()
        if arguments.start_date_of_day and arguments.end_date_of_day:
            results = calculator.rating_in_daterange(
                datetime.strptime(arguments.start_date_of_day, DATA_FORMAT),
                datetime.strptime(arguments.end_date_of_day, DATA_FORMAT)
            )

        sheet = client.client.open(title='Statistic')
        players = tx.players.all()
        time_now = datetime.now()

        attribute_mapper = {
            'player_uuid': 'Nickname',
            'games_count': 'Кількість ігор',
            'wins_count': 'Перемоги',
            'win_rate': 'Процент перемог',
            'games_citizen': 'Ігри за мирного',
            'wins_citizen': 'Перемоги',
            'win_rate_citizen': 'Процент перемог',
            'games_mafia': 'Ігри за мафію (М)',
            'wins_mafia': 'Перемоги (М)',
            'win_rate_mafia': 'Процент перемог (М)',
            'games_don': 'Ігри за дона (Д)',
            'wins_don': 'Перемоги (Д)',
            'win_rate_don': 'Процент перемог (Д)',
            'games_sheriff': 'Ігри за шерифа (Ш)',
            'wins_sheriff': 'Перемоги (Ш)',
            'win_rate_sheriff': 'Процент перемог (Ш)',
            'win_three_on_three': 'Перемоги 3в3',
            'win_two_on_two': 'Перемоги 2в2',
            'win_one_on_one': 'Перемоги 1в1',
            'win_clear_citizen': 'Чисті перемоги',
            'win_guessing_game': 'Угадайки',
            'first_death': 'Перша смерть',
            'first_death_sheriff': 'Перша смерть (Ш)',
            'don_find_sheriff_in_first_night': 'Дон знайшов шерифа в першу ніч',
            'don_find_sheriff_in_two_first_night': 'Дон знайшов шерифа в перші дві ночі'
        }

        name_worksheet = f"Range [{arguments.start_date_of_day} - {arguments.end_date_of_day}] "\
                         + time_now.strftime('%d-%m-%Y %H:%M:%S') \
                         if arguments.start_date_of_day and arguments.end_date_of_day \
                         else 'All ' + time_now.strftime('%d-%m-%Y %H:%M:%S')

        worksheet = sheet.add_worksheet(
            name_worksheet,
            cols=len(attribute_mapper),
            rows=len(players)
        )

        cells = [Cell(1, col, value) for col, value in enumerate(attribute_mapper.values(), start=1)]
        for row, player_uuid in enumerate(results, start=2):
            for col, attribute in enumerate(list(attribute_mapper.keys())[1:], start=2):  # [1:] - skip player UUID
                cells.append(Cell(row, col, getattr(results[player_uuid], attribute)))

            # Use nickname (no UUID)
            cells.append(
                Cell(
                    row,
                    1,
                    [player for player in players if player.player_id == player_uuid][0].nickname.capitalize()
                )
            )

        worksheet.update_cells(cells)

        # Autofit cell width by len of max strings in column
        sheet.batch_update(body={
            'requests': [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(attribute_mapper)
                        }
                    }
                }
            ]
        })

        print(sheet.url)
