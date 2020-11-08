class UnitOfWork:

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, type, value, traceback):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError


class UnitOfWorkManager:

    def start(self):
        return UnitOfWork()


class CacheMemory:

    def get_houses_by_game_id(self, game_id):
        raise NotImplementedError

    def __check_data_by_game_id_in_cache(self, game_id):
        raise NotImplementedError
