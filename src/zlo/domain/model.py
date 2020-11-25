import datetime
import uuid
from dataclasses import dataclass
from typing import Optional

from zlo.domain.types import (
    GameID,
    HouseID,
    PlayerID,
    ClassicRole,
    ClubID,
    TournamentID,
    BestMoveID,
    DeviseID,
    HandOfMafiaID,
    SheriffVersionID,
    DisqualifiedID,
    NominatedForBestID
)


@dataclass
class Player:

    def __init__(self, nickname: str, name: str, club: str, player_id: PlayerID = None):
        self.nickname = nickname
        self.name = name
        self.club = club
        self.player_id = player_id if player_id else str(uuid.uuid4())

    def __repr__(self):
        return f"Player({self.nickname})"

    def as_dict(self):
        return {
            "player_id": str(self.player_id),
            "name": self.name,
            "nickname": self.nickname,
            "club": self.club
        }


@dataclass
class Game:
    game_id: GameID
    date: datetime.datetime
    result: int
    club: Optional[ClubID]
    table: Optional[int]
    tournament: Optional[TournamentID]
    heading: Player
    advance_result: int

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


@dataclass
class BestMove:
    best_move_id: BestMoveID
    game_id: GameID
    killed_house: HouseID
    best_1: Optional[HouseID]
    best_2: Optional[HouseID]
    best_3: Optional[HouseID]


@dataclass
class Disqualified:
    disqualified_id: DisqualifiedID
    game_id: GameID
    house: HouseID


@dataclass
class SheriffVersion:
    sheriff_version_id: SheriffVersionID
    game_id: GameID
    house: HouseID


@dataclass
class NominatedForBest:
    nominated_for_best_id: NominatedForBestID
    game_id: GameID
    house: HouseID


@dataclass
class Devise:
    devise_id: DeviseID
    game_id: GameID
    killed_house: HouseID
    house_1: Optional[HouseID]
    house_2: Optional[HouseID]
    house_3: Optional[HouseID]


@dataclass
class HandOfMafia:
    hand_of_mafia_id: HandOfMafiaID
    game_id: GameID
    house_hand_id: HouseID
    victim_id: Optional[HouseID]


@dataclass
class BonusTolerantPointFromPlayers:
    bonus_tolerant_point_id: str
    game_id: GameID
    house_from_id: HouseID
    house_to_id: HouseID


@dataclass
class Kills:
    kill_id: str
    game_id: GameID
    killed_house_id: HouseID
    circle_number: int


@dataclass
class Voted:
    voted_id: str
    game_id: GameID
    house_id: HouseID
    day: int


@dataclass
class SheriffChecks:
    sheriff_checks_id: str
    game_id: GameID
    checked_house_id: Optional[HouseID]
    circle_number: int


@dataclass
class DonChecks:
    don_checks_id: str
    game_id: GameID
    checked_house_id: Optional[HouseID]
    circle_number: int


@dataclass
class BonusFromPlayers:
    bonus_id: str
    game_id: GameID
    bonus_from: Optional[HouseID]
    bonus_to: Optional[HouseID]
