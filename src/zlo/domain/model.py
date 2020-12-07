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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                self.date == other.date,
                self.result == other.result,
                self.club == other.club,
                self.table == other.table,
                self.tournament == other.tournament,
                self.heading == other.heading,
                self.advance_result == other.advance_result
            )
        )


@dataclass
class House:
    house_id: HouseID
    player_id: PlayerID
    role: ClassicRole
    slot: int
    game_id: GameID
    bonus_mark: float
    fouls: int

    def update_bonus_mark(self, bonus_mark: float):
        self.bonus_mark = bonus_mark

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.player_id) == str(other.player_id),
                str(self.game_id) == str(other.game_id),
                self.role == other.role,
                self.slot == other.slot,
                self.bonus_mark == other.bonus_mark,
                self.fouls == other.fouls
            )
        )


@dataclass
class BestMove:
    best_move_id: BestMoveID
    game_id: GameID
    killed_house: HouseID
    best_1: Optional[HouseID]
    best_2: Optional[HouseID]
    best_3: Optional[HouseID]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.killed_house) == str(other.killed_house),
                str(self.best_1) == str(other.best_1),
                str(self.best_2) == str(other.best_2),
                str(self.best_3) == str(other.best_3)
            )
        )


@dataclass
class Disqualified:
    disqualified_id: DisqualifiedID
    game_id: GameID
    house: HouseID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house) == str(other.house)
            )
        )


@dataclass
class SheriffVersion:
    sheriff_version_id: SheriffVersionID
    game_id: GameID
    house: HouseID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house) == str(other.house)
            )
        )


@dataclass
class NominatedForBest:
    nominated_for_best_id: NominatedForBestID
    game_id: GameID
    house: HouseID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house) == str(other.house)
            )
        )


@dataclass
class Devise:
    devise_id: DeviseID
    game_id: GameID
    killed_house: HouseID
    house_1: Optional[HouseID]
    house_2: Optional[HouseID]
    house_3: Optional[HouseID]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.killed_house) == str(other.killed_house),
                str(self.house_1) == str(other.house_1),
                str(self.house_2) == str(other.house_2),
                str(self.house_3) == str(other.house_3)
            )
        )


@dataclass
class HandOfMafia:
    hand_of_mafia_id: HandOfMafiaID
    game_id: GameID
    house_hand_id: HouseID
    victim_id: Optional[HouseID]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house_hand_id) == str(other.house_hand_id),
                str(self.victim_id) == str(other.victim_id)
            )
        )


@dataclass
class BonusTolerantFromPlayers:
    bonus_id: str
    game_id: GameID
    house_from_id: HouseID
    house_to_id: HouseID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house_to_id) == str(other.house_to_id),
                str(self.house_from_id) == str(other.house_from_id)
            )
        )


@dataclass
class Kills:
    kill_id: str
    game_id: GameID
    killed_house_id: HouseID
    circle_number: int

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.killed_house_id) == str(other.killed_house_id),
                self.circle_number == other.circle_number
            )
        )


@dataclass
class Voted:
    voted_id: str
    game_id: GameID
    house_id: HouseID
    day: int

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house_id) == str(other.house_id),
                self.day == other.day
            )
        )


@dataclass
class SheriffChecks:
    sheriff_check_id: str
    game_id: GameID
    checked_house_id: Optional[HouseID]
    circle_number: int

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.checked_house_id) == str(other.checked_house_id),
                self.circle_number == other.circle_number
            )
        )


@dataclass
class DonChecks:
    don_check_id: str
    game_id: GameID
    checked_house_id: Optional[HouseID]
    circle_number: int

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                self.circle_number == other.circle_number,
                str(self.checked_house_id) == str(other.checked_house_id)
            )
        )


@dataclass
class Misses:
    miss_id: str
    game_id: GameID
    house_id: Optional[HouseID]
    circle_number: int

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house_id) == str(other.house_id),
                self.circle_number == other.circle_number
            )
        )


@dataclass
class BonusFromPlayers:
    bonus_id: str
    game_id: GameID
    bonus_from: Optional[HouseID]
    bonus_to: Optional[HouseID]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.bonus_from) == str(other.bonus_from),
                str(self.bonus_to) == str(other.bonus_to)
            )
        )
