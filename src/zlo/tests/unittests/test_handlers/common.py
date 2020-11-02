from typing import List


from zlo.domain.model import House
from zlo.tests.fakes import FakeUnitOfWorkManager
from zlo.tests.fixture import prepare_game, generate_ten_slots_for_game


class BaseTestHadnler:

    def given_prepare_game_and_houses(self):
        self._uown = FakeUnitOfWorkManager()
        self.game = prepare_game(uow=self._uown)
        self.houses: List[House] = generate_ten_slots_for_game(self.game.game_id)

        for house in self.houses:
            self._uown.sess.houses.add(house)
