from random import sample
from typing import List


import contexts
from zlo.domain.model import House
from zlo.domain.handlers import CreateOrUpdateVotedHundler
from zlo.domain.events import CreateOrUpdateVoted
from zlo.tests.unittests.test_handlers.common import BaseTestHadnler


class WhenVotedIsCreating(BaseTestHadnler):

    def given_fake_uowm_handler_and_info(self):
        self.handler = CreateOrUpdateVotedHundler(uowm=self._uown)

        # Choise houses for event
        self.choises_houses: List[House] = sample(self.houses, k=3)
        self.days = {
            1: [house.slot for house in self.choises_houses[:2]],
            2: [self.choises_houses[2].slot]
        }

        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.days
        )

    def because_handler_process_event(self):
        self.handler(self.voted_event)

    def it_should_save_voted(self):
        for day, slots in self.days.items():
            our_voted = self._uown.sess.voted.get_by_game_id_and_days(self.game.game_id, day)
            for voted in our_voted:
                assert voted.voted_house_id in [house.house_id for house in self.choises_houses]
