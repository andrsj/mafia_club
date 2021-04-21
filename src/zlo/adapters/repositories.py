from typing import List


from sqlalchemy.orm import Session


from zlo.domain import model


class PlayerRepository:

    def __init__(self, session: Session):
        self._session = session

    def get_by_nickname(self, nick: str) -> model.Player:
        return self._session.query(model.Player).filter_by(nickname=nick).first()

    def get_by_id(self, player_id) -> model.Player:
        return self._session.query(model.Player).filter_by(player_id=player_id).first()

    def add(self, player: model.Player):
        self._session.add(player)

    def all(self):
        return self._session.query(model.Player).all()


class GameRepository:

    def __init__(self, session: Session):
        self._session = session

    def get_by_game_id(self, game_id):
        return self._session.query(model.Game).filter_by(game_id=game_id).first()

    def get_by_datetime_range(self, start_date, end_date):
        return self._session.query(model.Game).filter(
            model.Game.date >= start_date
        ).filter(model.Game.date <= end_date).all()

    def get_by_name_club(self, name):
        return self._session.query(model.Game).filter(club=name).all()

    def get_all_games(self):
        return self._session.query(model.Game).all()

    def add(self, game: model.Game):
        self._session.add(game)


class HouseRepository:

    def __init__(self, session: Session):
        self._session = session

    def get_all_houses(self):
        return self._session.query(model.House).all()

    def get_by_house_id(self, house_id) -> model.House:
        return self._session.query(model.House).filter_by(house_id=house_id).first()

    def get_by_game_id(self, game_id) -> List[model.House]:
        return self._session.query(model.House).filter_by(game_id=game_id).all()

    def get_by_game_id_and_player_id(self, game_id, player_id) -> model.House:
        return self._session.query(model.House).filter_by(game_id=game_id).filter_by(player_id=player_id).first()

    def get_by_game_id_and_slot(self, game_id, slot) -> model.House:
        return self._session.query(model.House).filter_by(game_id=game_id).filter_by(slot=slot).first()

    def add(self, house: model.House):
        self._session.add(house)


class BestMoveRepository:

    def __init__(self, session: Session):
        self._session = session

    def get_all_best_moves(self):
        return self._session.query(model.BestMove).all()

    def get_by_game_id(self, game_id) -> model.BestMove:
        return self._session.query(model.BestMove).filter_by(game_id=game_id).first()

    def add(self, best_move: model.BestMove):
        self._session.add(best_move)


class SheriffVersionRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_versions(self):
        return self._session.query(model.SheriffVersion).all()

    def get_by_game_id(self, game_id) -> List[model.SheriffVersion]:
        return self._session.query(model.SheriffVersion).filter_by(game_id=game_id).all()

    def get_by_game_id_and_slot(self, game_id, slot) -> model.SheriffVersion:
        return self._session.query(model.SheriffVersion).filter_by(game_id=game_id)\
            .join(model.House).filter(model.House.slot == slot).all()

    def add(self, sheriff_version: model.SheriffVersion):
        self._session.add(sheriff_version)

    def delete(self, sheriff_version: model.SheriffVersion):
        self._session.query(model.SheriffVersion).filter_by(
            sheriff_version_id=sheriff_version.sheriff_version_id).delete()


class DisqualifiedRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_diqsualified(self):
        return self._session.query(model.Disqualified).all()

    def get_by_game_id(self, game_id) -> List[model.Disqualified]:
        return self._session.query(model.Disqualified).filter_by(game_id=game_id).all()

    def add(self, disqualified: model.Disqualified):
        self._session.add(disqualified)


class NominatedForBestRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[model.NominatedForBest]:
        return self._session.query(model.NominatedForBest).filter_by(game_id=game_id).all()

    def add(self, nominated_for_best: model.NominatedForBest):
        self._session.add(nominated_for_best)

    def delete(self, nominated_for_best: model.NominatedForBest):
        self._session.query(model.NominatedForBest).filter_by(
            nominated_for_best_id=nominated_for_best.nominated_for_best_id
        ).delete()


class VotedRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_voted(self):
        return self._session.query(model.Voted).all()

    def get_by_game_id(self, game_id) -> List[model.Voted]:
        return self._session.query(model.Voted).filter_by(game_id=game_id).all()

    def add(self, voted: model.Voted):
        self._session.add(voted)

    def delete(self, voted: model.Voted):
        self._session.query(model.Voted).filter_by(voted_id=voted.voted_id).delete()


class HandOfMafiaRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_hands_of_mafia(self):
        return self._session.query(model.HandOfMafia).all()

    def get_by_game_id(self, game_id) -> List[model.HandOfMafia]:
        return self._session.query(model.HandOfMafia).filter_by(game_id=game_id).first()

    def add(self, hand_of_mafia: model.HandOfMafia):
        self._session.add(hand_of_mafia)


class KillsRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[model.Kills]:
        return self._session.query(model.Kills).filter_by(game_id=game_id).all()

    def add(self, kill: model.Kills):
        self._session.add(kill)

    def delete(self, kill: model.Kills):
        self._session.query(model.Kills).filter_by(kill_id=kill.kill_id).delete()


class MissesRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_misses(self):
        return self._session.query(model.Misses).all()

    def get_by_game_id(self, game_id) -> List[model.Misses]:
        return self._session.query(model.Misses).filter_by(game_id=game_id).all()

    def add(self, miss: model.Misses):
        self._session.add(miss)

    def delete(self, miss: model.Misses):
        self._session.query(model.Misses).filter_by(miss_id=miss.miss_id).delete()


class DonChecksRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[model.DonChecks]:
        return self._session.query(model.DonChecks).filter_by(game_id=game_id).all()

    def add(self, don_check: model.DonChecks):
        self._session.add(don_check)

    def delete(self, don_check: model.DonChecks):
        self._session.query(model.DonChecks).filter_by(don_check_id=don_check.don_check_id).delete()


class SheriffChecksRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[model.SheriffChecks]:
        return self._session.query(model.SheriffChecks).filter_by(game_id=game_id).all()

    def add(self, sheriff_check: model.SheriffChecks):
        self._session.add(sheriff_check)

    def delete(self, sheriff_check: model.SheriffChecks):
        self._session.query(model.SheriffChecks).filter_by(sheriff_check_id=sheriff_check.sheriff_check_id).delete()


class BonusTolerantRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_game_id(self, game_id) -> List[model.BonusTolerantFromPlayers]:
        return self._session.query(model.BonusTolerantFromPlayers).filter_by(game_id=game_id).all()

    def add(self, bonus: model.BonusTolerantFromPlayers):
        self._session.add(bonus)

    def delete(self, bonus: model.BonusTolerantFromPlayers):
        self._session.query(model.BonusTolerantFromPlayers).filter_by(bonus_id=bonus.bonus_id).delete()


class BonusFromPlayersRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_bonuses(self):
        return self._session.query(model.BonusFromPlayers).all()

    def get_by_game_id(self, game_id) -> List[model.BonusFromPlayers]:
        return self._session.query(model.BonusFromPlayers).filter_by(game_id=game_id).all()

    def add(self, bonus: model.BonusFromPlayers):
        self._session.add(bonus)

    def delete(self, bonus: model.BonusFromPlayers):
        self._session.query(model.BonusFromPlayers).filter_by(bonus_id=bonus.bonus_id).delete()


class BonusHeadingRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_bonuses(self):
        return self._session.query(model.BonusHeading).all()

    def add(self, bonus: model.BonusHeading):
        self._session.add(bonus)

    def get_by_game_id(self, game_id) -> List[model.BonusHeading]:
        return self._session.query(model.BonusHeading).filter_by(game_id=game_id).all()

    def delete(self, bonus: model.BonusHeading):
        self._session.query(model.BonusHeading).filter_by(bonus_id=bonus.bonus_id).delete()


class DeviseRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_devises(self):
        return self._session.query(model.Devise).all()

    def add(self, devise: model.Devise):
        self._session.add(devise)

    def get_by_game_id(self, game_id) -> List[model.Devise]:
        return self._session.query(model.Devise).filter_by(game_id=game_id).all()

    def delete(self, devise: model.Devise):
        self._session.query(model.Devise).filter_by(devise_id=devise.devise_id).delete()


class BreakRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_breaks(self):
        return self._session.query(model.Break).all()

    def add(self, break_: model.Break):
        self._session.add(break_)

    def get_by_game_id(self, game_id) -> List[model.Break]:
        return self._session.query(model.Break).filter_by(game_id=game_id).all()

    def delete(self, break_: model.Break):
        self._session.query(model.Break).filter_by(break_id=break_.break_id).delete()


class RatingRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_ratings(self) -> List[model.Rating]:
        return self._session.query(model.Rating).all()

    def add(self, rating: model.Rating):
        self._session.add(rating)

    def delete(self, rating: model.Rating):
        self._session.query(model.Rating).filter_by(rating_id=rating.rating_id).delete()


class SeasonRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_seasons(self) -> List[model.Season]:
        return self._session.query(model.Season).all()

    def add(self, season: model.Season):
        self._session.add(season)

    def delete(self, season: model.Season):
        self._session.query(model.Rating).filter_by(season_id=season.season_id).delete()

    def get_by_name(self, name: str):
        self._session.query(model.Rating).filter_by(name=name).first()
