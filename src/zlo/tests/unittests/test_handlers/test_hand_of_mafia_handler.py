import contexts
from expects import expect, equal
from zlo.domain.handlers import CreateOrUpdateHandOfMafiaHandler
from zlo.domain.events import CreateOrUpdateHandOfMafia
from zlo.domain.model import HandOfMafia
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenHandOfMafiaIsCreating(BaseTestHandler):

    def given_event(self):

        self.handler = CreateOrUpdateHandOfMafiaHandler(uowm=self._uowm, cache=self.cache)

        self.choises_houses = [self.houses[0], self.houses[1]]

        self.hand_of_mafia_event = CreateOrUpdateHandOfMafia(
            game_id=self.game.game_id,
            slot_from=self.choises_houses[0].slot,
            slot_to=self.choises_houses[1].slot
        )

    def because_handler_process_event(self):
        self.handler(self.hand_of_mafia_event)

    def it_should_save_hand_of_mafia(self):
        our_hand_of_mafia: HandOfMafia = self._uowm.sess.hand_of_mafia.get_by_game_id(self.game.game_id)
        expect(our_hand_of_mafia.house_hand_id).to(equal(self.choises_houses[0].house_id))
        expect(our_hand_of_mafia.victim_id).to(equal(self.choises_houses[1].house_id))


class WhenHandOfMafiaIsUpdated(BaseTestHandler):
    def given_event(self):

        self.handler = CreateOrUpdateHandOfMafiaHandler(uowm=self._uowm, cache=self.cache)

        self._uowm.sess.hand_of_mafia.add(
            HandOfMafia(
                hand_of_mafia_id='hand_of_maifa_id_1',
                game_id=self.game.game_id,
                house_hand_id=self.houses[0].house_id,
                victim_id=self.houses[0].house_id,
            )
        )

        self.choises_houses = [self.houses[2], self.houses[3]]

        self.new_hand_of_mafia_event = CreateOrUpdateHandOfMafia(
            game_id=self.game.game_id,
            slot_from=self.choises_houses[0].slot,
            slot_to=self.choises_houses[1].slot
        )

    def because_handler_process_event(self):
        self.handler(self.new_hand_of_mafia_event)

    def it_should_update_hand_of_mafia(self):
        our_hand_of_mafia: HandOfMafia = self._uowm.sess.hand_of_mafia.get_by_game_id(self.game.game_id)
        expect(our_hand_of_mafia.house_hand_id).to(equal(self.choises_houses[0].house_id))
        expect(our_hand_of_mafia.victim_id).to(equal(self.choises_houses[1].house_id))
