import datetime
from typing import List
from dateutil import parser

from zlo.domain.infrastructure import UnitOfWork, UnitOfWorkManager
from zlo.domain.model import Player, Game, House
from zlo.domain.types import HouseID, GameID


class FakePlayerRepo:
    players: List[Player] = []

    def add(self, player):
        self.players.append(player)

    def get_by_player_nickname(self, nick):
        for player in self.players:
            if player.nickname == nick:
                return player
        return None

    def get_by_id(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return player
        return None


class FakeGameRepo:
    games: List[Game] = []

    def add(self, game):
        self.games.append(game)

    def get_by_game_id(self, game_id):
        for game in self.games:
            if game.game_id == game_id:
                return game
        return None

    def get_by_datetime_range(self, start_date: datetime.datetime, end_date: datetime.datetime):
        print(self.games)
        return [game for game in self.games if start_date < game.date < end_date]


class FakeHouseRepo:
    houses: List[House] = []

    def add(self, house: House):
        self.houses.append(house)

    def get_by_house_id(self, house_id: HouseID):
        for house in self.houses:
            if house.house_id == house_id:
                return house
        return None

    def get_by_game_id(self, game_id: GameID):
        return [house for house in self.houses if house.game_id == game_id]


class FakeUnitOfWork(UnitOfWork):

    def __init__(self):
        self.games = FakeGameRepo()
        self.houses = FakeHouseRepo()
        self.players = FakePlayerRepo()
        self.committed = False
        self.rolled_back = False
        self.flushed = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def flush(self):
        self.flushed = True


class FakeUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self):
        self.sess = FakeUnitOfWork()

    def clear_committed_flag(self):
        self.sess.committed = False

    def start(self):
        return self.sess