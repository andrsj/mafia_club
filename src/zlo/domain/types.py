import enum


class Role(enum.Enum):
    citizen = 0
    mafia = 1
    sheriff = 2
    don = 3


class GameResult(enum.Enum):
    citizen = 0
    mafia = 1
    unfinished = 2
