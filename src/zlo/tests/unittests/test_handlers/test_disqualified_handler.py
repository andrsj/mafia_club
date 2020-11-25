from expects import expect, have_len
from nose.tools import assert_list_equal


from zlo.domain.handlers import CreateOrUpdateDisqualifiedHandler
from zlo.domain.events import CreateOrUpdateDisqualified
from zlo.domain.model import Disqualified
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenDisqualiefieldIsCreated(BaseTestHandler):

    @classmethod
    def examples_slots(cls):
        yield [1]
        yield [1, 2]
        yield [1, 2, 3]
        yield [1, 2, 3, 4]

    def given_fake_uowm_handler_and_info(self, choises_slots):
        self.handler = CreateOrUpdateDisqualifiedHandler(uowm=self._uowm, cache=self.cache)

        # Choise houses for event
        self.choises_houses = [house for house in self.houses if house.slot in choises_slots]

        self.disqualifield_event = CreateOrUpdateDisqualified(
            game_id=self.game.game_id,
            disqualified_slots=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.disqualifield_event)

    def it_should_save_disqualifield(self, choises_slots):
        our_disqualifields = self._uowm.sess.disqualifieds.get_by_game_id(self.game.game_id)
        expect(our_disqualifields).to(have_len(len(choises_slots)))
        for disqualifield in our_disqualifields:
            assert disqualifield.house in [house.house_id for house in self.choises_houses]

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenDisqualiefieldIsIsUpdated(BaseTestHandler):

    @classmethod
    def example_slots(cls):
        yield [1, 2, 3], [1, 2]
        yield [1, 2], [1, 3]
        yield [1, 2, 4], [1, 3]

    def given_fake_uowm_handler_and_info(self, old_slots, new_slots):
        self.handler = CreateOrUpdateDisqualifiedHandler(uowm=self._uowm, cache=self.cache)

        self.houses_from_cache = self.cache.get_houses_by_game_id(self.game.game_id)
        for i, slot in enumerate(old_slots):
            self._uowm.sess.disqualifieds.add(
                Disqualified(
                    disqualified_id=f'{i}_disqualified_id',
                    game_id=self.game.game_id,
                    house=self.houses_from_cache[slot].house_id
                )
            )

        self.disqualifield_event = CreateOrUpdateDisqualified(
            game_id=self.game.game_id,
            disqualified_slots=new_slots
        )

    def because_handler_process_event(self):
        self.handler(self.disqualifield_event)

    def it_should_update_disqualifield(self, old_slots, new_slots):
        our_disqualifields = self._uowm.sess.disqualifieds.get_by_game_id(self.game.game_id)
        our_houses_disqualifields = [disqualifield.house for disqualifield in our_disqualifields]

        old_houses = [self.houses_from_cache.get(slot).house_id for slot in old_slots]
        new_houses = [self.houses_from_cache.get(slot).house_id for slot in new_slots]

        delete_houses = [house_id for house_id in old_houses if house_id not in new_houses]

        assert_list_equal(
            sorted(our_houses_disqualifields),
            sorted(new_houses)
        )

        for house_id in delete_houses:
            assert house_id not in our_houses_disqualifields

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
