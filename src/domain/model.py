class Player:

    def __init__(self, nickname, name, club):
        self.nickname = nickname
        self.name = name
        self.club = club

    def __repr__(self):
        return f"Player({self.nickname})"
