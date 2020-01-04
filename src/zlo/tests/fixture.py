import random
import uuid
from typing import List

from zlo.domain.model import Player, House
from zlo.domain.types import ClassicRole, HouseID

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
                player_id=player.id,
                role=ClassicRole.citizen,
                game_id=game_id,
                slot=i,
                id=HouseID(str(uuid.uuid4()))  # what to do with this stuff
            )
        )
    # first number will be sheriff
    # second -> don
    # third and fourth will be mafia
    # This 4 roles will be updated on slots based on number
    if randomize_roles:
        roles = random.sample(range(1, 11), k=4)
        houses[roles[0]].role = ClassicRole.sheriff
        houses[roles[1]].role = ClassicRole.don
        houses[roles[2]].role = ClassicRole.mafia
        houses[roles[3]].role = ClassicRole.mafia
    return houses
