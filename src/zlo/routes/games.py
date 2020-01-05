import datetime
import logging
import uuid

import inject as inject
from flask import json, Response, jsonify, request
from flask.views import MethodView
from src.zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Game

from dateutil import parser


class GamesView(MethodView):
    methods = ['GET', "POST"]

    @inject.params(
        uow=UnitOfWorkManager,
    )
    def __init__(self, uow):
        self.uow = uow
        self._log = logging.getLogger(__name__)

    def get(self):
        with self.uow.start() as tx:
            games = tx.games.get_all_games()
            result = [json.dumps(game) for game in games]
            return jsonify(result)

    def post(self):
        data = request.json
        """
            game_id=str(uuid.uuid4()),
            date=self.datetime,
            heading=self.heading,
            result=None,
            table=0,
            club="ZloMafiaClub",
            tournament=None
        """
        try:
            with self.uow.start() as tx:
                player = tx.players.get_by_nickname(data["heading"])

                new_game = {
                    "game_id": data.get("game_id") or uuid.uuid4(),
                    "date": parser.parse(data["date"]),
                    "heading": player.player_id,
                    "result": data.get("result") or 0,
                    "table": data.get("table") or 0,
                    "club": data.get("club") or "ZLO",
                    "tournament": data.get("tournament") or 0
                }
                game = Game(**new_game)
                tx.games.add(game)
        except KeyError as e:
            logging.error(e)
            return Response(status=403)
        else:
            logging.info(f"Create game with attributes {new_game}")
        return Response(status=200)
