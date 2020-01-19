from datetime import datetime


class CreateOrUpdateGame:
    game_id: str
    date: datetime
    result: int
    club: str
    table: int
    tournament: str
    heading: str
    advance_result: int