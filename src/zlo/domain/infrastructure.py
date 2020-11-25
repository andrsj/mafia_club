from abc import ABC, abstractmethod
from dataclasses import dataclass


class UnitOfWork(ABC):

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class UnitOfWorkManager(ABC):

    @abstractmethod
    def start(self):
        pass


class HouseCacheMemory(ABC):

    @abstractmethod
    def get_houses_by_game_id(self, game_id):
        pass


@dataclass
class EventHouseModel:
    day: int
    house_id: str
