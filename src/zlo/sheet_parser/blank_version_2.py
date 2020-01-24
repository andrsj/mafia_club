import uuid

from zlo.domain.events import CreateOrUpdateGame
from zlo.domain.types import AdvancedGameResult

from zlo.domain.types import GameResult


class NotFinishedBlank(Exception):
    pass


class BlankParser:
    def __init__(self, matrix):
        self._matrix = matrix

    def parse_game_result(self):
        """
        Parse who win the game.
        If mafia win the game then check how mafia win this game
        If citizin win the game then check how citizen with this game
        :return: tuple(GameResult, AdvancedGameResult)
        """

        if self._matrix[1][8].value:
            game_result = GameResult.mafia
        elif self._matrix[0][8].value:
            game_result = GameResult.citizen
        else:
            raise NotFinishedBlank

        if game_result == GameResult.mafia:
            if self._matrix[4][6].value:
                advanced_game_result = AdvancedGameResult.three_on_three
            elif self._matrix[4][7].value:
                advanced_game_result = AdvancedGameResult.two_on_two
            else:
                advanced_game_result = AdvancedGameResult.one_on_one
        else:
            if self._matrix[4][9].value:
                advanced_game_result = AdvancedGameResult.clear_citizen
            else:
                advanced_game_result = AdvancedGameResult.guessing_game

        return game_result, advanced_game_result

    def parse_game_info(self) -> CreateOrUpdateGame:
        """
        Get general stats about game
        """
        game_result, advanced_game_result = self.parse_game_result()
        game_id = self._matrix[6][1].value or uuid.uuid4()
        return CreateOrUpdateGame(
            game_id=game_id,
            heading=self._matrix[1][1].value,
            date=self._matrix[0][1].value,
            club=self._matrix[3][1].value,
            tournament=self._matrix[4][1].value,
            table=self._matrix[4][4].value,
            result=game_result.value,
            advance_result=advanced_game_result.value
        )
        # return {
        #     "heading": self._matrix[1][1].value,
        #     "date": self._matrix[0][1].value,
        #     "club": self._matrix[3][1].value,
        #     "tournament": self._matrix[4][1].value,
        #     "table": self._matrix[4][4].value,
        #     "game_result": game_result,
        #     "game_result_advanced": advanced_game_result
        # }

    def parse_houses(self):
        pass

    def parse_kills(self):
        pass

    def parse_voted_list(self):
        pass

    def parse_sheriff_checks(self):
        pass

    def get_bonus_points_from_houses_data(self, houses_data=None):
        pass

    def get_bonus_tolerant_points_from_houses_data(self, houses_data=None):
        pass

    def parse_hand_of_mafia(self):
        pass

    def parse_devise(self):
        pass
