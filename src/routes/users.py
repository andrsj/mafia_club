import logging

import inject as inject
from flask.views import View

from src.domain.infrastructure import UnitOfWorkManager
from src.domain.model import Player


class PlayerView(View):
    methods = ['GET']

    @inject.params(
        uow=UnitOfWorkManager,
    )
    def __init__(self, uow):
        self.uow = uow
        self._log = logging.getLogger(__name__)

    def dispatch_request(self, p_id):
        with self.uow.start() as tx:
            player = tx.players.get_by_id(p_id)
            if player:
                return f"ID {player.id}, Nickname {player.nickname}," \
                       f" Name {player.name}, Club {player.club}"
            else:
                return "No such player found"
