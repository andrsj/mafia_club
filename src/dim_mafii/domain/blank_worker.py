from typing import Optional, Dict, List, Tuple

import inject

from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.domain.types import GameResult, AdvancedGameResult, ClassicRole, BlankError
from dim_mafii.sheet_parser.client2 import SpreadSheetManager


class MatrixParser:

    def __init__(self, matrix):
        self._matrix = matrix

    def get_game_result(self) -> Optional[GameResult]:
        if self._matrix[1][9]:
            return GameResult.mafia
        elif self._matrix[0][9]:
            return GameResult.citizen
        else:
            return None

    def get_advanced_result(self) -> Optional[AdvancedGameResult]:
        result = self.get_game_result()
        if result == GameResult.mafia:
            if self._matrix[4][7]:
                return AdvancedGameResult.three_on_three
            elif self._matrix[4][8]:
                return AdvancedGameResult.two_on_two
            else:
                return AdvancedGameResult.one_on_one
        elif result == GameResult.citizen:
            if self._matrix[4][10]:
                return AdvancedGameResult.clear_citizen
            else:
                return AdvancedGameResult.guessing_game
        else:
            return None

    def get_heading(self) -> str:
        return self._matrix[1][2].lower().strip()

    def get_game_id(self) -> str:
        return self._matrix[6][2] or None

    def get_table_number(self) -> int:
        return self.get_number(self._matrix[4][5])

    @staticmethod
    def get_number(value: str) -> Optional[int]:
        if value.isdigit():
            return int(value)

    @classmethod
    def get_voted_from_string(cls, value: str) -> List[int]:
        value = value.strip()
        value.replace(' ', '')
        if value:
            if '10' in value:
                return [10] + [cls.get_slot_or_count_number_from_string(v) for v in value.replace('10', '')]
            return [cls.get_slot_or_count_number_from_string(v) for v in value]

    @staticmethod
    def get_role_from_string(value: str) -> Optional[ClassicRole]:
        value = value.upper()
        if value == "":
            return ClassicRole.citizen
        elif value == "М":
            return ClassicRole.mafia
        elif value == "Ш":
            return ClassicRole.sheriff
        elif value == "Д":
            return ClassicRole.don

    @staticmethod
    def get_bonus_mark(value) -> float:
        if value.strip():
            return float(value.strip().replace(',', '.'))
        return 0

    @staticmethod
    def get_slot_or_count_number_from_string(value) -> int:
        value = value.strip()
        if value in [str(i) for i in range(1, 11)]:
            return int(value)

    def get_best_move(self) -> Optional[Tuple[int, int, int, int]]:
        killed_player_slot = self.get_slot_or_count_number_from_string(self._matrix[22][1])
        if not killed_player_slot:
            return None

        best_1_slot = self.get_slot_or_count_number_from_string(self._matrix[22][2])
        best_2_slot = self.get_slot_or_count_number_from_string(self._matrix[22][3])
        best_3_slot = self.get_slot_or_count_number_from_string(self._matrix[22][4])
        if not (bool(best_1_slot) + bool(best_2_slot) + bool(best_3_slot)) > 1:
            return None

        return (
            killed_player_slot,
            best_1_slot,
            best_2_slot,
            best_3_slot
        )

    def get_disqualified(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[21][7:] if value]

    def get_sheriff_versions(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[22][7:]]

    def get_nominated_for_best(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[24][2:] if value]

    def get_kills(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[33][2:]]

    def get_votes(self) -> Optional[Dict[int, List[int]]]:
        """
        {
            day: [slot, slot, ...]
            day: [slot, slot, ...]
            ...
        }
        """
        results = {}
        for day, voted in enumerate(self._matrix[44][2:], start=1):
            results[day] = self.get_voted_from_string(voted)

        if all(value is None for value in results.values()):
            return None

        return results

    def get_sheriff_checks(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[37][2:]]

    def get_don_checks(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[40][2:]]

    def get_bonus_point_from_house_by_slot(self, slot) -> Optional[int]:
        slot = self.get_slot_or_count_number_from_string(self._matrix[slot + 9][8])
        return slot if slot else None

    def get_bonus_points_from_houses_data(self) -> Dict[int, int]:
        slots = {}
        for i in range(1, 11):
            row_number = i + 9
            slot = self.get_slot_or_count_number_from_string(self._matrix[row_number][8])
            if slot != 0:
                slots[i] = slot

        return slots

    def get_bonus_tolerant_point_from_house_by_slot(self, slot) -> Optional[int]:
        slot = self.get_slot_or_count_number_from_string(self._matrix[slot + 9][9])
        return slot if slot else None

    def get_bonus_tolerant_points_from_house_data(self) -> Dict[int, int]:
        slots = {}
        for i in range(1, 11):
            row_number = i + 9
            slot = self.get_slot_or_count_number_from_string(self._matrix[row_number][9])
            if slot != 0:
                slots[i] = slot

        return slots

    def get_bonus_points_from_heading(self) -> Dict[int, float]:
        bonus_points = {}
        for i in range(1, 11):
            row_number = i + 9
            point = self.get_bonus_mark(self._matrix[row_number][7])
            if point != 0:
                bonus_points[i] = point

        return bonus_points

    def get_hand_of_mafia(self) -> Dict[str, int]:
        return {
            'slot_from': self.get_slot_or_count_number_from_string(self._matrix[6][8]),
            'slot_to': self.get_slot_or_count_number_from_string(self._matrix[6][9])
        }

    def get_devises(self) -> Dict[int, Dict[str, int]]:
        devises = {}
        for row in range(27, 31):
            slot = self.get_slot_or_count_number_from_string(self._matrix[row][7])
            if slot:
                devises[slot] = {
                    'first': self.get_slot_or_count_number_from_string(self._matrix[row][8]),
                    'second': self.get_slot_or_count_number_from_string(self._matrix[row][9]),
                    'third': self.get_slot_or_count_number_from_string(self._matrix[row][10])
                }
        return devises

    def get_misses(self) -> List[int]:
        return [self.get_slot_or_count_number_from_string(value) for value in self._matrix[34][2:] if value]

    def get_breaks(self) -> Dict[int, Dict[str, int]]:
        breaks = {}
        for row in range(27, 31):
            count = self.get_slot_or_count_number_from_string(self._matrix[row][2])
            if count:
                breaks[count] = {
                    'count': count,
                    'slot_from': self.get_slot_or_count_number_from_string(self._matrix[row][3]),
                    'slot_to': self.get_slot_or_count_number_from_string(self._matrix[row][4])
                }

        return breaks

    def get_list_of_nicknames_players(self) -> List[str]:
        return [self._matrix[i][2] for i in range(10, 20)]

    def get_club(self) -> str:
        return self._matrix[3][2]

    def get_roles_of_players(self) -> Dict[int, ClassicRole]:
        return {i - 9: self.get_role_from_string(self._matrix[i][0]) for i in range(10, 20)}


class BlankChecker:
    """
    Checker one blank matrix for errors

    First step: check_empty_blank
    Second step: game_info_is_correct
    If previous step return False: get_errors
    """

    @inject.params(uowm=UnitOfWorkManager)
    def __init__(self, matrix_parser: MatrixParser, uowm):
        self.parser = matrix_parser
        self._uowm = uowm
        self.__errors: List[str] = []

    def game_info_is_correct(self) -> Optional[bool]:
        if self.check_empty_blank():
            return

        for method in [
            self.check_heading,
            self.check_players,
            self.check_winner,
            self.check_club,
            self.check_kills_with_votes,
            # TODO self.check_bonuses
            self.check_correct_kicks,
            self.check_mafia_hand,
            self.check_count_players_of_end_game
        ]:
            error: List[str] = method()
            if error:
                self.__errors.extend(error)

        return not self.__errors

    def get_errors(self) -> List[str]:
        return self.__errors

    def check_empty_blank(self) -> bool:
        """

        Return True if blank doesn't have players

         a = ['','','']      -  Empty blank due to NO ONE player
         b = ['a','b','']    -  Not empty blank due to Someone is missing
         c = ['a','b','c']   -  Not empty blank due to every 10 players is present
         for i in [a,b,c]:
            print(all(i), not any(i))

         False       True
         False       False
         True        False
        """
        players = self.parser.get_list_of_nicknames_players()
        return not any(players)

    def check_heading(self) -> List[str]:
        heading = self.parser.get_heading()
        with self._uowm.start() as tx:
            player = tx.players.get_by_nickname(heading)

        if not player:
            return [f"[Ведучий] Відсутній гравець в базі з ніком '{heading}'"]

    def check_club(self) -> List[str]:
        club = self.parser.get_club()
        if not club:
            return ['Не вказаний клуб гри']

        with self._uowm.start() as tx:
            clubs = tx.clubs.get_clubs()

        if club.lower().strip() not in [c.name.lower() for c in clubs]:
            return [f"Не вірна назва клубу '{club}'"]

    def check_winner(self) -> List[str]:
        game_result = self.parser.get_game_result()
        advanced_result = self.parser.get_advanced_result()

        if game_result is None:
            return ['Не вказана команда переможця']

        if advanced_result is None:
            return ['Не вказано тип перемоги']

    def check_kills_with_votes(self) -> Optional[List[str]]:
        kills = self.parser.get_kills()
        votes = self.parser.get_votes()

        errors = []
        if votes is None:
            return

        for day in votes:
            votes_per_day = votes[day]
            if votes_per_day:
                for vote in votes_per_day:
                    if vote and vote in kills:
                        errors.append(f'Заголосований і вбитий мають один і той же слот {vote}')

        return errors

    def check_players(self) -> List[str]:

        roles = self.parser.get_roles_of_players()
        if not any(roles):
            return ['Відсутні ролі для гравців']

        with self._uowm.start() as tx:
            players = tx.players.all()

        errors: List[str] = []

        nicknames = self.parser.get_list_of_nicknames_players()
        for i, nickname in enumerate(nicknames, start=1):
            player = next((p for p in players if p.nickname == nickname.lower().strip()), None)
            if player is None:
                errors.append(f"Відсутній гравець в базі з ніком '{nickname}' за слотом {i}")

        return errors

    def check_bonuses(self):
        # TODO Check type of bonuses [int slot OR float value]
        ...

    def check_correct_kicks(self) -> List[str]:
        ten_slots = {i: 0 for i in list(range(1, 11))}
        kills = self.parser.get_kills()
        disqs = self.parser.get_disqualified()
        votes = self.parser.get_votes()
        if votes:  # If game has votes -> filter for days non vote ELSE empty
            votes = [v for v in votes.values() if v]  # Filter None values [if day doesn't have votes]
            votes = [item for sublist in votes for item in sublist]  # Make flatten list for all votes
        else:
            votes = []

        for slots in (kills, disqs, votes):
            for slot in slots:
                if slot:
                    ten_slots[slot] = ten_slots.get(slot, 0) + 1

        for slot in ten_slots:
            if ten_slots[slot] > 1:
                return ['Не вірна гра (Вигнаний слот повторюється)']

    def check_mafia_hand(self) -> List[str]:
        roles = self.parser.get_roles_of_players()  # List of roles ['', 'Ш', 'М', 'Д', ...]
        hand_of_mafia = self.parser.get_hand_of_mafia()  # Info about slots, which players was

        for slot in hand_of_mafia.values():
            if not slot:
                continue
            if roles[slot].value in (ClassicRole.mafia.value, ClassicRole.don.value):  # If player was Mafia
                return ['Чорний гравець є Рукою Мафії']

    def check_count_players_of_end_game(self):
        if not self.check_correct_kicks():

            ten_slots = [i for i in range(1, 11)]
            kills = self.parser.get_kills()
            disqs = self.parser.get_disqualified()
            votes = self.parser.get_votes()
            if votes:  # If game has votes -> filter for days non vote ELSE empty
                votes = [v for v in votes.values() if v]  # Filter None values [if day doesn't have votes]
                votes = [item for sublist in votes for item in sublist]  # Make flatten list for all votes
            else:
                votes = []

            for slots in (kills, disqs, votes):
                for slot in slots:
                    if slot:
                        ten_slots.remove(slot)

            roles: Dict[int, ClassicRole] = self.parser.get_roles_of_players()
            mafias_slots = [role for role in roles if roles[role] in (ClassicRole.mafia, ClassicRole.don)]

            adv_res: AdvancedGameResult = self.parser.get_advanced_result()

            if adv_res.value == AdvancedGameResult.three_on_three.value:
                if len(ten_slots) > 6:
                    return ['Не вірна к-сть гравців, що вийшла при 3х3']

                # If citizens more than mafias
                if len([slot for slot in ten_slots if slot not in mafias_slots]) > 3:
                    return ['К-сть мирних більша за мафів при 3х3']

            elif adv_res.value == AdvancedGameResult.two_on_two.value:
                if len(ten_slots) > 4:
                    return ['Не вірна к-сть гравців, що вийшла при 2х2']

                # If citizens more than mafias
                if len([slot for slot in ten_slots if slot not in mafias_slots]) > 2:
                    return ['К-сть мирних більша за мафів при 2х2']

            elif adv_res.value == AdvancedGameResult.one_on_one:
                if len(ten_slots) > 2:
                    return ['Не вірна к-сть гравців, що вийшла при 1х1']

                # If citizens more than mafias
                if len([slot for slot in ten_slots if slot not in mafias_slots]) > 1:
                    return ['К-сть мирних більша за мафів при 1х1']

            elif adv_res.value in (AdvancedGameResult.clear_citizen.value, AdvancedGameResult.guessing_game.value):
                # If one or more mafias in end game
                if len([slot for slot in mafias_slots if slot in ten_slots]):
                    return ['При виграші мирних не всі мафіозники вийшли з гри']


def check_spreadsheets_for_errors(
        manager: SpreadSheetManager,
        list_of_spreadsheets_titles: List[str],
        status: str) -> Optional[str]:

    all_errors: List[BlankError] = []
    # List of all errors from ONE spreadsheet
    # (All worksheets which spreadsheet has)

    map_spreadsheets_name_ids = manager.get_map_spreadsheets_id_by_names(list_of_spreadsheets_titles)

    if not map_spreadsheets_name_ids:
        # TODO rewrite with logger on next Pull Request
        print('Not found ANY of these spreadsheets')
        return

    for spreadsheet_title in map_spreadsheets_name_ids:

        # TODO rewrite with logger on next Pull Request
        print(spreadsheet_title, '\n')

        spreadsheet_id = map_spreadsheets_name_ids[spreadsheet_title]
        spreadsheet = manager.get_spreadsheet_by_id(spreadsheet_id)

        worksheets = spreadsheet.worksheets()
        """
        Map urls with titles of worksheets (blanks)
        {
            'title1': url1,
            'title2': url2,
            ...
        }
        """
        map_worksheets_urls = {worksheet.title: worksheet.url for worksheet in worksheets}

        all_matrix: Dict[str: List[List]] = manager.get_matrix_from_sheet(spreadsheet)

        for blank_title in all_matrix:

            normalized_matrix = manager.get_sub_matrix(all_matrix[blank_title])
            matrix_parser = MatrixParser(normalized_matrix)
            blank_checker = BlankChecker(matrix_parser)

            if blank_checker.check_empty_blank():
                # TODO rewrite with logger on next Pull Request
                print('Empty blank:', blank_title)
                continue

            if blank_checker.game_info_is_correct():
                # TODO rewrite with logger on next Pull Request
                print('Correct blank:', blank_title)
                continue

            # TODO rewrite with logger on next Pull Request
            print('Checked blank:', blank_title)

            errors_per_one_blank: List[str] = blank_checker.get_errors()
            for error in errors_per_one_blank:
                all_errors.append(
                    BlankError(
                        spreadsheet_name=spreadsheet.title,
                        worksheet_name=blank_title,
                        information=error,
                        heading=matrix_parser.get_heading(),
                        worksheet_url=manager.get_url(map_worksheets_urls[blank_title])
                    )
                )

        manager.mark_blank_as_checked(spreadsheet, all_errors)
        print(spreadsheet.title, 'was marked!\n')

    if all_errors:
        url = manager.write_game_errors(all_errors, status)
        return url
