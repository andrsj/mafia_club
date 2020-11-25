import logging
import uuid
from copy import copy
from typing import List, Dict
from collections import namedtuple

import inject
from zlo.domain.types import GameID
from zlo.domain.infrastructure import EventHouseModel
from zlo.domain.events import (
    CreateOrUpdateGame,
    CreateOrUpdateHouse,
    CreateOrUpdateVoted,
    CreateOrUpdateKills,
    CreateOrUpdateBestMove,
    CreateOrUpdateHandOfMafia,
    CreateOrUpdateDisqualified,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateNominatedForBest
)
from zlo.domain.infrastructure import UnitOfWorkManager, HouseCacheMemory
from zlo.domain.model import (
    Game,
    House,
    Kills,
    Voted,
    Devise,
    Player,
    BestMove,
    DonChecks,
    HandOfMafia,
    Disqualified,
    SheriffChecks,
    SheriffVersion,
    NominatedForBest,
    BonusPointsFromPlayers,
    BonusTolerantPointFromPlayers
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
            # This object if to replace list of dict with list of namedtuple.
            # Just to make code more readable and comfortable to write
            event_house = namedtuple("EventHouse", ['day', 'house_id'])

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

                    voted_event_houses.append(event_house(day=day, house_id=house.house_id))

            # Get slots which are already saved in db. And check if they are up-to-date

            votes: List[Voted] = tx.voted.get_by_game_id(evt.game_id)
            all_votes_tuples = [event_house(voted.day, voted.house_id) for voted in votes]
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


class CreateOrUpdateKillsHandler(BaseHandler):

    def __call__(self, evt: CreateOrUpdateKills):
        with self._uowm.start() as tx:
            houses: Dict[int, House] = self.get_houses(tx, game_id=evt.game_id)

            killed_event_houses = []

            for day, slot in enumerate(evt.kills_slots, start=1):
                house = houses.get(slot)
                if house is None:
                    killed_event_houses.append(None)
                else:
                    killed_event_houses.append(
                        EventHouseModel(
                            day=day,
                            house_id=house.house_id
                        )
                    )

            # Get slots which are already saved in db. And check if they are up-to-date

            kills: List[Kills] = tx.kills.get_by_game_id(evt.game_id)
            all_kills_tuples = [EventHouseModel(kill.circle_number, kill.killed_house_id) for kill in kills]
            valid_kills = copy(all_kills_tuples)

            # Remove redundant
            for kill, kill_t in zip(kills, all_kills_tuples):
                if kill_t not in killed_event_houses:
                    tx.kills.delete(kill)
                    valid_kills.remove(kill_t)

            # Add which is missed
            for kill_event in killed_event_houses:
                if kill_event not in valid_kills and kill_event is not None:
                    kill = Kills(
                        kill_id=str(uuid.uuid4()),
                        game_id=evt.game_id,
                        killed_house_id=kill_event.house_id,
                        circle_number=kill_event.day
                    )
                    tx.kills.add(kill)

            tx.commit()
