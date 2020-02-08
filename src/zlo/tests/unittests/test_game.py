import datetime
import uuid

import contexts
from expects import expect, be_none, equal
from zlo.domain.types import GameResult, AdvancedGameResult
from zlo.domain.model import Player, Game


class When_Game_is_creating:

    def given_heading(self):
        self.heading = Player(nickname="Gentlemen", name="Denis", club="Zlo")
        self.datetime = datetime.datetime.now().utcnow()

    def because_game_is_creating(self):
        self.game = Game(
            game_id=str(uuid.uuid4()),
            date=self.datetime,
            heading=self.heading,
            result=GameResult.citizen.value,
            table=0,
            club="ZloMafiaClub",
            tournament=None,
            advance_result=AdvancedGameResult.guessing_game.value
        )

    def test_it_should_store_correct_values(self):
        # expect(self.game.result).to(be_none)
        expect(self.game.date).to(equal(self.datetime))
        expect(self.game.heading.nickname).to(equal("Gentlemen"))


if __name__ == "__main__":
    contexts.main()
