from abc import ABCMeta, abstractmethod


class UnitOfWork(metaclass=ABCMeta):

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


class UnitOfWorkManager(metaclass=ABCMeta):

    @abstractmethod
    def start(self):
        pass


class HouseCacheMemory(metaclass=ABCMeta):

    @abstractmethod
    def get_houses_by_game_id(self, game_id):
        pass
