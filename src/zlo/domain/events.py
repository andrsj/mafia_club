from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

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


@dataclass
class CreateOrUpdateBestMove:
    game_id: str
    killed_player_slot: int
    best_1_slot: int
    best_2_slot: int
    best_3_slot: int

    def __init__(self, game_id, killed_player_slot, best_1_slot, best_2_slot, best_3_slot):
        self.game_id = game_id
        self.killed_player_slot = int(killed_player_slot)
        self.best_1_slot = int(best_1_slot) if best_1_slot else 0
        self.best_2_slot = int(best_2_slot) if best_2_slot else 0
        self.best_3_slot = int(best_3_slot) if best_3_slot else 0


@dataclass
class CreateOrUpdateDisqualified:
    game_id: str
    disqualified_slots: List[int]


@dataclass
class CreateOrUpdateSheriffVersion:
    game_id: str
    sheriff_version_slots: List[int]


@dataclass
class CreateOrUpdateNominatedForBest:
    game_id: str
    nominated_slots: List[int]


@dataclass
class CreateOrUpdateVoted:
    game_id: str
    voted_slots: Dict[int, Optional[List[int]]]


@dataclass
class CreateOrUpdateSheriffChecks:
    game_id: str
    sheriff_checks: List[int]


@dataclass
class CreateOrUpdateKills:
    game_id: str
    kills_slots: List[int]


@dataclass
class CreateOrUpdateDonChecks:
    game_id: str
    don_checks: List[int]


@dataclass
class CreateOrUpdateBonusFromHeading:
    game_id: str
    house_slot: int
    value: float


@dataclass
class CreateOrUpdateBonusFromPlayers:
    game_id: str
    bonus: Dict[int, int]

@dataclass
class CreateOrUpdateBonusTolerant:
    game_id: str
    bonuses: Dict[int, int]


@dataclass
class CreateOrUpdateMisses:
    game_id: str
    misses_slots: List[int]


@dataclass
class CreateOrUpdateHandOfMafia:
    game_id: str
    slot_from: int
    slot_to: int


@dataclass
class CreateOrUpdateBreaks:
    game_id: str
    count: int
    slot_from: int
    slot_to: int


@dataclass
class CreateOrUpdateDevises:
    game_id: str
    killed_slot: int
    first_slot: int
    second_slot: int
    third_slot: int
