from typing import List


from zlo.domain.model import House
from zlo.tests.fakes import FakeUnitOfWorkManager, FakeHouseCacheMemory
from zlo.tests.fixture import prepare_game, generate_ten_slots_for_game


class BaseTestHadnler:

    def given_prepare_game_and_houses(self):
        self._uown = FakeUnitOfWorkManager()

        self._uown.sess.clean_all()

        self.cache = FakeHouseCacheMemory()
        self.cache.clean()

        self.game = prepare_game(uow=self._uown)

        self.houses: List[House] = generate_ten_slots_for_game(self.game.game_id)

        self.cache.add_houses_by_game(game_id=self.game.game_id, houses=self.houses)

        for house in self.houses:
            self._uown.sess.houses.add(house)
