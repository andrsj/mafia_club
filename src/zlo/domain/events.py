from dataclasses import dataclass
from datetime import datetime

from zlo.domain.types import ClassicRole


@dataclass
class CreateOrUpdateGame:
    game_id: str
    date: datetime
    result: int
    club: str
    table: int
    tournament: str
    heading: str
    advance_result: int


@dataclass
class CreateOrUpdateHouse:
    game_id: str
    player_nickname: str
    role: ClassicRole
    slot: int
    bonus_mark: float
    fouls: int
