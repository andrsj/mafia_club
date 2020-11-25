import contexts
from nose.tools import assert_list_equal
from zlo.domain.model import Misses
from zlo.domain.handlers import CreateOrUpdateMissesHandler
from zlo.domain.events import CreateOrUpdateMisses
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenMissesIsCreated(BaseTestHandler):

    @classmethod
    def example_slots(cls):
        yield [1, 2]
        yield [1, 0, 2]

        # Test create without misses
        # at start and in the middle
        yield [0, 1, 0, 2]
        yield [0, 0, 5]

    def given_event_and_handler(self, choises_slots):
        self.handler = CreateOrUpdateMissesHandler(uowm=self._uowm, cache=self.cache)

        self.misses_event = CreateOrUpdateMisses(
            game_id=self.game.game_id,
            misses_slots=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.misses_event)

    def it_should_save_misses(self, choises_slots):
        our_misses = self._uowm.sess.misses.get_by_game_id(game_id=self.game.game_id)
        our_misss_tuples = [(miss.circle_number, miss.house_id) for miss in our_misses]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_misses_tuples = []
        for day, slot in enumerate(choises_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_misses_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_misss_tuples, key=lambda k: k[0]),
            sorted(expected_misses_tuples, key=lambda k: k[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenMissesIsUpdated(BaseTestHandler):
    @classmethod
    def example_slots(cls):
        # Test one slot update
        yield [1, 0, 3], [2, 0, 3]
        yield [0, 0, 1], [0, 0, 2]
        yield [1, 2], [1, 3]

        # Test deleting slot
        yield [1, 3, 5], [1, 3]

        # Test adding slot
        yield [1, 0, 4, 0, 2], [1, 0, 0, 2]

        # Test full update
        yield [0, 1, 2], [1, 2, 3]

    def given_model_and_event_for_update(self, old_slots, new_slots):

        self.handler = CreateOrUpdateMissesHandler(self._uowm, self.cache)
        houses = self.cache.get_houses_by_game_id(self.game.game_id)

        for day, slot in enumerate(old_slots, start=1):
            if slot == 0:
                continue
            house = houses.get(slot)
            self._uowm.sess.misses.add(
                Misses(
                    misses_id=f'miss_id_{day}',
                    game_id=self.game.game_id,
                    house_id=house.house_id,
                    circle_number=day
                )
            )

        self.misses_event = CreateOrUpdateMisses(
            game_id=self.game.game_id,
            misses_slots=new_slots
        )

    def because_handler_process_event(self):
        self.handler(self.misses_event)

    def it_should_update_misss(self, old_slots, new_slots):
        our_misses = self._uowm.sess.misses.get_by_game_id(game_id=self.game.game_id)
        our_misses_tuples = [(miss.circle_number, miss.house_id) for miss in our_misses]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_misses_tuples = []
        for day, slot in enumerate(new_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_misses_tuples.append((day, house.house_id))

        expected_deleted_misses_tuples = []
        for day, slot in enumerate(old_slots, start=1):
            house = houses.get(slot)
            if house is not None and slot not in new_slots:
                expected_deleted_misses_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_misses_tuples, key=lambda k: k[0]),
            sorted(expected_misses_tuples, key=lambda k: k[0])
        )

        for miss_tuple in expected_deleted_misses_tuples:
            assert miss_tuple not in our_misses_tuples
