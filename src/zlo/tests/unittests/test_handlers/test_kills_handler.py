import contexts
from nose.tools import assert_list_equal
from zlo.domain.model import Kills
from zlo.domain.handlers import CreateOrUpdateKillsHandler
from zlo.domain.events import CreateOrUpdateKills
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenKillsIsCreated(BaseTestHandler):

    @classmethod
    def examples_slots(cls):
        yield [1, 2]
        yield [1, 2, 3, 4]

        # Test event with misses
        # at start and in the middle
        yield [1, 0, 2, 3]
        yield [1, 0, 0, 2, 3]
        yield [0, 1, 0, 2]
        yield [0, 0, 1]

    def given_event(self, choises_slots):

        self.handler = CreateOrUpdateKillsHandler(self._uowm, self.cache)

        self.kills_event = CreateOrUpdateKills(
            game_id=self.game.game_id,
            kills_slots=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.kills_event)

    def it_should_save_kills(self, choises_slots):
        our_kills = self._uowm.sess.kills.get_by_game_id(game_id=self.game.game_id)
        our_kills_tuples = [(kill.circle_number, kill.killed_house_id) for kill in our_kills]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_kills_tuples = []
        for day, slot in enumerate(choises_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_kills_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_kills_tuples, key=lambda k: k[0]),
            sorted(expected_kills_tuples, key=lambda k: k[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenKillsIsUpdated(BaseTestHandler):

    @classmethod
    def example_slots(cls):
        # Test update one slot
        yield [1, 0, 3], [2, 0, 3]
        yield [1, 2], [1, 3]
        yield [0, 0, 1], [0, 0, 2]

        # Test deleting slot
        yield [1, 3, 5], [1, 3]

        # Test adding slot
        yield [1, 0, 4, 0, 2], [1, 0, 0, 2]

        # Test full update
        yield [0, 1, 2], [1, 2, 3]

    def given_model_and_event_for_update(self, old_slots, new_slots):

        self.handler = CreateOrUpdateKillsHandler(self._uowm, self.cache)
        houses = self.cache.get_houses_by_game_id(self.game.game_id)

        for day, slot in enumerate(old_slots, start=1):
            if slot == 0:
                continue
            house = houses.get(slot)
            self._uowm.sess.kills.add(
                Kills(
                    kill_id=f'kill_id_{day}',
                    game_id=self.game.game_id,
                    killed_house_id=house.house_id,
                    circle_number=day
                )
            )

        self.kills_event = CreateOrUpdateKills(
            game_id=self.game.game_id,
            kills_slots=new_slots
        )

    def because_handler_process_event(self):
        self.handler(self.kills_event)

    def it_should_update_kills(self, old_slots, new_slots):
        our_kills = self._uowm.sess.kills.get_by_game_id(game_id=self.game.game_id)
        our_kills_tuples = [(kill.circle_number, kill.killed_house_id) for kill in our_kills]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_kills_tuples = []
        for day, slot in enumerate(new_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_kills_tuples.append((day, house.house_id))

        expected_deleted_kills_tuples = []
        for day, slot in enumerate(old_slots, start=1):
            house = houses.get(slot)
            if house is not None and slot not in new_slots:
                expected_deleted_kills_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_kills_tuples, key=lambda k: k[0]),
            sorted(expected_kills_tuples, key=lambda k: k[0])
        )

        for kill_tuple in expected_deleted_kills_tuples:
            assert kill_tuple not in our_kills_tuples


if __name__ == '__main__':
    contexts.main()
