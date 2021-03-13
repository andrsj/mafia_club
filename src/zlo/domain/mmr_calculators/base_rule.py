from abc import ABC, abstractmethod
from typing import Dict, List
from uuid import UUID


from zlo.domain import model


class BaseRuleMMR(ABC):

    def __init__(self, game: model.Game, houses: List[model.House]):
        self.game = game
        self.houses = houses

    @abstractmethod
    def get_additional_data(self):
        pass

    @abstractmethod
    def calculate_mmr(self):
        pass

    @abstractmethod
    def get_mmr(self) -> Dict[UUID, int]:
        pass
