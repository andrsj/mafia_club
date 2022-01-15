from expects import expect, have_len
from nose.tools import assert_list_equal


from dim_mafii.domain.handlers import CreateOrUpdateNominatedForBestHandler
from dim_mafii.domain.events import CreateOrUpdateNominatedForBest
from dim_mafii.domain.model import NominatedForBest
from dim_mafii.tests.unittests.test_handlers.common import BaseTestHandler


class WhenNominatedForBestIsCreated(BaseTestHandler):

    @classmethod
    def examples_slots(cls):
        yield [1]
        yield [1, 2]
        yield [1, 2, 3]
        yield [1, 2, 3, 4]

    def given_fake_uowm_handler_and_info(self, choises_slots):
        self.handler = CreateOrUpdateNominatedForBestHandler(uowm=self._uowm, cache=self.cache)

        # Choise houses for event
        self.choises_houses = [house for house in self.houses if house.slot in choises_slots]

        self.nominated_for_best_event = CreateOrUpdateNominatedForBest(
            game_id=self.game.game_id,
            nominated_slots=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.nominated_for_best_event)

    def it_should_save_disqualifield(self, choises_slots):
        our_nominated_for_best = self._uowm.sess.nominated_for_best.get_by_game_id(self.game.game_id)
        expect(our_nominated_for_best).to(have_len(len(choises_slots)))
        for nominated_for_best in our_nominated_for_best:
            assert nominated_for_best.house in [house.house_id for house in self.choises_houses]

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenNominatedForBestIsIsUpdated(BaseTestHandler):

    @classmethod
    def example_slots(cls):
        yield [1, 2, 3], [1, 2]
        yield [1, 2], [1, 3]
        yield [1, 2, 4], [1, 3]

    def given_fake_uowm_handler_and_info(self, old_slots, new_slots):
        self.handler = CreateOrUpdateNominatedForBestHandler(uowm=self._uowm, cache=self.cache)

        self.houses_from_cache = self.cache.get_houses_by_game_id(self.game.game_id)
        for i, slot in enumerate(old_slots):
            self._uowm.sess.nominated_for_best.add(
                NominatedForBest(
                    nominated_for_best_id=f'{i}_nominated_for_best_id',
                    game_id=self.game.game_id,
                    house=self.houses_from_cache[slot].house_id
                )
            )

        self.nominated_for_best_event = CreateOrUpdateNominatedForBest(
            game_id=self.game.game_id,
            nominated_slots=new_slots
        )

    def because_handler_process_event(self):
        self.handler(self.nominated_for_best_event)

    def it_should_update_nominated_for_best(self, old_slots, new_slots):
        our_nominated_for_bests = self._uowm.sess.nominated_for_best.get_by_game_id(self.game.game_id)
        our_houses_nominated_for_bests = [nominated_for_best.house for nominated_for_best in our_nominated_for_bests]

        old_houses = [self.houses_from_cache.get(slot).house_id for slot in old_slots]
        new_houses = [self.houses_from_cache.get(slot).house_id for slot in new_slots]

        delete_houses = [house_id for house_id in old_houses if house_id not in new_houses]

        assert_list_equal(
            sorted(our_houses_nominated_for_bests),
            sorted(new_houses)
        )

        for house_id in delete_houses:
            assert house_id not in our_houses_nominated_for_bests

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
