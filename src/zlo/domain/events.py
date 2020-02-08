from dataclasses import dataclass
from datetime import datetime


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
#
# @dataclass
# class BestMove:
#     game_id:
