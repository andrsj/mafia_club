import datetime
from typing import List, Dict

from zlo.domain.infrastructure import UnitOfWork, UnitOfWorkManager, CacheMemory
from zlo.domain.model import Player, Game, House, Voted
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
            if player.player_id == player_id:
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


class FakeVotedRepo:
    voted: List[Voted] = []

    def add(self, voted: Voted):
        self.voted.append(voted)

    def delete(self, voted: Voted):
        self.voted.remove(voted)

    def get_by_game_id(self, game_id: GameID):
        return [voted for voted in self.voted if voted.game_id == game_id]

    def get_by_game_id_and_days(self, game_id: GameID, day: int):
        return [
            voted for voted in self.voted
            if voted.game_id == game_id and voted.voted_day == day
        ]

class FakeUnitOfWork(UnitOfWork):

    def __init__(self):
        self.games = FakeGameRepo()
        self.houses = FakeHouseRepo()
        self.players = FakePlayerRepo()
        self.voted = FakeVotedRepo()
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


class FakeHouseCacheMemory(CacheMemory):
    cache: Dict[GameID, Dict[int, House]] = {}

    def __init__(self, uowm: FakeUnitOfWorkManager):
        self._uowm = uowm

    def get_by_game_id_from_cache(self, game_id: GameID) -> Dict[int, House]:
        if not self.__check_data_by_game_id_in_cache(game_id):
            self.__get_by_game_id_from_db(game_id)
        return self.cache[game_id]

    def __get_by_game_id_from_db(self, game_id: GameID):
        houses = self._uowm.sess.houses.get_by_game_id(game_id)
        self.cache[game_id] = {house.slot: house for house in houses}

    def __check_data_by_game_id_in_cache(self, game_id: GameID):
        return game_id in self.cache
