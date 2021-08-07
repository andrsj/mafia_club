import datetime

from expects import expect, equal
from dim_mafii.domain.types import GameResult, AdvancedGameResult
from dim_mafii.tests.fakes import FakeUnitOfWorkManager
from dim_mafii.tests.unittests.test_handlers.common import BaseTestHandler
from dim_mafii.domain.handlers import CreateOrUpdateGameHandler
from dim_mafii.domain.events import CreateOrUpdateGame
from dim_mafii.domain.model import Player


class WhenGameIsCreated:

    def given_fake_uowm_handler_and_info(self):
        self._uowm = FakeUnitOfWorkManager()
        self.handler = CreateOrUpdateGameHandler(uowm=self._uowm)
        self.heading = Player(
            nickname="Gentlemen",
            name="Denis",
            club="Zlo"
        )

        self._uowm.sess.players.add(self.heading)
        self.game_id = 'test_game_id_1'
        self.date_of_game = datetime.datetime.now().utcnow()

        self.game_event = CreateOrUpdateGame(
            game_id=self.game_id,
            date=self.date_of_game,
            result=GameResult.citizen.value,
            table=0,
            club="ZloMafiaClub",
            heading=self.heading.nickname,
            advance_result=AdvancedGameResult.guessing_game.value,
            tournament='TestTournament'
        )

    def because_handler_process_event(self):
        self.handler(self.game_event)

    def it_should_save_game(self):
        our_game = self._uowm.sess.games.get_by_game_id(self.game_id)
        expect(our_game.game_id).to(equal(self.game_id))
        expect(our_game.date).to(equal(self.game_event.date))
        expect(our_game.heading).to(equal(self.heading.player_id))
        expect(our_game.result).to(equal(self.game_event.result))
        expect(our_game.advance_result).to(equal(self.game_event.advance_result))
        expect(our_game.tournament).to(equal(self.game_event.tournament))

    def cleanup(self):
        self._uowm.sess.clean_all()


class WhenGameIsUpdated(BaseTestHandler):

    def given_updated_event_game(self):
        self.heading = Player(
            nickname='TestGentlemen',
            name='TestDenis',
            club='TestMafiaClub'
        )
        self._uowm.sess.players.add(self.heading)

        self.handler = CreateOrUpdateGameHandler(uowm=self._uowm)

        # Update game from BaseTestHandler!
        # Dont need to create new game
        self.game_event = CreateOrUpdateGame(
            game_id=self.game.game_id,
            date=self.game.date,
            result=GameResult.mafia.value,
            club='TestZloMafia',
            table=3,
            tournament='TestTournament',
            heading=self.heading.nickname,
            advance_result=AdvancedGameResult.one_on_one.value,
        )

    def because_handler_process_event(self):
        self.handler(self.game_event)

    def it_should_update_game(self):
        our_game = self._uowm.sess.games.get_by_game_id(self.game.game_id)
        expect(our_game.heading).to(equal(self.heading.player_id))
        expect(our_game.result).to(equal(self.game_event.result))
        expect(our_game.advance_result).to(equal(self.game_event.advance_result))
        expect(our_game.tournament).to(equal(self.game_event.tournament))
        expect(our_game.club).to(equal(self.game_event.club))
        expect(our_game.table).to(equal(self.game_event.table))

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
