import uuid
from random import randint


from expects import expect, equal
from zlo.domain.types import ClassicRole
from zlo.tests.fakes import FakeUnitOfWorkManager
from zlo.tests.unittests.test_handlers.common import BaseTestHandler
from zlo.domain.handlers import CreateOrUpdateHouseHandler
from zlo.domain.events import CreateOrUpdateHouse
from zlo.domain.model import Player, House


class WhenHouseIsCreating:

    def given_fake_uowm_handler_and_info(self):
        self._uown = FakeUnitOfWorkManager()
        self.handler = CreateOrUpdateHouseHandler(uowm=self._uown)
        self.game_id = str(uuid.uuid4())

        self.player = {
            "nickname": "Мафіозник",
            "player_id": str(uuid.uuid4()),
        }
        self._uown.sess.players.add(
            Player(
                nickname=self.player['nickname'],
                player_id=self.player['player_id'],
                name='',
                club=''
            )
        )

        self.house_event = CreateOrUpdateHouse(
            game_id=self.game_id,
            player_nickname=self.player['nickname'],
            role=ClassicRole.mafia,
            slot=randint(1, 10),
            bonus_mark=0,
            fouls=randint(0, 4)
        )

    def because_handler_process_event(self):
        self.handler(self.house_event)

    def it_should_save_house(self):
        our_house = self._uown.sess.houses.get_by_game_id_and_slot(self.game_id, self.house_event.slot)
        expect(our_house.player_id).to(equal(self.player['player_id']))
        expect(our_house.slot).to(equal(self.house_event.slot))
        expect(our_house.fouls).to(equal(self.house_event.fouls))
        expect(our_house.bonus_mark).to(equal(self.house_event.bonus_mark))
        expect(our_house.role).to(equal(self.house_event.role.value))


class WhenHouseIsUpdated(BaseTestHandler):

    def given_updated_event(self):
        self.handler = CreateOrUpdateHouseHandler(uowm=self._uowm)

        self.new_player = Player(
            nickname='TestFish',
            name='TestAndrew',
            club='TestZloClub'
        )
        self._uowm.sess.players.add(self.new_player)

        self._uowm.sess.houses.add(
            House(
                house_id='house_id_1',
                player_id=self.new_player.player_id,
                role=ClassicRole.citizen,
                slot=1,
                game_id=self.game.game_id,
                bonus_mark=0,
                fouls=0,
            )
        )

        self.house_event = CreateOrUpdateHouse(
            game_id=self.game.game_id,
            player_nickname=self.new_player.nickname,
            role=ClassicRole.mafia,
            slot=1,
            bonus_mark=0.3,
            fouls=3,
        )

    def because_handler_process_event(self):
        self.handler(self.house_event)

    def it_should_update_house(self):
        our_house = self._uowm.sess.houses.get_by_game_id_and_slot(self.game.game_id, 1)
        expect(our_house.player_id).to(equal(self.new_player.player_id))
        expect(our_house.role).to(equal(self.house_event.role.value))
        expect(our_house.bonus_mark).to(equal(self.house_event.bonus_mark))
        expect(our_house.fouls).to(equal(self.house_event.fouls))
