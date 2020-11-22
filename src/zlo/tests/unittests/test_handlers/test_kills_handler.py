from nose.tools import assert_list_equal
from zlo.domain.handlers import CreateOrUpdateKillsHandler
from zlo.domain.events import CreateOrUpdateKills
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenKillsIsCreated(BaseTestHandler):

    @classmethod
    def examples_slots(cls):
        yield [1, 2]
        yield [1, 2, 3, 4]
        yield [1, 0, 2, 3]
        yield [1, 0, 0, 2, 3]

    def given_event(self, choises_slots):

        self.handler = CreateOrUpdateKillsHandler(self._uowm, self.cache)

        self.kills_event = CreateOrUpdateKills(
            game_id=self.game.game_id,
            kills_slots=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.kills_event)

    def it_should_save_kills(self, choises_slots):
        our_kills = self._uowm.sess.kills.get_by_game_id(game_id=self.game.game_id)
        our_kills_tuples = [(kill.circle_number, kill.killed_house_id) for kill in our_kills]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_kills_tuples = []
        for day, slot in enumerate(choises_slots):
            house = houses.get(slot)
            if house is not None:
                expected_kills_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_kills_tuples, key=lambda k: k[0]),
            sorted(expected_kills_tuples, key=lambda k: k[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
