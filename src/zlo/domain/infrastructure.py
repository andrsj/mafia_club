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
