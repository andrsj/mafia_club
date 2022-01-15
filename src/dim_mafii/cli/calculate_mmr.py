import os
from uuid import UUID
import uuid
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

import inject

from dim_mafii.domain.utils import create_parser_for_date_range
from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.domain.config import DATE_FORMAT
from dim_mafii.domain import model

from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database

@inject.params(
    uowm=UnitOfWorkManager
)
def get_mmr(uowm: UnitOfWorkManager, start_date: datetime, end_date: datetime, clubname: str):
    """
    Розраховує рейтинг гравця в межах заданих ігор
    :param uowm: Class для роботи з БД
    :param start_date: Дата початку фільтрації
    :param end_date: Дата кінця фільтрації
    :param clubname: Фільтр клубу
    :return: {nickname: MMR}
    """
    with uowm.start() as tx:
        players = tx.players.all()
        games = tx.games.get_by_datetime_range(start_date=start_date, end_date=end_date)
        votes = tx.voted.get_all_voted()
        breaks = tx.breaks.get_all_breaks()
        misses = tx.misses.get_all_misses()
        houses = tx.houses.get_all_houses()
        devises = tx.devises.get_all_devises()
        best_moves = tx.best_moves.get_all_best_moves()
        disqualifieds = tx.disqualifieds.get_all_diqsualified()
        sheriff_version = tx.sheriff_versions.get_all_versions()
        hands_of_mafia = tx.hand_of_mafia.get_all_hands_of_mafia()
        bonuses_from_players = tx.bonuses_from_players.get_all_bonuses()
        bonuses_from_heading = tx.bonuses_from_heading.get_all_bonuses()

        mmr = 1500 if clubname == 'ZLO' else 1000
        final_result: Dict[UUID, int] = {player.player_id: mmr for player in players}

        for game in [
            g for g in games
            if start_date < g.date < end_date
            and g.club == clubname
        ]:
            res1 = mmr_for_game(game, houses, final_result)
            res2 = mmr_for_best_player(game, houses, bonuses_from_players)
            res3 = mmr_for_sheriffs(game, houses) if game.result == 1 else {}
            res4 = mmr_for_sheriff_versions(game, houses, sheriff_version) if game.result == 2 else {}
            res5 = mmr_for_hand_of_mafia(game, houses, hands_of_mafia) if game.result == 2 else {}
            res6 = mmr_for_misses(game, houses, misses)
            res7 = mmr_for_voted_three(game, houses, votes, best_moves)
            res8 = mmr_for_best_move(game, houses, best_moves)
            res9 = mmr_for_disqualifields(game, houses, disqualifieds)
            res10 = mmr_for_devises(game, houses, devises)
            res11 = mmr_for_wrong_breaks(game, houses, breaks)
            res12 = mmr_for_bonuses_from_heading(game, houses, bonuses_from_heading)

            for result in (
                res1, res2, res3,
                res4, res5, res6,
                res7, res8, res9,
                res10, res11, res12
            ):
                for uuid in result:
                    final_result[uuid] += result[uuid]

        for key in {k: v for k, v in sorted(final_result.items(), key=lambda i: i[1], reverse=True)}:
            nickname = [player for player in players if player.player_id == key][0].nickname.capitalize()
            print(f'{nickname:20} {final_result.get(key)}')

    return final_result


def mmr_for_game(game: model.Game, houses: List[model.House], rating: Dict[UUID, int]):
    """
    Розрахунок ММР за ігри
    Виграв:
        1000-1700 +9
        1700-1800 +8
        1800-1900 +7
        ...
    Програв:
        1000-1700 -6
        1700-1800 -6
        1800-1900 -7
        ...
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]
    for house in houses_for_game:
        player_id: UUID = house.player_id
        if rating[player_id] <= 1700:
            mmr = (9, -6)
        elif 1700 < rating[player_id] <= 1800:
            mmr = (8, -6)
        elif 1800 < rating[player_id] <= 1900:
            mmr = (7, -7)
        else:
            mmr = (7 - rating[player_id] // 100, -7 - rating[player_id] // 200)
        if game.result == 2:
            result[player_id] += mmr[0] if house.role in [1, 3] else mmr[1]
        elif game.result == 1:
            result[player_id] += mmr[0] if house.role in [0, 2] else mmr[1]

    return result


def mmr_for_best_player(game: model.Game, houses: List[model.House], bonuses: List[model.BonusFromPlayers]):
    """
    Розраховує додаткові бали
    за кращих гравців від інших гравців
    Бали даються в випадку, якщо к-сть кращого гравця віддали
    за одного і того ж три або більше раз за одну гру (+1 MMR)
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]
    bonuses_for_game: List[model.BonusFromPlayers] = [bonus for bonus in bonuses if bonus.game_id == game.game_id]

    for house in houses_for_game:
        bonus_for_house = [bonus for bonus in bonuses_for_game if bonus.bonus_to == house.house_id]
        if len(bonus_for_house) >= 3:
            result[house.player_id] += 1

    return result


def mmr_for_sheriffs(game: model.Game, houses: List[model.House]):
    """
    Додаткові рейтингові бали за перемогу при карті Шерифа (+1 MMR)
    """
    if game.result != 1:
        return {}

    result = defaultdict(int)

    sheriffs = [house for house in houses if house.role == 2]
    sheriff_for_this_game = [house for house in sheriffs if house.game_id == game.game_id]
    if sheriff_for_this_game:
        result[sheriff_for_this_game[0].player_id] += 1

    return result

def mmr_for_sheriff_versions(
    game: model.Game,
    houses: List[model.House],
    sheriff_versions: List[model.SheriffVersion]
):
    """
    Розрахунок додаткових балів за гру шерифа від чорного
    При перемозі додаються додаткові бали (+1 MMR)
    """
    if game.result != 2:
        return {}

    result = defaultdict(int)

    # Get all mafias
    black_houses_for_game: List[model.House] = [
        house for house in houses
        if house.game_id == game.game_id
        and house.role in (1, 3)
    ]

    # Get all sheriff versions
    sheriff_versions_per_game: List[model.SheriffVersion] = [
        version for version in sheriff_versions
        if version.game_id == game.game_id
    ]

    for house in black_houses_for_game:
        # Check if mafia win and house was in sheriff version
        if house.house_id in [version.house for version in sheriff_versions_per_game]:
            result[house.player_id] += 1

    return result


def mmr_for_hand_of_mafia(
    game: model.Game,
    houses: List[model.House],
    hands_of_mafia: List[model.HandOfMafia]
):
    """
    Розрахунок штрафних балів за Руку чорних (-2 MMR)
    """
    if game.result != 2:
        return {}

    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]
    hand_of_mafia = [hand for hand in hands_of_mafia if hand.game_id == game.game_id]
    if hand_of_mafia:
        house_hand_of_mafia = [
            house for house in houses_for_game
            if house.house_id == hand_of_mafia[0].house_hand_id][0]

        result[house_hand_of_mafia.player_id] += -2

    return result


def mmr_for_misses(game: model.Game, houses: List[model.House], misses: List[model.Misses]):
    """
    Розрахунок штрафних балів за промахи при поразці чорних (-3 MMR)
    """
    if game.result != 2:
        return {}

    result = defaultdict(int)

    black_houses_per_game: List[model.House] = [
        house for house in houses
        if house.game_id == game.game_id
        and house.role in (1, 3)
    ]

    misses_per_game: List[model.Misses] = [miss for miss in misses if miss.game_id == game.game_id]

    for house in black_houses_per_game:
        if house.house_id in [miss.house_id for miss in misses_per_game]:
            result[house.player_id] += -3

    return result


def mmr_for_voted_three(
    game: model.Game,
    houses: List[model.House],
    votes: List[model.Voted],
    best_moves: List[model.BestMove]
):
    """
    Розрахунок додаткових балів або штрафів
    за підйом 3х мирних

    Мафи +2
    Мирні -2 (окрім першого вбитого)
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]
    votes_for_game_first_night: List[model.Voted] = [
        voted for voted in votes
        if voted.game_id == game.game_id
        and voted.day == 2  # START FROM 0
    ]
    best_move = [move for move in best_moves if move.game_id == game.game_id]

    # If in first night we got 3 voted
    if len(votes_for_game_first_night) >= 3:
        house_ids = [voted.house_id for voted in votes_for_game_first_night]
        voted_houses = [house for house in houses_for_game if house.house_id in house_ids]
        if all((house.role in (0, 2) for house in voted_houses)):
            for house in houses_for_game:
                # Mafia | Don
                if house.role in (1, 3):
                    result[house.player_id] += 2

                # Citizen | Sheriff
                elif house.role in (0, 2):
                    # Skip first killed house
                    if best_move and best_move[0].killed_house == house.house_id:
                        continue
                    result[house.player_id] -= 2

    return result


def mmr_for_best_move(game: model.Game, houses: List[model.House], best_moves: List[model.BestMove]):
    """
    Додаткові бали:
    Кращий хід - 2 чорних +1
    Кращий хід - 3 чорних +2
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]
    best_move = [move for move in best_moves if move.game_id == game.game_id]
    if best_move:
        houses = [
            house for house in houses_for_game
            if house.house_id in (
                best_move[0].best_1,
                best_move[0].best_2,
                best_move[0].best_3,
            )
        ]

        if len([house for house in houses if house.role in (0, 2)]) == 2:
            house = [house for house in houses_for_game if house.house_id == best_move[0].killed_house][0]
            result[house.player_id] += 1

        if len([house for house in houses if house.role in (0, 2)]) == 3:
            house = [house for house in houses_for_game if house.house_id == best_move[0].killed_house][0]
            result[house.player_id] += 2

    return result


def mmr_for_disqualifields(game: model.Game, houses: List[model.House], disqualifieds: List[model.Disqualified]):
    """
    Мінус за дискваліфікацію (5 балів)
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]
    disqualifieds_for_game = [d for d in disqualifieds if d.game_id == game.game_id]

    for disqualified in disqualifieds_for_game:
        house = [house for house in houses_for_game if house.house_id == disqualified.house][0]
        result[house.player_id] += -5

    return result


def mmr_for_devises(game: model.Game, houses: List[model.House], devises: List[model.Devise]):
    """
    MMR за заповіти
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]

    devises_for_game = [d for d in devises if d.game_id == game.game_id]

    for devise in devises_for_game:
        chosed_houses = [
            house for house in houses_for_game
            if house.house_id in [devise.house_1, devise.house_2, devise.house_3]
        ]
        killed_house = [house for house in houses_for_game if house.house_id == devise.killed_house][0]
        if killed_house.role in (0, 2):
            # If all houses is Mafia or Don and WIN citizen
            if all((house.role in (1, 3) for house in chosed_houses)) and game.result == 1:
                result[killed_house.player_id] += 1
            # If any house Citizen or Sheriff and WIN mafia
            elif any((house.role in (0, 2) for house in chosed_houses)) and game.result == 2:
                result[killed_house.player_id] += -2

    return result


def mmr_for_wrong_breaks(game: model.Game, houses: List[model.House], breaks: List[model.Break]):
    """
    MMR за злом проти своїх
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]

    breaks_for_game = [b for b in breaks if b.game_id == game.game_id]

    for break_ in breaks_for_game:
        house_to, house_from = [h for h in houses_for_game if h.house_id in [break_.house_to, break_.house_from]]
        # Злом чорного в чорного при поразці чорних
        if game.result == 1 and (house_to.role in (1, 3) and house_from.role in (1, 3)):
            result[house_from.player_id] += -2

        # Злом мирного в мирного при поразці мирних
        if game.result == 2 and (house_to.role in (0, 2) and house_from.role in (0, 2)):
            result[house_from.player_id] += -2

    return result


def mmr_for_bonuses_from_heading(game: model.Game, houses: List[model.House], bonuses: List[model.BonusHeading]):
    """
    Розрахунок MMR за додаткові бали від ведучого
    """
    result = defaultdict(int)

    houses_for_game: List[model.House] = [house for house in houses if house.game_id == game.game_id]

    bonuses_for_game = [b for b in bonuses if b.game_id == game.game_id]

    for bonus in bonuses_for_game:
        house = [h for h in houses_for_game if h.house_id == bonus.house_id][0]
        if 0.1 <= bonus.value <= 0.2:
            result[house.player_id] += 1
        elif bonus.value <= 0.4:
            result[house.player_id] += 2
        elif bonus.value >= 0.5:
            result[house.player_id] += 3

    return result

@inject.params(
    uowm=UnitOfWorkManager
)
def push_mmr_into_db(
    uowm: UnitOfWorkManager,
    rating: Dict[UUID, int],
    start_date: datetime,
    end_date: datetime,
    name_season: str
):
    # TODO push writing db logic into class?
    with uowm.start() as tx:
        season = model.Season(
            season_id=str(uuid.uuid4()),
            name=name_season,
            start=start_date,
            end=end_date
        )
        tx.season.add(season)
        tx.commit()

        for player_uuid in rating:
            tx.rating.add(
                model.Rating(
                    rating_id=str(uuid.uuid4()),
                    player=player_uuid,
                    mmr=rating[player_uuid],
                    season=season.season_id
                )
            )

        tx.commit()

if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    parser = create_parser_for_date_range()
    args = parser.parse_args()

    # start = datetime.strptime(args.start_date_of_day, DATA_FORMAT)
    start = datetime(2021, 1, 1)

    # end = datetime.strptime(args.end_date_of_day, DATA_FORMAT)
    end = datetime(2021, 1, 31)

    uowm = inject.instance(UnitOfWorkManager)
    rating = get_mmr(
        uowm,
        # start_date=datetime.strptime(args.start_date_of_day, DATA_FORMAT),
        start_date=start,
        # end_date=datetime.strptime(args.end_date_of_day, DATA_FORMAT),
        end_date=end,
        clubname='Школа Зло'  # ZLO | Школа Зло
    )

    push_mmr_into_db(uowm, rating, start, end, 'Школа ZLO Січень 2021')
