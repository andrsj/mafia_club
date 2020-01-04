import datetime
import uuid

from expects import expect, have_len
from zlo.domain.model import Game, Player
from zlo.domain.statistic import generate_statistic_by_date
from zlo.domain.types import GameResult, ClassicRole
from zlo.tests.fakes import FakeUnitOfWork, FakeUnitOfWorkManager
from zlo.tests.fixture import DEFAULT_PLAYERS as players, generate_ten_slots_for_game


class When_statistic_calculated_for_one_game:
    start_date = datetime.datetime.now() - datetime.timedelta(days=5)
    end_date = datetime.datetime.now() + datetime.timedelta(days=5)

    def given_fake_uow_and_games(self):
        self.heading_player = Player(nickname="Nata", name="Katya", club="ZloMafiaClub")

        self.uowm = FakeUnitOfWorkManager()
        # self.uow = FakeUnitOfWork()


        self.uowm.sess.players.add(self.heading_player)
        for player in players:
            self.uowm.sess.players.add(player)

        self.game = Game(
            date=datetime.datetime.utcnow(),
            id=str(uuid.uuid4()),
            heading=self.heading_player.id,
            club="ZloMafiaClub",
            result=GameResult.mafia,
            table=0
        )
        self.uowm.sess.games.add(self.game)

        self.houses = generate_ten_slots_for_game(self.game.id)

        self.houses[0].role = ClassicRole.don
        self.houses[1].role = ClassicRole.mafia
        self.houses[2].role = ClassicRole.mafia
        self.houses[3].role = ClassicRole.sheriff

        for slot in self.houses:
            self.uowm.sess.houses.add(slot)

    def because_statistic_run_on_them(self):
        self.result = generate_statistic_by_date(uowm=self.uowm, start_date=self.start_date, end_date=self.end_date)

    def it_should_has_non_zero_result(self):
        expect(self.result).to(have_len(10))
        print(self.result)
        assert True is False
