from abc import ABC, abstractmethod
from typing import Dict
from uuid import UUID


from zlo.domain import model


class BaseRuleMMR(ABC):

    def __init__(self, game: model.GameInfo):
        self.game_info = game

    @abstractmethod
    def calculate_mmr(self) -> Dict[UUID, int]:
        pass
