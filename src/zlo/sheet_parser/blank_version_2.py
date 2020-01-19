from gspread import Worksheet
from zlo.domain.types import GameResult, AdvancedGameResult
import numpy
import logging
import os
import time
import uuid
from pprint import pprint
from typing import List

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.cli.auth import auth
from zlo.cli.exceptions import UnknownPlayer
from zlo.cli.zlo_logger import get_logger
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Game, House, BestMove
from zlo.domain.types import GameResult, ClassicRole
from dateutil import parser


class NotFinishedBlank(Exception):
    pass


class BlankParser:
    def __init__(self, work_sheet: Worksheet):
        self._ws = work_sheet
        self._game_data = self._ws.range('B2:K46')
        self._matrix = numpy.asarray(self._game_data).reshape(45, 10)

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

    def parse_game_info(self):
        """
        Get general stats about game
        """
        game_result, advanced_game_result = self.parse_game_result()
        return {
            "heading": self._matrix[1][1].value,
            "date": self._matrix[0][1].value,
            "club": self._matrix[3][1].value,
            "tournament": self._matrix[4][1].value,
            "table": self._matrix[4][4].value,
            "game_result": game_result,
            "game_result_advanced": advanced_game_result
        }

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

    def parse_game_info(self):
        pass

    def parse_hand_of_mafia(self):
        pass

    def parse_devise(self):
        pass