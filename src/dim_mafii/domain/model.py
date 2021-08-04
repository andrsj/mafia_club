import datetime
import uuid
from dataclasses import dataclass, field
from typing import Optional, List

from dim_mafii.domain import types


@dataclass
class Player:

    def __init__(self, nickname: str, name: str, club: str, displayname: str = None, player_id: types.PlayerID = None):
        self.nickname = nickname
        self.name = name
        self.club = club
        self.player_id = player_id if player_id else str(uuid.uuid4())
        self.displayname = displayname or nickname

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
    game_id: types.GameID
    date: datetime.datetime
    result: int
    club: Optional[types.ClubID]
    table: Optional[int]
    tournament: Optional[types.TournamentID]
    heading: Player
    advance_result: int
    calculated: bool = False

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
                self.advance_result == other.advance_result,
                self.calculated == other.calculated
            )
        )

    def __str__(self):
        return f"Game:\n" \
               f"\tResult: {self.result}    Club: {self.club}\n" \
               f"\tTable: {self.table}    Heading: {self.heading}\n" \
               f"\tDate: {self.date}"


@dataclass
class House:
    house_id: types.HouseID
    player_id: types.PlayerID
    role: types.ClassicRole
    slot: int
    game_id: types.GameID
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

    def __hash__(self):
        return hash((self.house_id, self.player_id, self.role, self.slot, self.game_id))


@dataclass
class BestMove:
    best_move_id: types.BestMoveID
    game_id: types.GameID
    killed_house: types.HouseID
    best_1: Optional[types.HouseID]
    best_2: Optional[types.HouseID]
    best_3: Optional[types.HouseID]

    @property
    def choosen_houses(self):
        return self.best_1, self.best_2, self.best_3

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
    disqualified_id: types.DisqualifiedID
    game_id: types.GameID
    house: types.HouseID

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
    sheriff_version_id: types.SheriffVersionID
    game_id: types.GameID
    house: types.HouseID

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
    nominated_for_best_id: types.NominatedForBestID
    game_id: types.GameID
    house: types.HouseID

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
    devise_id: types.DeviseID
    game_id: types.GameID
    killed_house: types.HouseID
    house_1: Optional[types.HouseID]
    house_2: Optional[types.HouseID]
    house_3: Optional[types.HouseID]

    @property
    def choosen_houses(self):
        return self.house_1, self.house_2, self.house_3

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
    hand_of_mafia_id: types.HandOfMafiaID
    game_id: types.GameID
    house_hand_id: types.HouseID
    victim_id: Optional[types.HouseID]

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
    game_id: types.GameID
    house_from_id: types.HouseID
    house_to_id: types.HouseID

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
class Break:
    break_id: str
    game_id: types.GameID
    count: int
    house_from: types.HouseID
    house_to: types.HouseID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house_from) == str(other.house_from),
                str(self.house_to) == str(other.house_to),
                self.count == other.count
            )
        )


@dataclass
class BonusHeading:
    bonus_id: str
    game_id: types.GameID
    house_id: types.HouseID
    value: float

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cant compare {self.__class__} with {type(other)}')
        return all(
            (
                str(self.game_id) == str(other.game_id),
                str(self.house_id) == str(other.house_id),
                self.value == other.value
            )
        )


@dataclass
class Kills:
    kill_id: str
    game_id: types.GameID
    killed_house_id: types.HouseID
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
    game_id: types.GameID
    house_id: types.HouseID
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
    game_id: types.GameID
    checked_house_id: Optional[types.HouseID]
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
    game_id: types.GameID
    checked_house_id: Optional[types.HouseID]
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
    game_id: types.GameID
    house_id: Optional[types.HouseID]
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
    game_id: types.GameID
    bonus_from: Optional[types.HouseID]
    bonus_to: Optional[types.HouseID]

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


@dataclass
class Rating:
    rating_id: str
    mmr: int
    player: types.PlayerID
    season: str
    club: str


@dataclass
class Season:
    season_id: str
    name: str
    start: datetime
    end: datetime
    prew_season: Optional[str]


@dataclass
class GameInfo:
    game: Optional[Game] = None
    best_move: Optional[BestMove] = None
    hand_of_mafia: Optional[HandOfMafia] = None
    kills: List[Kills] = field(default_factory=list)
    votes: List[Voted] = field(default_factory=list)
    houses: List[House] = field(default_factory=list)
    breaks: List[Break] = field(default_factory=list)
    misses: List[Misses] = field(default_factory=list)
    devises: List[Devise] = field(default_factory=list)
    don_checks: List[DonChecks] = field(default_factory=list)
    disqualifieds: List[Disqualified] = field(default_factory=list)
    sheriff_checks: List[SheriffChecks] = field(default_factory=list)
    sheriff_versions: List[SheriffVersion] = field(default_factory=list)
    bonuses_from_heading: List[BonusHeading] = field(default_factory=list)
    nominated_for_best: List[NominatedForBest] = field(default_factory=list)
    bonuses_from_players: List[BonusFromPlayers] = field(default_factory=list)
    bonuses_for_tolerant: List[BonusTolerantFromPlayers] = field(default_factory=list)
