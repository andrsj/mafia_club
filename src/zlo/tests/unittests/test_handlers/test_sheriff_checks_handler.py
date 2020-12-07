from typing import List


from expects import expect, have_len
from nose.tools import assert_list_equal
from zlo.domain.handlers import CreateOrUpdateSheriffChecksHandler
from zlo.domain.events import CreateOrUpdateSheriffChecks
from zlo.tests.unittests.test_handlers.common import BaseTestHandler
from zlo.domain.model import SheriffChecks


class WhenSheriffChecksIsCreating(BaseTestHandler):

    @classmethod
    def examples_slots(cls):
        yield [1, ]
        yield [1, 2]
        yield [1, 2, 3]
        # Test create with misses
        # at start and in the middle
        yield [1, 0, 2]
        yield [0, 1]
        yield [0, 0, 1, 2]
        yield [0, 1, 0, 3]

    def given_info_and_event(self, choises_slots):

        self.handler = CreateOrUpdateSheriffChecksHandler(uowm=self._uowm, cache=self.cache)

        self.choises_houses = [house for house in self.houses if house.slot in choises_slots]

        self.sheriff_checks_event = CreateOrUpdateSheriffChecks(
            game_id=self.game.game_id,
            sheriff_checks=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.sheriff_checks_event)

    def it_should_save_sheriff_checks(self, choises_slots):
        our_sheriff_checks: List[SheriffChecks] = self._uowm.sess.sheriff_checks.get_by_game_id(self.game.game_id)
        our_sheriff_checks_tuples = [(check.circle_number, check.checked_house_id) for check in our_sheriff_checks]
        expect(our_sheriff_checks).to(have_len(len([slot for slot in choises_slots if slot])))

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_sheriff_checks_tuples = []
        for day, slot in enumerate(choises_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_sheriff_checks_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_sheriff_checks_tuples, key=lambda k: k[0]),
            sorted(expected_sheriff_checks_tuples, key=lambda k: k[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenSheriffChecksIsUpdated(BaseTestHandler):

    @classmethod
    def example_slots(cls):
        # Test update one slot
        yield [1, 0, 3], [2, 0, 3]
        yield [0, 0, 1], [0, 0, 2]
        yield [1, 2], [1, 3]

        # Test adding slot
        yield [1, 3, 5], [1, 3]

        # Test deleting slot
        yield [1, 0, 4, 0, 2], [1, 0, 0, 2]

        # Test full update event
        yield [0, 1, 2], [1, 2, 3]

    def given_model_and_event_for_update(self, old_slots, new_slots):

        self.handler = CreateOrUpdateSheriffChecksHandler(self._uowm, self.cache)
        houses = self.cache.get_houses_by_game_id(self.game.game_id)

        for day, slot in enumerate(old_slots, start=1):
            if slot == 0:
                continue
            house = houses.get(slot)
            self._uowm.sess.sheriff_checks.add(
                SheriffChecks(
                    sheriff_check_id=f'sheriff_check_id_{day}',
                    game_id=self.game.game_id,
                    checked_house_id=house.house_id,
                    circle_number=day
                )
            )

        self.sheriff_checks_event = CreateOrUpdateSheriffChecks(
            game_id=self.game.game_id,
            sheriff_checks=new_slots
        )

    def because_handler_process_event(self):
        self.handler(self.sheriff_checks_event)

    def it_should_update_sheriff_checks(self, old_slots, new_slots):
        our_sheriff_checks = self._uowm.sess.sheriff_checks.get_by_game_id(game_id=self.game.game_id)
        our_sheriff_checks_tuples = [
            (sheriff_check.circle_number, sheriff_check.checked_house_id)
            for sheriff_check in our_sheriff_checks
        ]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_sheriff_checks_tuples = []
        for day, slot in enumerate(new_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_sheriff_checks_tuples.append((day, house.house_id))

        expected_deleted_sheriff_checks_tuples = []
        for day, slot in enumerate(old_slots, start=1):
            house = houses.get(slot)
            if house is not None and slot not in new_slots:
                expected_deleted_sheriff_checks_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_sheriff_checks_tuples, key=lambda k: k[0]),
            sorted(expected_sheriff_checks_tuples, key=lambda k: k[0])
        )

        for sheriff_check_tuple in expected_deleted_sheriff_checks_tuples:
            assert sheriff_check_tuple not in our_sheriff_checks_tuples

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
