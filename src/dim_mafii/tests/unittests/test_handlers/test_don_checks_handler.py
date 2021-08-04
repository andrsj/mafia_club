from nose.tools import assert_list_equal
from dim_mafii.domain.model import DonChecks
from dim_mafii.domain.handlers import CreateOrUpdateDonChecksHandler
from dim_mafii.domain.events import CreateOrUpdateDonChecks
from dim_mafii.tests.unittests.test_handlers.common import BaseTestHandler


class WhenDonChecksIsCreated(BaseTestHandler):

    @classmethod
    def examples_slots(cls):
        yield [1, 2]
        yield [1, 2, 3, 4]

        # Test with misses
        # at start and in the middle
        yield [1, 0, 2, 3]
        yield [1, 0, 0, 2, 3]
        yield [0, 1, 0, 2]
        yield [0, 0, 1]

    def given_event(self, choises_slots):

        self.handler = CreateOrUpdateDonChecksHandler(self._uowm, self.cache)

        self.don_checks_event = CreateOrUpdateDonChecks(
            game_id=self.game.game_id,
            don_checks=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.don_checks_event)

    def it_should_save_don_checks(self, choises_slots):
        our_don_checks = self._uowm.sess.don_checks.get_by_game_id(game_id=self.game.game_id)
        our_don_checks_tuples = [(don_check.circle_number, don_check.checked_house_id) for don_check in our_don_checks]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_don_checks_tuples = []
        for day, slot in enumerate(choises_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_don_checks_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_don_checks_tuples, key=lambda k: k[0]),
            sorted(expected_don_checks_tuples, key=lambda k: k[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenDonChecksIsUpdated(BaseTestHandler):

    @classmethod
    def example_slots(cls):
        # Test update one slot
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

        self.handler = CreateOrUpdateDonChecksHandler(self._uowm, self.cache)
        houses = self.cache.get_houses_by_game_id(self.game.game_id)

        for day, slot in enumerate(old_slots, start=1):
            if slot == 0:
                continue
            house = houses.get(slot)
            self._uowm.sess.don_checks.add(
                DonChecks(
                    don_check_id=f'don_check_id_{day}',
                    game_id=self.game.game_id,
                    checked_house_id=house.house_id,
                    circle_number=day
                )
            )

        self.don_checks_event = CreateOrUpdateDonChecks(
            game_id=self.game.game_id,
            don_checks=new_slots
        )

    def because_handler_process_event(self):
        self.handler(self.don_checks_event)

    def it_should_update_don_checks(self, old_slots, new_slots):
        our_don_checks = self._uowm.sess.don_checks.get_by_game_id(game_id=self.game.game_id)
        our_don_checks_tuples = [(don_check.circle_number, don_check.checked_house_id) for don_check in our_don_checks]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_don_checks_tuples = []
        for day, slot in enumerate(new_slots, start=1):
            house = houses.get(slot)
            if house is not None:
                expected_don_checks_tuples.append((day, house.house_id))

        expected_deleted_don_checks_tuples = []
        for day, slot in enumerate(old_slots, start=1):
            house = houses.get(slot)
            if house is not None and slot not in new_slots:
                expected_deleted_don_checks_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_don_checks_tuples, key=lambda k: k[0]),
            sorted(expected_don_checks_tuples, key=lambda k: k[0])
        )

        for don_check_tuple in expected_deleted_don_checks_tuples:
            assert don_check_tuple not in our_don_checks_tuples
            
    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
