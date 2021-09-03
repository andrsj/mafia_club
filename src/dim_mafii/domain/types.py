from __future__ import annotations

import enum
from dataclasses import dataclass

HouseID = str
GameID = str
PlayerID = str
ClubID = str
TournamentID = str
BestMoveID = str
DeviseID = str
HandOfMafiaID = str
DisqualifiedID = str
SheriffVersionID = str
NominatedForBestID = str


class ClassicRole(enum.Enum):
    citizen = 0
    mafia = 1
    sheriff = 2
    don = 3


class GameResult(enum.Enum):
    unfinished = 0
    citizen = 1
    mafia = 2


class AdvancedGameResult(enum.Enum):
    three_on_three = 1
    two_on_two = 2
    one_on_one = 3
    clear_citizen = 4
    guessing_game = 5


class Fouls(enum.Enum):
    zero = 0
    one = 1
    two = 2
    three = 3
    four = 4
    disqualification = 5


class BonusForBestMove(enum.Enum):
    full = 0.4
    half = 0.2


@dataclass
class Result:
    player_uuid: str
    games_count: int
    wins_count: int

    @property
    def win_rate(self):
        return round(self.wins_count / self.games_count * 100, 2)

    games_citizen: int
    games_mafia: int
    games_don: int
    games_sheriff: int

    wins_citizen: int
    wins_mafia: int
    wins_don: int
    wins_sheriff: int

    @property
    def win_rate_citizen(self):
        return round(self.wins_citizen / self.games_citizen * 100, 2) if self.games_citizen > 0 else 0

    @property
    def win_rate_mafia(self):
        return round(self.wins_mafia / self.games_mafia * 100, 2) if self.games_mafia > 0 else 0

    @property
    def win_rate_don(self):
        return round(self.wins_don / self.games_don * 100, 2) if self.games_don > 0 else 0

    @property
    def win_rate_sheriff(self):
        return round(self.wins_sheriff / self.games_sheriff * 100, 2) if self.games_sheriff > 0 else 0

    win_three_on_three: int
    win_two_on_two: int
    win_one_on_one: int
    win_clear_citizen: int
    win_guessing_game: int

    first_death: int
    first_death_sheriff: int

    don_find_sheriff_in_first_night: int
    don_find_sheriff_in_two_first_night: int

    misses_in_game: int

    def update(self, new_result: Result):
        if new_result.player_uuid != self.player_uuid:
            raise TypeError(f"[{self.__class__}]: {new_result} is for different players")
        self.games_count += new_result.games_count
        self.wins_count += new_result.wins_count

        self.games_citizen += new_result.games_citizen
        self.games_mafia += new_result.games_mafia
        self.games_don += new_result.games_don
        self.games_sheriff += new_result.games_sheriff

        self.wins_citizen += new_result.wins_citizen
        self.wins_mafia += new_result.wins_mafia
        self.wins_don += new_result.wins_don
        self.wins_sheriff += new_result.wins_sheriff

        self.win_three_on_three += new_result.win_three_on_three
        self.win_two_on_two += new_result.win_two_on_two
        self.win_one_on_one += new_result.win_one_on_one
        self.win_clear_citizen += new_result.win_clear_citizen
        self.win_guessing_game += new_result.win_guessing_game

        self.first_death += new_result.first_death
        self.first_death_sheriff += new_result.first_death_sheriff

        self.don_find_sheriff_in_first_night += new_result.don_find_sheriff_in_first_night
        self.don_find_sheriff_in_two_first_night += new_result.don_find_sheriff_in_two_first_night

        self.misses_in_game += new_result.misses_in_game

    @staticmethod
    def check_winner(game_result, game_role) -> bool:
        game_result = GameResult(game_result)
        game_role = ClassicRole(game_role)
        if game_result == game_result.citizen and game_role in (ClassicRole.citizen, ClassicRole.sheriff):
            return True
        if game_result == game_result.mafia and game_role in (ClassicRole.mafia, ClassicRole.don):
            return True
        return False


@dataclass
class BlankError:
    spreadsheet_name: str
    worksheet_name: str
    information: str
    heading: str
    worksheet_url: str
