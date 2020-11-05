class UnitOfWork:

    def __enter__(self):
        raise NotImplementedError("enter")

    def __exit__(self, type, value, traceback):
        raise NotImplementedError("exit")

    def commit(self):
        raise NotImplementedError("commit")

    def rollback(self):
        raise NotImplementedError("rollback")


class UnitOfWorkManager:

    def start(self):
        return UnitOfWork()


class CacheMemory:

    def get_by_game_id_from_cache(self, game_id):
        raise NotImplementedError("get by game id from cache")

    def __get_by_game_id_from_db(self, game_id):
        raise NotImplementedError("get by game id from db")

    def __check_data_by_game_id_in_cache(self, game_id):
        raise NotImplementedError("check data by game id in cache")
