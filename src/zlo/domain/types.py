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
class PlayerResult:
    nickname: str
    games_number: int = 1
    wins_count: int = 0
    bonus_marks: float = 0
    bonus_mark_number: int = 0
    best_moves_marks: float = 0
    best_moves_number: int = 0

    def update_by_new_result(self, new_result: PlayerResult):
        if self.nickname != new_result.nickname:
            raise TypeError(f" {self} and {new_result} is for different players")

        self.games_number += new_result.games_number
        self.wins_count += new_result.wins_count
        self.bonus_marks += new_result.bonus_marks
        self.bonus_mark_number += new_result.bonus_mark_number
        self.best_moves_marks += new_result.best_moves_marks
        self.best_moves_number += new_result.best_moves_number

    def calculate_win_rate(self):
        if self.games_number == 0:
            self.win_rate = 0
            self.middle_best_moves = 0
            self.middle_mark_on_game = 0
            self.middle_bonus_mark = 0
        self.win_rate = (self.wins_count * 100) / self.games_number
        self.middle_mark_on_game = (self.bonus_marks + self.best_moves_marks + self.wins_count) / self.games_number
        self.middle_bonus_mark = (self.bonus_marks + self.best_moves_marks) / self.games_number
        self.middle_best_moves = (self.best_moves_marks / self.best_moves_number) if self.best_moves_number else 0

    def get_repr_of_stats(self):
        return f"{self.nickname} Кількість ігор {self.games_number}; Кількість Перемог {self.wins_count};" \
               f" Вінрейт {int(self.win_rate)}% Середній бал за гру {round(self.middle_mark_on_game, 2)}; " \
               f" Кількість кращих ходів {self.best_moves_number }" \
               f" Середній бонус за кращий хід {round(self.middle_best_moves, 2)}"


def check_winner(game_result: GameResult, game_role: ClassicRole) -> bool:
    game_result = GameResult(game_result)
    game_role = ClassicRole(game_role)
    if game_result == game_result.citizen and game_role in (ClassicRole.citizen, ClassicRole.sheriff):
        return True
    if game_result == game_result.mafia and game_role in (ClassicRole.mafia, ClassicRole.don):
        return True
    return False
