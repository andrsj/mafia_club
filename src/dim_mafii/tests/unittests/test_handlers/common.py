from typing import List


from dim_mafii.domain.model import House
from dim_mafii.tests.fakes import FakeUnitOfWorkManager, FakeHouseCacheMemory
from dim_mafii.tests.fixture import prepare_game, generate_ten_slots_for_game


class BaseTestHandler:

    def given_prepare_game_and_houses(self):

        self._uowm = FakeUnitOfWorkManager()

        self._uowm.sess.clean_all()

        self.cache = FakeHouseCacheMemory()
        self.cache.clean()

        self.game = prepare_game(uow=self._uowm)

        self.houses: List[House] = generate_ten_slots_for_game(self.game.game_id)

        self.cache.add_houses_by_game(game_id=self.game.game_id, houses=self.houses)

        for house in self.houses:
            self._uowm.sess.houses.add(house)

