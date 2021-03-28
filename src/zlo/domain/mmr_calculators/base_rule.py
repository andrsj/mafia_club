from abc import ABC, abstractmethod
from typing import Dict, Optional
from uuid import UUID


from zlo.domain import model


Rating = Dict[UUID, int]


class BaseRuleMMR(ABC):

    def __init__(self, game: model.GameInfo):
        self.game_info = game

    @abstractmethod
    def calculate_mmr(self, rating: Optional[Rating] = None) -> Rating:
        pass
