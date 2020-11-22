import datetime
from typing import List, Dict


from zlo.domain.model import Player, Game, House, BestMove, HandOfMafia, Kills
from zlo.domain.infrastructure import UnitOfWork, UnitOfWorkManager, HouseCacheMemory
from zlo.domain.model import Player, Game, House, Voted
from zlo.domain.types import HouseID, GameID


class FakePlayerRepo:
    players: List[Player] = []

    def add(self, player: Player):
        self.players.append(player)

    def get_by_nickname(self, nick):
        for player in self.players:
            if player.nickname == nick:
                return player
        return None

    def get_by_id(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def clean(self):
        self.players = []


class FakeGameRepo:
    games: List[Game] = []

    def add(self, game: Game):
        self.games.append(game)

    def get_by_game_id(self, game_id):
        for game in self.games:
            if game.game_id == game_id:
                return game
        return None

    def get_by_datetime_range(self, start_date: datetime.datetime, end_date: datetime.datetime):
        return [game for game in self.games if start_date < game.date < end_date]

    def clean(self):
        self.games = []


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

    def get_by_game_id_and_slot(self, game_id: GameID, slot: int):
        for house in self.houses:
            if house.game_id == game_id and house.slot == slot:
                return house
        return None

    def clean(self):
        self.houses = []


class FakeBestMoveRepo:
    best_moves: Dict[GameID, BestMove] = {}

    def add(self, best_move: BestMove):
        self.best_moves[best_move.game_id] = best_move

    def get_by_game_id(self, game_id: GameID):
        return self.best_moves.get(game_id)

    def clean(self):
        self.best_moves = {}


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
            if voted.game_id == game_id and voted.day == day
        ]

    def clean(self):
        self.voted = []


class FakeHandOfMafiaRepo:
    hands_of_mafia: Dict[GameID, HandOfMafia] = {}

    def add(self, hand_of_mafia: HandOfMafia):
        self.hands_of_mafia[hand_of_mafia.game_id] = hand_of_mafia

    def get_by_game_id(self, game_id: GameID):
        return self.hands_of_mafia.get(game_id)

    def clean(self):
        self.hands_of_mafia = {}


class FakeKillRepo:
    kills: List[Kills] = []

    def add(self, kill: Kills):
        self.kills.append(kill)

    def get_by_game_id(self, game_id: GameID) -> List[Kills]:
        return [kill for kill in self.kills if kill.game_id == game_id]


class FakeUnitOfWork(UnitOfWork):

    def __init__(self):
        self.games = FakeGameRepo()
        self.houses = FakeHouseRepo()
        self.players = FakePlayerRepo()
        self.kills = FakeKillRepo()
        self.best_moves = FakeBestMoveRepo()
        self.hand_of_mafia = FakeHandOfMafiaRepo()
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

    def clean_all(self):
        self.games.clean()
        self.houses.clean()
        self.players.clean()
        self.voted.clean()
        self.best_moves.clean()
        self.hand_of_mafia.clean()


class FakeUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self):
        self.sess = FakeUnitOfWork()

    def clear_committed_flag(self):
        self.sess.committed = False

    def start(self):
        return self.sess


class FakeHouseCacheMemory(HouseCacheMemory):
    cache: Dict[GameID, Dict[int, House]] = {}

    def get_houses_by_game_id(self, game_id: GameID) -> Dict[int, House]:
        return self.cache.get(game_id)

    def add_houses_by_game(self, game_id: GameID, houses: List[House]):
        self.cache[game_id] = {house.slot: house for house in houses}

    def clean(self):
        self.cache = {}
