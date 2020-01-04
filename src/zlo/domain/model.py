import datetime
import uuid
from dataclasses import dataclass
from typing import Optional

from zlo.domain.types import GameResult, GameID, HouseID, PlayerID, ClassicRole, ClubID, TournamentID


class Player:

    def __init__(self, nickname: str, name: str, club: str, player_id: PlayerID = None):
        self.nickname = nickname
        self.name = name
        self.club = club
        self.id = player_id if player_id else str(uuid.uuid4())

    def __repr__(self):
        return f"Player({self.nickname})"


@dataclass
class Game:
    game_id: GameID
    date: datetime.datetime
    result: Optional[GameResult]
    club: Optional[ClubID]
    table: Optional[int]
    tournament: Optional[TournamentID]
    heading: Player

    def update_game_result(self, result):
        self.result = result


@dataclass
class House:
    house_id: HouseID
    player_id: PlayerID
    role: ClassicRole
    slot: int
    game_id: GameID
    bonus_mark: float = 0
    fouls: int = 0

    def update_bonus_mark(self, bonus_mark: float):
        self.bonus_mark = bonus_mark
