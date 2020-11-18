from typing import List


from zlo.domain.model import (
    Game,
    House,
    Kills,
    Voted,
    Devise,
    Player,
    BestMove,
    DonChecks,
    HandOfMafia,
    Disqualified,
    SheriffChecks,
    SheriffVersion,
    NominatedForBest,
    BonusPointsFromPlayers,
    BonusTolerantPointFromPlayers
)


class PlayerRepository:

    def __init__(self, session):
        self._session = session

    def get_by_nickname(self, nick: str):
        return self._session.query(Player).filter_by(nickname=nick).first()

    def get_by_id(self, player_id):
        return self._session.query(Player).filter_by(player_id=player_id).first()

    def add(self, player: Player):
        self._session.add(player)

    def all(self):
        return self._session.query(Player).all()


class GameRepository:

    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id):
        return self._session.query(Game).filter_by(game_id=game_id).first()

    def get_by_datetime_range(self, start_date, end_date):
        return self._session.query(Game).filter(Game.date >= start_date).filter(Game.date <= end_date).all()

    def get_all_games(self):
        return self._session.query(Game).all()

    def add(self, game: Game):
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

    def get_by_game_id_and_slot(self, game_id, slot):
        return self._session.query(House).filter_by(game_id=game_id).filter_by(slot=slot).first()

    def add(self, house: House):
        self._session.add(house)


class BestMoveRepository:

    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id) -> BestMove:
        return self._session.query(BestMove).filter_by(game_id=game_id).first()

    def add(self, best_move: BestMove):
        self._session.add(best_move)


class SheriffVersionRepository:
    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[SheriffVersion]:
        return self._session.query(SheriffVersion).filter_by(game_id=game_id).all()

    def get_by_game_id_and_slot(self, game_id, slot) -> SheriffVersion:
        return self._session.query(SheriffVersion).filter_by(game_id=game_id)\
            .join(House).filter(House.slot == slot).all()

    def add(self, sheriff_version: SheriffVersion):
        self._session.add(sheriff_version)


class DisqualifiedRepository:
    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[Disqualified]:
        return self._session.query(Disqualified).filter_by(game_id=game_id).all()

    def add(self, disqualified: Disqualified):
        self._session.add(disqualified)


class NominatedForBestRepository:
    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[NominatedForBest]:
        return self._session.query(NominatedForBest).filter_by(game_id=game_id).all()

    def add(self, nominated_for_best: NominatedForBest):
        self._session.add(nominated_for_best)


class VotedRepository:
    def __init__(self, session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[Voted]:
        return self._session.query(Voted).filter_by(game_id=game_id).all()

    def add(self, voted: Voted):
        self._session.add(voted)

    def delete(self, voted: Voted):
        self._session.query(Voted).filter_by(Voted.voted_id == voted.voted_id).delete()
