from typing import List


from zlo.domain.model import House
from zlo.tests.fakes import FakeUnitOfWorkManager
from zlo.tests.fixture import prepare_game, generate_ten_slots_for_game


class BaseTestMMRCalculator:

    def given_prepare_game_and_houses(self):

        self._uowm = FakeUnitOfWorkManager()

        self._uowm.sess.clean_all()

        self.game = prepare_game(uow=self._uowm)

        self.houses: List[House] = generate_ten_slots_for_game(self.game.game_id)

        for house in self.houses:
            self._uowm.sess.houses.add(house)
