from src.domain.model import Player


class PlayerRepository:

    def __init__(self, session):
        self._session = session

    def get_by_nickname(self, nick):
        return self._session.query(Player).filter_by(nickname=nick).first()

    def get_by_id(self, player_id):
        return self._session.query(Player).filter_by(id=player_id).first()

    def add(self, player):
        self._session.add(player)