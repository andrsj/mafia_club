from typing import List
import uuid


from dim_mafii.domain.model import House
from dim_mafii.domain.game_info_builder import GameInfoBuilder
from dim_mafii.tests.fakes import FakeUnitOfWorkManager
from dim_mafii.tests.fixture import prepare_game, generate_ten_slots_for_game


class BaseTestMMRCalculator:

    def given_prepare_game_and_houses(self):

        self._uowm = FakeUnitOfWorkManager()

        self._uowm.sess.clean_all()

        self.game = prepare_game(uow=self._uowm)

        self.houses: List[House] = generate_ten_slots_for_game(self.game.game_id)

        for house in self.houses:
            self._uowm.sess.houses.add(house)

        self.game_builder = GameInfoBuilder().\
            with_game(game=self.game).\
            with_houses(houses=self.houses)

    def cleanup(self):
        self._uowm.sess.clean_all()


def generate_uuid():
    return str(uuid.uuid4())
