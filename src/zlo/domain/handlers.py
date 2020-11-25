import logging
import uuid
from copy import copy
from typing import List, Dict

import inject
from zlo.domain.types import GameID
from zlo.domain.utils import EventHouseModel
from zlo.domain.events import (
    CreateOrUpdateGame,
    CreateOrUpdateHouse,
    CreateOrUpdateVoted,
    CreateOrUpdateMisses,
    CreateOrUpdateBestMove,
    CreateOrUpdateDonChecks,
    CreateOrUpdateHandOfMafia,
    CreateOrUpdateDisqualified,
    CreateOrUpdateBonusTolerant,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateNominatedForBest,
    CreateOrUpdateSheriffChecks,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateNominatedForBest,
    CreateOrUpdateBonusFromPlayers
)
from zlo.domain.infrastructure import UnitOfWorkManager, HouseCacheMemory
from zlo.domain.model import (
    Game,
    House,
    Kills,
    Voted,
    Devise,
    Misses,
    Player,
    BestMove,
    DonChecks,
    HandOfMafia,
    Disqualified,
    SheriffChecks,
    SheriffVersion,
    NominatedForBest,
    BonusTolerantFromPlayers,
    BonusFromPlayers
)
from zlo.tests.fakes import FakeHouseCacheMemory


class BaseHandler:
    @inject.params(
        uowm=UnitOfWorkManager,
        cache=HouseCacheMemory
    )
    def __init__(self, uowm, cache):
        self._uowm = uowm
        self._log = logging.getLogger(__name__)
        self.cache: FakeHouseCacheMemory = cache

    def get_houses(self, tx, game_id: GameID):
        """
        Get houses from cache.
        If no houses in cache than houses get from db
        and save in cache
        Transform house to dict
        Example: {slot: House, ...}
        """
        houses: Dict[int, House] = self.cache.get_houses_by_game_id(game_id)

        if houses is None:
            houses_from_db: List[House] = tx.houses.get_by_game_id(game_id)
            self.cache.add_houses_by_game(game_id=game_id, houses=houses_from_db)
            houses = {house.slot: house for house in houses_from_db}

        return houses


class CreateOrUpdateGameHandler:
    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, uowm):
        self._uowm = uowm
        self._log = logging.getLogger(__name__)

    def __call__(self, evt: CreateOrUpdateGame):

        with self._uowm.start() as tx:
            player: Player = tx.players.get_by_nickname(evt.heading)
            game: Game = tx.games.get_by_game_id(evt.game_id)
            if game is None:
                self._log.info(f"Create new game {evt}")
                game = Game(
                    game_id=evt.game_id,
                    tournament=evt.tournament,
                    heading=player.player_id,
                    date=evt.date,
                    club=evt.club,
                    result=evt.result,
                    table=evt.table,
                    advance_result=evt.advance_result
                )
                tx.games.add(game)
            else:
                self._log.info(f"Update existing game {evt}")
                game.tournament = evt.tournament
                game.heading = player.player_id
                game.date = evt.date
                game.club = evt.club
                game.result = evt.result
                game.advance_result = evt.advance_result
                game.table = evt.table
            tx.commit()


class CreateOrUpdateHouseHandler:
    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, uowm):
        self._uowm = uowm
        self._log = logging.getLogger(__name__)

    def __call__(self, evt: CreateOrUpdateHouse):
        with self._uowm.start() as tx:
            player: Player = tx.players.get_by_nickname(evt.player_nickname)
            house: House = tx.houses.get_by_game_id_and_slot(evt.game_id, evt.slot)

            if house is None:
                self._log.info(f"Create new house {evt}")
                house = House(
                    house_id=str(uuid.uuid4()),
                    game_id=evt.game_id,
                    player_id=player.player_id,
                    role=evt.role.value,
                    slot=evt.slot,
                    bonus_mark=evt.bonus_mark,
                    fouls=evt.fouls
                )
                tx.houses.add(house)
            else:
                self._log.info(f"Update existing house {evt}")
                house.game_id = evt.game_id
                house.player_id = player.player_id
                house.role = evt.role.value
                house.slot = evt.slot
                house.bonus_mark = evt.bonus_mark
                house.fouls = evt.fouls
            tx.commit()


class CreateOrUpdateBestMoveHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateBestMove):
        with self._uowm.start() as tx:

            houses: Dict[int, House] = self.get_houses(tx, evt.game_id)

            killed_house: House = houses[evt.killed_player_slot]
            best_1_house: House = houses[evt.best_1_slot]
            best_2_house: House = houses[evt.best_2_slot]
            best_3_house: House = houses[evt.best_3_slot]

            best_move: BestMove = tx.best_moves.get_by_game_id(evt.game_id)

            if best_move is None:
                self._log.info(f"Create new best move {evt}")
                best_move = BestMove(
                    best_move_id=str(uuid.uuid4()),
                    game_id=evt.game_id,
                    killed_house=killed_house.house_id,
                    best_1=best_1_house.house_id,
                    best_2=best_2_house.house_id,
                    best_3=best_3_house.house_id,
                )
                tx.best_moves.add(best_move)
            else:
                self._log.info(f"Update best move {evt}")
                best_move.game_id = evt.game_id
                best_move.killed_house = killed_house.house_id
                best_move.best_1 = best_1_house.house_id
                best_move.best_2 = best_2_house.house_id
                best_move.best_3 = best_3_house.house_id
            tx.commit()


class CreateOrUpdateSheriffVersionHandler:
    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, uowm):
        self._uowm = uowm
        self._log = logging.getLogger(__name__)

    def __call__(self, evt: CreateOrUpdateSheriffVersion):
        with self._uowm.start() as tx:
            houses: List[House] = [
                house for house in tx.houses.get_by_game_id(evt.game_id)
                if house.slot in evt.sheriff_version_slots
            ]
            sheriff_versions: List[SheriffVersion] = tx.sheriff_versions.get_by_game_id(evt.game_id)
            if not sheriff_versions:
                for house in houses:
                    sheriff_version = SheriffVersion(
                        sheriff_version_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        house=house.house_id
                    )
                    tx.sheriff_versions.add(sheriff_version)
            else:
                for sheriff_version, house in zip(sheriff_versions, houses):
                    sheriff_version.house = house.house_id
            tx.commit()


class CreateOrUpdateDisqualifiedHandler:
    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, uowm):
        self._uowm = uowm
        self._log = logging.getLogger(__name__)

    def __call__(self, evt: CreateOrUpdateDisqualified):
        with self._uowm.start() as tx:
            houses: List[House] = [
                house for house in tx.houses.get_by_game_id(evt.game_id)
                if house.slot in evt.disqualified_slots
            ]
            disqualifieds: List[Disqualified] = tx.disqualifieds.get_by_game_id(evt.game_id)
            if not disqualifieds:
                for house in houses:
                    disqualified = Disqualified(
                        disqualified_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        house=house.house_id
                    )
                    tx.disqualifieds.add(disqualified)
            else:
                for sheriff_version, house in zip(disqualifieds, houses):
                    sheriff_version.house = house.house_id
            tx.commit()


class CreateOrUpdateNominatedForBestHandler:
    @inject.params(
        uowm=UnitOfWorkManager
    )
    def __init__(self, uowm):
        self._uowm = uowm
        self._log = logging.getLogger(__name__)

    def __call__(self, evt: CreateOrUpdateNominatedForBest):
        with self._uowm.start() as tx:
            houses: List[House] = [
                house for house in tx.houses.get_by_game_id(evt.game_id)
                if house.slot in evt.nominated_slots
            ]
            nominated_for_bests: List[NominatedForBest] = tx.nominated_for_best.get_by_game_id(evt.game_id)
            if not nominated_for_bests:
                for house in houses:
                    nominated_for_best = NominatedForBest(
                        nominated_for_best_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        house=house.house_id
                    )
                    tx.nominated_for_best.add(nominated_for_best)
            else:
                for nominated_for_best, house in zip(nominated_for_bests, houses):
                    nominated_for_best.house = house.house_id
            tx.commit()


class CreateOrUpdateVotedHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateVoted):
        with self._uowm.start() as tx:

            houses: Dict[int, House] = self.get_houses(tx, game_id=evt.game_id)

            voted_event_houses = []

            # Parse voted slots from event
            for day, slots in evt.voted_slots.items():
                if slots is None:
                    continue
                for slot in slots:
                    try:
                        house = houses[slot]
                    except KeyError:
                        # todo exception should be raised about missing house
                        continue

                    voted_event_houses.append(EventHouseModel(day=day, house_id=house.house_id))

            # Get slots which are already saved in db. And check if they are up-to-date

            votes: List[Voted] = tx.voted.get_by_game_id(evt.game_id)
            all_votes_tuples = [EventHouseModel(voted.day, voted.house_id) for voted in votes]
            valid_votes = copy(all_votes_tuples)

            # Remove redundant
            for voted, voted_t in zip(votes, all_votes_tuples):
                if voted_t not in voted_event_houses:
                    tx.voted.delete(voted)
                    valid_votes.remove(voted_t)

            # Add which is missed
            for voted_event in voted_event_houses:
                if voted_event not in valid_votes:
                    voted = Voted(
                        game_id=evt.game_id,
                        voted_id=str(uuid.uuid4()),
                        house_id=voted_event.house_id,
                        day=voted_event.day
                    )
                    tx.voted.add(voted)

            tx.commit()


class CreateOrUpdateHandOfMafiaHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateHandOfMafia):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, evt.game_id)

            hand_house = houses[evt.slot_from]  # Who vote
            victim_house = houses[evt.slot_to]  # Who voted

            hand_of_mafia: HandOfMafia = tx.hand_of_mafia.get_by_game_id(evt.game_id)
            if hand_of_mafia is None:
                hand_of_mafia = HandOfMafia(
                    hand_of_mafia_id=str(uuid.uuid4()),
                    game_id=evt.game_id,
                    house_hand_id=hand_house.house_id,
                    victim_id=victim_house.house_id
                )
                tx.hand_of_mafia.add(hand_of_mafia)
            else:
                hand_of_mafia.house_hand_id = hand_house.house_id
                hand_of_mafia.victim_id = victim_house.house_id

            tx.commit()


class CreateOrUpdateMissesHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateMisses):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, game_id=evt.game_id)

            misses_event_houses = []

            for day, slot in enumerate(evt.misses_slots, start=1):
                house = houses.get(slot)
                if house is None:
                    misses_event_houses.append(None)
                else:
                    misses_event_houses.append(
                        EventHouseModel(
                            day=day,
                            house_id=house.house_id
                        )
                    )

            misses: List[Misses] = tx.misses.get_by_game_id(evt.game_id)
            all_misses_tuples = [EventHouseModel(miss.circle_number, miss.house_id) for miss in misses]
            valid_misses = copy(all_misses_tuples)

            # Remove redundant
            for miss, miss_tuple in zip(misses, all_misses_tuples):
                if miss_tuple not in misses_event_houses:
                    tx.misses.delete(miss)
                    valid_misses.remove(miss_tuple)

            # Add which is missed
            for miss_event in misses_event_houses:
                if miss_event not in valid_misses and miss_event is not None:
                    miss = Misses(
                        misses_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        house_id=miss_event.house_id,
                        circle_number=miss_event.day
                    )
                    tx.misses.add(miss)

            tx.commit()


class CreateOrUpdateBonusFromPlayersHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateBonusFromPlayers):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, evt.game_id)

            bonuses_from_players: List[BonusFromPlayers] = tx.bonuses_from_players.get_by_game_id(evt.game_id)
            bonuses_from_players_tuples = [
                (bonus.bonus_from, bonus.bonus_to)
                for bonus in bonuses_from_players
            ]
            valid_bonuses_from_players_tuples = copy(bonuses_from_players_tuples)

            bonuses_from_players_event_tuples = []
            for slot_from, slot_to in evt.bonus.items():
                house_from = houses.get(slot_from).house_id
                house_to = houses.get(slot_to).house_id
                bonuses_from_players_event_tuples.append((house_from, house_to))

            # Remove redundant
            for bonus, bonus_t in zip(bonuses_from_players, bonuses_from_players_tuples):
                if bonus_t not in bonuses_from_players_event_tuples:
                    tx.bonuses_from_players.delete(bonus)
                    valid_bonuses_from_players_tuples.remove(bonus_t)

            # Add which is missed
            for bonus_event in bonuses_from_players_event_tuples:
                if bonus_event not in valid_bonuses_from_players_tuples:
                    bonus = BonusFromPlayers(
                        game_id=evt.game_id,
                        bonus_id=str(uuid.uuid4()),
                        bonus_from=bonus_event[0],
                        bonus_to=bonus_event[1]
                    )
                    tx.bonuses_from_players.add(bonus)

            tx.commit()





class CreateOrUpdateDonChecksHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateDonChecks):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, game_id=evt.game_id)

            don_checks_event_houses = []

            for day, slot in enumerate(evt.don_checks, start=1):
                house = houses.get(slot)
                if house is None:
                    don_checks_event_houses.append(None)
                else:
                    don_checks_event_houses.append(
                        EventHouseModel(
                            day=day,
                            house_id=house.house_id
                        )
                    )

            # Get slots which are already saved in db. And check if they are up-to-date

            don_checks: List[DonChecks] = tx.don_checks.get_by_game_id(evt.game_id)
            all_don_checks_tuples = [
                EventHouseModel(don_check.circle_number, don_check.checked_house_id)
                for don_check in don_checks
            ]
            valid_don_checks = copy(all_don_checks_tuples)

            # Remove redundant
            for don_check, don_check_tuple in zip(don_checks, all_don_checks_tuples):
                if don_check_tuple not in don_checks_event_houses:
                    tx.don_checks.delete(don_check)
                    valid_don_checks.remove(don_check_tuple)

            # Add which is missed
            for don_check_event in don_checks_event_houses:
                if don_check_event not in valid_don_checks and don_check_event is not None:
                    don_check = DonChecks(
                        don_checks_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        checked_house_id=don_check_event.house_id,
                        circle_number=don_check_event.day
                    )
                    tx.don_checks.add(don_check)

            tx.commit()


class CreateOrUpdateSheriffChecksHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateSheriffChecks):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, game_id=evt.game_id)

            sheriff_checks_event_houses = []

            for day, slot in enumerate(evt.sheriff_checks, start=1):
                house = houses.get(slot)
                if house is None:
                    sheriff_checks_event_houses.append(None)
                else:
                    sheriff_checks_event_houses.append(
                        EventHouseModel(
                            day=day,
                            house_id=house.house_id
                        )
                    )

            sheriff_checks: List[SheriffChecks] = tx.sheriff_checks.get_by_game_id(evt.game_id)
            all_sheriff_checks_tuples = [
                # event_house(check.circle_number, check.checked_house_id)
                EventHouseModel(check.circle_number, check.checked_house_id)
                for check in sheriff_checks
            ]
            valid_sheriff_checks = copy(all_sheriff_checks_tuples)

            # Remove redundant
            for sheriff_check, sheriff_check_t in zip(sheriff_checks, all_sheriff_checks_tuples):
                if sheriff_check_t not in sheriff_checks_event_houses:
                    tx.sheriff_checks.delete(sheriff_check)
                    valid_sheriff_checks.remove(sheriff_check_t)

            # Add which is missed
            for sheriff_check_event in sheriff_checks_event_houses:
                if sheriff_check_event not in valid_sheriff_checks and sheriff_check_event is not None:
                    sheriff_check = SheriffChecks(
                        sheriff_checks_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        checked_house_id=sheriff_check_event.house_id,
                        circle_number=sheriff_check_event.day
                    )
                    tx.sheriff_checks.add(sheriff_check)

            tx.commit()

class CreateOrUpdateBonusTolerantHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateBonusTolerant):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, evt.game_id)

            bonuses_tolerant: List[BonusTolerantFromPlayers] = tx.bonuses_tolerant.get_by_game_id(evt.game_id)
            bonuses_tolerant_tuples = [
                (bonus.house_from_id, bonus.house_to_id)
                for bonus in bonuses_tolerant
            ]
            valid_bonuses_tolerant_tuples = copy(bonuses_tolerant_tuples)

            bonuses_tolerant_event_tuples = []
            for slot_from, slot_to in evt.bonuses.items():
                house_from = houses.get(slot_from).house_id
                house_to = houses.get(slot_to).house_id
                bonuses_tolerant_event_tuples.append((house_from, house_to))

            # Remove redundant
            for bonus, bonus_t in zip(bonuses_tolerant, bonuses_tolerant_tuples):
                if bonus_t not in bonuses_tolerant_event_tuples:
                    tx.bonuses_tolerant.delete(bonus)
                    valid_bonuses_tolerant_tuples.remove(bonus_t)

            # Add which is missed
            for bonus_event in bonuses_tolerant_event_tuples:
                if bonus_event not in valid_bonuses_tolerant_tuples:
                    bonus = BonusTolerantFromPlayers(
                        game_id=evt.game_id,
                        bonus_id=str(uuid.uuid4()),
                        house_from_id=bonus_event[0],
                        house_to_id=bonus_event[1]
                    )
                    tx.bonuses_tolerant.add(bonus)

            tx.commit()

