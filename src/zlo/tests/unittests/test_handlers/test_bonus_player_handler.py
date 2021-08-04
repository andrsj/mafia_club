from zlo.domain.handlers import CreateOrUpdateBonusFromPlayersHandler
from zlo.domain.events import CreateOrUpdateBonusFromPlayers
from zlo.domain.model import BonusFromPlayers
from nose.tools import assert_list_equal
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenBonusFromPlayersIsCreated(BaseTestHandler):

    @classmethod
    def example_bonuses(cls):
        yield {1: 2, 2: 1, 3: 10}
        yield {2: 6}
        yield {}

    def given_event_and_handler(self, bonuses):
        self.handler = CreateOrUpdateBonusFromPlayersHandler(uowm=self._uowm, cache=self.cache)

        self.event_bonus = CreateOrUpdateBonusFromPlayers(
            game_id=self.game.game_id,
            bonus=bonuses
        )

    def because_handler_process_event(self):
        self.handler(self.event_bonus)

    def it_should_save_bonuses(self, bonuses):
        our_bonuses = self._uowm.sess.bonuses_from_players.get_by_game_id(self.game.game_id)
        our_bonuses_tuples = [(bonus.bonus_from, bonus.bonus_to) for bonus in our_bonuses]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_bonuses_tuples = [
            (houses.get(slot_from).house_id, houses.get(slot_to).house_id)
            for slot_from, slot_to in bonuses.items()
        ]

        assert_list_equal(
            sorted(our_bonuses_tuples, key=lambda b: b[0]),
            sorted(expected_bonuses_tuples, key=lambda b: b[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenBonusFromPlayersIsUpdated(BaseTestHandler):

    @classmethod
    def example_bonuses(cls):
        # Update slot to
        yield {1: 2}, {1: 3}

        # Update slot from
        yield {2: 3}, {1: 3}

        # Delete one bonus
        yield {1: 2, 3: 4}, {3: 4}

        # Add one bonus
        yield {1: 2}, {1: 2, 3: 4}

    def given_event_and_handler(self, old_data, new_data):
        self.handler = CreateOrUpdateBonusFromPlayersHandler(uowm=self._uowm, cache=self.cache)
        houses = self.cache.get_houses_by_game_id(self.game.game_id)

        for i, (slot_from, slot_to) in enumerate(old_data.items()):
            self._uowm.sess.bonuses_from_players.add(
                BonusFromPlayers(
                    game_id=self.game.game_id,
                    bonus_id=f"{i}_bonus_from_player_id",
                    bonus_from=houses.get(slot_from).house_id,
                    bonus_to=houses.get(slot_to).house_id
                )
            )

        self.bonus_event = CreateOrUpdateBonusFromPlayers(
            game_id=self.game.game_id,
            bonus=new_data
        )

    def because_handler_process_event(self):
        self.handler(self.bonus_event)

    def it_should_update_bonuses(self, old_data, new_data):
        our_bonuses = self._uowm.sess.bonuses_from_players.get_by_game_id(self.game.game_id)
        our_bonuses_tuples = [(bonus.bonus_from, bonus.bonus_to) for bonus in our_bonuses]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_bonuses_tuples = [
            (houses.get(slot_from).house_id, houses.get(slot_to).house_id)
            for slot_from, slot_to in new_data.items()
        ]

        assert_list_equal(
            sorted(our_bonuses_tuples, key=lambda b: b[0]),
            sorted(expected_bonuses_tuples, key=lambda b: b[0])
        )

        expected_deleted_bonuses_tuples = []
        for slot_from, slot_to in old_data.items():
            house_from = houses.get(slot_from).house_id
            house_to = houses.get(slot_to).house_id
            bonus_tuple = (house_from, house_to)
            if bonus_tuple not in expected_bonuses_tuples:
                expected_deleted_bonuses_tuples.append(bonus_tuple)

        for bonus_tuple in expected_deleted_bonuses_tuples:
            assert bonus_tuple not in our_bonuses_tuples

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
