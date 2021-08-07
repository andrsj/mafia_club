import logging

import inject as inject
from flask import request, Response
from flask.views import MethodView
from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.domain.model import Player


class PlayerView(MethodView):
    methods = ['GET', 'POST']

    @inject.params(
        uow=UnitOfWorkManager,
    )
    def __init__(self, uow):
        self.uow = uow
        self._log = logging.getLogger(__name__)

    def get(self):
        nickname = request.json["nickname"]
        with self.uow.start() as tx:
            player = tx.players.get_by_nickname(nickname)
            if player:
                # return jsonify(player)
                # todo why jsonify dont work
                return {"nickname": player.nickname, "name": player.name, "club": player.club}
            else:
                return {}

    def post(self):
        data = request.json
        try:
            with self.uow.start() as tx:
                new_player = {
                    "nickname": data["nickname"],
                    "name": data["name"],
                    "club": data["club"]
                }
                player = Player(**new_player)
                tx.players.add(player)
                tx.commit()
        except KeyError as e:
            logging.error(e)
            return Response(status=403)
        else:
            logging.info(f"Create new player with attributes {new_player}")
        return Response(status=200)
