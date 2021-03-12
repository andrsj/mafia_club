import datetime
import random
from typing import List, NamedTuple

from zlo.domain.model import Player, House, Game
from zlo.domain.types import ClassicRole, GameResult, AdvancedGameResult
from zlo.adapters.orm import SqlAlchemyUnitOfWork
from zlo.tests.fakes import FakeUnitOfWorkManager
from zlo.domain import model


# This is default players to test some basic logic
DEFAULT_PLAYERS = [
    Player(
        nickname="Zlo",
        name="Irka",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Nicolleta",
        name="Nicolleta",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Ништяк",
        name="Stas",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Червона",
        name="Червона",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Британка",
        name="Nastya",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Дюймовочка",
        name="Dima",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Mana",
        name="Marina",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="BurryBuster",
        name="Lubomur",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="Джентльмен",
        name="Den",
        club="ZloMafiaClub"
    ),
    Player(
        nickname="De Marko",
        name="Ostap",
        club="ZloMafiaClub"
    )
]

def generate_ten_slots_for_game(game_id, randomize_roles=False) -> List[House]:
    """
    Use default players to generate slots for game
    """
    houses: List[House] = []
    for i, player in enumerate(DEFAULT_PLAYERS, start=1):
        houses.append(
            House(
                player_id=player.player_id,
                role=ClassicRole.citizen.value,
                game_id=game_id,
                slot=i,
                house_id=f'{i}_house_id_test',
                fouls=0,
                bonus_mark=0.0
            )
        )
    # first number will be sheriff
    # second -> don
    # third and fourth will be mafia
    # This 4 roles will be updated on slots based on number
    if randomize_roles:
        roles = random.sample(range(1, 11), k=4)
        houses[roles[0]].role = ClassicRole.sheriff.value
        houses[roles[1]].role = ClassicRole.don.value
        houses[roles[2]].role = ClassicRole.mafia.value
        houses[roles[3]].role = ClassicRole.mafia.value
    else:
        houses[0].role = ClassicRole.sheriff.value
        houses[1].role = ClassicRole.don.value
        houses[2].role = ClassicRole.mafia.value
        houses[3].role = ClassicRole.mafia.value

    return houses

def prepare_game(
    uow: FakeUnitOfWorkManager,
    date=None,
    heading_player=None,
    game_id=None,
    table=0,
    club="ZloMafiaClub",
    result=GameResult.unfinished
) -> Game:

    if heading_player is None:
        heading_player = Player(nickname="Nata", name="Katya", club="ZloMafiaClub")
        uow.sess.players.add(heading_player)

    game = Game(
        date=date if date else datetime.datetime.utcnow(),
        game_id=game_id if game_id is not None else 'test_game_id_0',
        heading=heading_player.player_id,
        club=club,
        result=result.value,
        table=table,
        tournament=None,
        advance_result=AdvancedGameResult.guessing_game.value
    )

    uow.sess.games.add(game)
    return game

def get_house_mapper(game_id, tx: SqlAlchemyUnitOfWork):
    houses = tx.houses.get_by_game_id(game_id)
    return {house.slot: house.house_id for house in houses}

def get_result_game(matrix):
    if matrix[1][9]:
        result = 2
    elif matrix[0][9]:
        result = 1
    else:
        result = 0

    advance_result = 0
    if result == 2:
        if matrix[4][7]:
            advance_result = 1
        elif matrix[4][8]:
            advance_result = 2
        else:
            advance_result = 3
    elif result == 1:
        if matrix[4][10]:
            advance_result = 4
        else:
            advance_result = 5

    return result, advance_result


def get_excepted_models(matrix, tx: SqlAlchemyUnitOfWork):

    game_id = matrix[6][2]

    # Game model
    res, advance_res = get_result_game(matrix)
    heading = tx.players.get_by_nickname(matrix[1][2])
    game = model.Game(
        game_id=game_id,
        date=datetime.datetime.strptime(matrix[0][2], '%Y-%m-%d'),
        result=res,
        club=matrix[3][2],
        table=int(matrix[4][5]),
        tournament=matrix[4][2],
        heading=heading.player_id,
        advance_result=advance_res
    )

    # House models
    players = [tx.players.get_by_nickname(row[2]) for row in matrix[10:20]]
    players_mapper = {player.nickname: player.player_id for player in players}
    role_mapper = {'': 0, 'М': 1, 'Ш': 2, 'Д': 3}
    houses = [
        model.House(
            game_id=game_id,
            house_id='',
            player_id=players_mapper.get(row[2]),
            role=role_mapper.get(row[0]),
            slot=index,
            bonus_mark=float(row[7]) if row[7] else 0.0,
            fouls=len(row[3] + row[4] + row[5] + row[6])
        )
        for index, row in enumerate(matrix[10:20], start=1)
    ]

    # House mapper
    houses_from_db = tx.houses.get_by_game_id(game_id)
    house_mapper = {house.slot: house.house_id for house in houses_from_db}

    # Kills models
    kills = [
        model.Kills(
            game_id=game_id,
            kill_id='',
            killed_house_id=house_mapper.get(int(slot)),
            circle_number=day
        )
        for day, slot in enumerate(matrix[33][2:11], start=1)
        if slot.isdigit()
    ]

    # Voted models
    votes = [
        model.Voted(
            game_id=game_id,
            voted_id='',
            house_id=house_mapper.get(int(slot)),
            day=day
        )
        for day, slot in enumerate(matrix[44][2:11], start=1)
        if slot.isdigit()
    ]

    # Misses models
    misses = [
        model.Misses(
            game_id=game_id,
            miss_id='',
            house_id=house_mapper.get(int(slot)),
            circle_number=day
        )
        for day, slot in enumerate(matrix[34][2:11], start=1)
        if slot.isdigit()
    ]

    best_move = model.BestMove(
        game_id=game_id,
        best_move_id='',
        best_1=house_mapper.get(int(matrix[22][2])),
        best_2=house_mapper.get(int(matrix[22][3])),
        best_3=house_mapper.get(int(matrix[22][4])),
        killed_house=house_mapper.get(int(matrix[22][1])),
    )

    don_checks = [
        model.DonChecks(
            game_id=game_id,
            don_check_id='',
            circle_number=day,
            checked_house_id=house_mapper.get(int(slot))
        )
        for day, slot in enumerate(matrix[40][2:11], start=1)
        if slot.isdigit()
    ]

    hand_of_mafia = model.HandOfMafia(
        game_id=game_id,
        hand_of_mafia_id='',
        house_hand_id=house_mapper.get(int(matrix[6][8])),
        victim_id=house_mapper.get(int(matrix[6][9]))
    )

    disqualifieds = [
        model.Disqualified(
            game_id=game_id,
            disqualified_id='',
            house=house_mapper.get(int(slot))
        )
        for slot in matrix[21][7:]
        if slot.isdigit()
    ]

    sheriff_checks = [
        model.SheriffChecks(
            game_id=game_id,
            sheriff_check_id='',
            checked_house_id=house_mapper.get(int(slot)),
            circle_number=day
        )
        for day, slot in enumerate(matrix[37][2:], start=1)
        if slot.isdigit()
    ]

    sheriff_versions = [
        model.SheriffVersion(
            game_id=game_id,
            sheriff_version_id='',
            house=house_mapper.get(int(slot))
        )
        for slot in matrix[22][7:]
        if slot.isdigit()
    ]

    nominated_for_best = [
        model.NominatedForBest(
            game_id=game_id,
            nominated_for_best_id='',
            house=house_mapper.get(int(slot))
        )
        for slot in matrix[24][2:]
        if slot.isdigit()
    ]

    bonus_from_players = [
        model.BonusFromPlayers(
            game_id=game_id,
            bonus_id='',
            bonus_from=house_mapper.get(slot),
            bonus_to=house_mapper.get(int(row[8]))
        )
        for slot, row in enumerate(matrix[10:20], start=1)
        if row[8].isdigit()
    ]

    bonus_tolerant_from_players = [
        model.BonusTolerantFromPlayers(
            game_id=game_id,
            bonus_id='',
            house_from_id=house_mapper.get(slot),
            house_to_id=house_mapper.get(int(row[9]))
        )
        for slot, row in enumerate(matrix[10:20], start=1)
        if row[9].isdigit()
    ]

    class ExceptedModels(NamedTuple):
        game: model.Game
        houses: List[model.House]
        kills: List[model.Kills]
        votes: List[model.Voted]
        misses: List[model.Misses]
        best_move: model.BestMove
        don_checks: List[model.DonChecks]
        hand_of_mafia: model.HandOfMafia
        disqualifieds: List[model.Disqualified]
        sheriff_checks: List[model.SheriffChecks]
        sheriff_versions: List[model.SheriffVersion]
        nominated_for_best: List[model.NominatedForBest]
        bonus_from_players: List[model.BonusFromPlayers]
        bonus_tolerant_from_players: List[model.BonusTolerantFromPlayers]

    return ExceptedModels(
        game,
        houses,
        kills,
        votes,
        misses,
        best_move,
        don_checks,
        hand_of_mafia,
        disqualifieds,
        sheriff_checks,
        sheriff_versions,
        nominated_for_best,
        bonus_from_players,
        bonus_tolerant_from_players
    )
