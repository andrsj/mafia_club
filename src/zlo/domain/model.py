import datetime
from dataclasses import dataclass
from typing import Optional

from zlo.domain.types import GameResult


class Player:

    def __init__(self, nickname, name, club):
        self.nickname = nickname
        self.name = name
        self.club = club

    def __repr__(self):
        return f"Player({self.nickname})"


@dataclass
class Game:
    id: str
    date: datetime.datetime
    result: Optional[GameResult]
    heading: Player

    def update_game_result(self, result):
        self.result = result
