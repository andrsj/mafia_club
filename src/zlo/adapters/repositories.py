from zlo.domain.model import Player, House, Game


class PlayerRepository:

    def __init__(self, session):
        self._session = session

    def get_by_nickname(self, nick: str):
        return self._session.query(Player).filter_by(nickname=nick).first()

    def get_by_id(self, player_id):
        return self._session.query(Player).filter_by(player_id=player_id).first()

    def add(self, player: Player):
        self._session.add(player)


class GameRepository:

    def __init__(self, session):
        self._session = session

    def get_by_id(self, game_id):
        return self._session.query(Game).filter_by(game_id=game_id).first()

    def get_by_datetime_range(self, start_date, end_date):
        return self._session.query(Game).filter(Game.date >= start_date).filter(Game.date <= end_date).all()

    def get_all_games(self):
        return self._session.query(Game).all()

    def add(self, game):
        self._session.add(game)


class HouseRepository:

    def __init__(self, session):
        self._session = session

    def get_by_house_id(self, house_id):
        return self._session.query(House).filter_by(haouse_id=house_id).first()

    def get_by_game_id(self, game_id):
        return self._session.query(House).filter_by(game_id=game_id).all()

    def get_by_game_id_and_player_id(self, game_id, player_id):
        return self._session.query(House).filter_by(game_id=game_id).filter_by(player_id=player_id).first()

    def add(self, house):
        self._session.add(house)


class BestMove:

    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id):
        return self._session.query(BestMove).filter_by(game_id=game_id).first()
