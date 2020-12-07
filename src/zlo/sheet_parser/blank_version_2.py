import uuid
from typing import List, Optional
from datetime import datetime

from zlo.domain.events import (
    CreateOrUpdateGame,
    CreateOrUpdateHouse,
    CreateOrUpdateBestMove,
    CreateOrUpdateDisqualified,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateNominatedForBest,
    CreateOrUpdateVoted,
    CreateOrUpdateSheriffChecks,
    CreateOrUpdateKills,
    CreateOrUpdateDonChecks,
    CreateOrUpdateMisses,
    CreateOrUpdateBonusFromHeading,
    CreateOrUpdateBonusFromPlayers,
    CreateOrUpdateBonusTolerant,
    CreateOrUpdateHandOfMafia,
    CreateOrUpdateBreaks,
    CreateOrUpdateDevises
)
from zlo.domain.types import AdvancedGameResult, ClassicRole
from zlo.domain.types import GameResult


class NotFinishedBlank(Exception):
    pass


class BlankParser:
    def __init__(self, matrix):
        self._matrix = matrix
        self._game_id = self._matrix[6][2]
        self._new_game = False
        if not self._game_id:
            self._game_id = str(uuid.uuid4())
            self._new_game = True

    def if_game_is_new(self):
        return self._new_game

    def parse_game_result(self):
        """
        Parse who win the game.
        If mafia win the game then check how mafia win this game
        If citizin win the game then check how citizen with this game
        :return: tuple(GameResult, AdvancedGameResult)
        """

        if self._matrix[1][9]:
            game_result = GameResult.mafia
        elif self._matrix[0][9]:
            game_result = GameResult.citizen
        else:
            raise NotFinishedBlank

        if game_result == GameResult.mafia:
            if self._matrix[4][7]:
                advanced_game_result = AdvancedGameResult.three_on_three
            elif self._matrix[4][8]:
                advanced_game_result = AdvancedGameResult.two_on_two
            else:
                advanced_game_result = AdvancedGameResult.one_on_one
        else:
            if self._matrix[4][10]:
                advanced_game_result = AdvancedGameResult.clear_citizen
            else:
                advanced_game_result = AdvancedGameResult.guessing_game

        return game_result, advanced_game_result

    def parse_game_info(self) -> CreateOrUpdateGame:
        """
        Get general stats about game
        """
        game_result, advanced_game_result = self.parse_game_result()
        return CreateOrUpdateGame(
            game_id=self._game_id,
            heading=self._matrix[1][2],

            # strptime(m[0][2], '%Y-%m-%d') or datetime.fromisoformat(m[0][2])
            date=datetime.strptime(self._matrix[0][2], '%Y-%m-%d'),

            club=self._matrix[3][2],
            tournament=self._matrix[4][2] or None,
            table=self.get_number_of_table(self._matrix[4][5]),
            result=game_result.value,
            advance_result=advanced_game_result.value
        )

    @staticmethod
    def get_bonus_mark(value):
        return float(value.strip().replace(',', '.')) if value else 0

    @staticmethod
    def get_role_from_string(value: str):
        value = value.upper()
        if value == "":
            return ClassicRole.citizen
        elif value == "М":
            return ClassicRole.mafia
        elif value == "Ш":
            return ClassicRole.sheriff
        elif value == "Д":
            return ClassicRole.don
        else:
            raise ValueError()

    def parse_houses(self) -> List[CreateOrUpdateHouse]:
        houses_events = []
        for i in range(1, 11):
            row_number = i + 9
            houses_events.append(
                CreateOrUpdateHouse(
                    game_id=self._game_id,
                    player_nickname=self._matrix[row_number][2],
                    role=self.get_role_from_string(self._matrix[row_number][0].strip()),
                    slot=int(self._matrix[row_number][1]),
                    bonus_mark=self.get_bonus_mark(self._matrix[row_number][7]),
                    fouls=len(
                        self._matrix[row_number][3]
                        + self._matrix[row_number][4]
                        + self._matrix[row_number][5]
                        + self._matrix[row_number][6]),
                )
            )

        return houses_events

    def parse_best_move(self) -> Optional[CreateOrUpdateBestMove]:
        killed_player_slot = self.get_slot_or_count_number_from_string(self._matrix[22][1])
        if not killed_player_slot:
            return None

        best_1_slot = self.get_slot_or_count_number_from_string(self._matrix[22][2])
        best_2_slot = self.get_slot_or_count_number_from_string(self._matrix[22][3])
        best_3_slot = self.get_slot_or_count_number_from_string(self._matrix[22][4])
        if not bool(best_1_slot) + bool(best_2_slot) + bool(best_3_slot) > 1:
            return None

        return CreateOrUpdateBestMove(
            game_id=self._game_id,
            killed_player_slot=killed_player_slot,
            best_1_slot=self.get_slot_or_count_number_from_string(self._matrix[22][2]),
            best_2_slot=self.get_slot_or_count_number_from_string(self._matrix[22][3]),
            best_3_slot=self.get_slot_or_count_number_from_string(self._matrix[22][4]),
        )

    @staticmethod
    def get_number_of_table(value: str) -> int:
        if value.isdigit():
            return int(value)
        return None

    @staticmethod
    def get_slot_or_count_number_from_string(value) -> int:
        value = value.strip()
        if value in [str(i) for i in range(1, 11)]:
            return int(value)
        else:
            return 0

    def get_voted_from_string(self, value: str):
        value = value.strip()
        value.replace(',', ' ').replace('.', ' ')
        if value:
            return [self.get_slot_or_count_number_from_string(v) for v in value.split(' ')]
        return None

    def parse_disqualified(self) -> CreateOrUpdateDisqualified:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[21][7:]]
        slots = [slot for slot in slots if bool(slot)]
        return CreateOrUpdateDisqualified(
            game_id=self._game_id,
            disqualified_slots=slots
        )

    def parse_sheriff_versions(self) -> CreateOrUpdateSheriffVersion:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[22][7:]]
        slots = [slot for slot in slots if bool(slot)]
        return CreateOrUpdateSheriffVersion(
            game_id=self._game_id,
            sheriff_version_slots=slots
        )

    def parse_nominated_for_best(self) -> CreateOrUpdateNominatedForBest:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[24][2:]]
        slots = [slot for slot in slots if bool(slot)]
        return CreateOrUpdateNominatedForBest(
            game_id=self._game_id,
            nominated_slots=slots
        )

    def parse_kills(self) -> CreateOrUpdateKills:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[33][2:]]
        while slots and slots[-1] == 0:
            slots.pop()
        return CreateOrUpdateKills(
            game_id=self._game_id,
            kills_slots=slots
        )

    def parse_voted(self) -> Optional[CreateOrUpdateVoted]:
        result = {}
        for i, voted in enumerate(self._matrix[44][2:], start=1):
            result[i] = self.get_voted_from_string(voted)
        if all([value is None for value in result.values()]):
            return None
        return CreateOrUpdateVoted(
            game_id=self._game_id,
            voted_slots=result
        )

    def parse_sheriff_checks(self) -> Optional[CreateOrUpdateSheriffChecks]:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[37][2:]]
        while slots and slots[-1] == 0:
            slots.pop()
        return CreateOrUpdateSheriffChecks(
            game_id=self._game_id,
            sheriff_checks=slots
        )

    def parse_don_checks(self) -> CreateOrUpdateDonChecks:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[40][2:]]
        while slots and slots[-1] == 0:
            slots.pop()
        return CreateOrUpdateDonChecks(
            game_id=self._game_id,
            don_checks=slots
        )

    def get_bonus_points_from_houses_data(self) -> CreateOrUpdateBonusFromPlayers:
        slots = {}
        for i in range(1, 11):
            row_number = i + 9
            slot = self.get_slot_or_count_number_from_string(self._matrix[row_number][8])
            if slot != 0:
                slots[i] = slot

        return CreateOrUpdateBonusFromPlayers(
            game_id=self._game_id,
            bonus=slots
        )

    def get_bonus_tolerant_points_from_houses_data(self) -> CreateOrUpdateBonusTolerant:
        slots = {}
        for i in range(1, 11):
            row_number = i + 9
            slot = self.get_slot_or_count_number_from_string(self._matrix[row_number][9])
            if slot != 0:
                slots[i] = slot

        return CreateOrUpdateBonusTolerant(
            game_id=self._game_id,
            bonuses=slots
        )

    def get_bonus_points_from_heading(self) -> List[CreateOrUpdateBonusFromHeading]:
        bonus_points = {}
        for i in range(1, 11):
            row_number = i + 9
            point = self.get_bonus_mark(self._matrix[row_number][7])
            if point != 0:
                bonus_points[i] = point

        events = [
            CreateOrUpdateBonusFromHeading(
                game_id=self._game_id,
                house_slot=slot,
                value=point
            ) for slot, point in bonus_points.items()
        ]
        return events

    def parse_hand_of_mafia(self) -> CreateOrUpdateHandOfMafia:
        voted_from = self.get_slot_or_count_number_from_string(self._matrix[6][8])
        voted_to = self.get_slot_or_count_number_from_string(self._matrix[6][9])
        return CreateOrUpdateHandOfMafia(
            game_id=self._game_id,
            slot_from=voted_from,
            slot_to=voted_to
        )

    def parse_devise(self):
        devises = []
        for row in range(27, 31):
            if self.get_slot_or_count_number_from_string(self._matrix[row][7]):
                devises.append(
                    CreateOrUpdateDevises(
                        game_id=self._game_id,
                        killed_slot=self.get_slot_or_count_number_from_string(self._matrix[row][7]),
                        first_slot=self.get_slot_or_count_number_from_string(self._matrix[row][8]),
                        second_slot=self.get_slot_or_count_number_from_string(self._matrix[row][9]),
                        third_slot=self.get_slot_or_count_number_from_string(self._matrix[row][10]),
                    )
                )

        return devises

    def parse_misses(self) -> CreateOrUpdateMisses:
        slots = [self.get_slot_or_count_number_from_string(value) for value in self._matrix[34][2:]]
        while slots and slots[-1] == 0:
            slots.pop()
        return CreateOrUpdateMisses(
            game_id=self._game_id,
            misses_slots=slots
        )

    def parse_breaks(self):
        breaks = []
        for row in range(27, 31):
            if self.get_slot_or_count_number_from_string(self._matrix[row][2]):
                breaks.append(
                    CreateOrUpdateBreaks(
                        game_id=self._game_id,
                        count=self.get_slot_or_count_number_from_string(self._matrix[row][2]),
                        slot_from=self.get_slot_or_count_number_from_string(self._matrix[row][3]),
                        slot_to=self.get_slot_or_count_number_from_string(self._matrix[row][4])
                    )
                )

        return breaks
