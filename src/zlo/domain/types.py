import enum

HouseID = str
GameID = str
PlayerID = str
ClubID = str


class ClassicRole(enum.Enum):
    citizen = 0
    mafia = 1
    sheriff = 2
    don = 3


class GameResult(enum.Enum):
    citizen = 0
    mafia = 1
    unfinished = 2


class Fouls(enum.Enum):
    zero = 0
    one = 1
    two = 2
    three = 3
    four = 4
    disqualification = 5


def check_winner(game_result: GameResult, game_role: ClassicRole) -> bool:
    if game_result == game_result.citizen and game_role in (ClassicRole.citizen, ClassicRole.sheriff):
        return True
    if game_result == game_result.mafia and game_role in (ClassicRole.mafia, ClassicRole.don):
        return True
    return False
