import logging

import inject
from flask import request
from flask.views import View

from src.zlo.domain.infrastructure import UnitOfWorkManager


class GameView(View):
    methods = ['GET']

    @inject.params(
        uow=UnitOfWorkManager,
    )
    def __init__(self, uow):
        self.uow = uow
        self._log = logging.getLogger(__name__)

    def dispatch_request(self):
        data = request.get_json()
