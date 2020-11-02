from expects import expect, equal, have_len
from zlo.domain.handlers import CreateOrUpdateKillsHandler
from zlo.domain.events import CreateOrUpdateKills
from zlo.tests.unittests.test_handlers.common import BaseTestHadnler


class WhenKillsIsCreating(BaseTestHadnler):

    @classmethod
    def examples_slots(cls):
        yield [1, 2]
        yield [1, 2, 3]
        yield [1, 2, 3, 4]
        yield [1, 0, 2, 3]
        yield [1, 0, 0, 2, 3]

    def given_event(self, choises_slots):

        self.handler = CreateOrUpdateKillsHandler(self._uown)

        self.choises_houses = [house for house in self.houses if house.slot in choises_slots]

        self.kills_event = CreateOrUpdateKills(
            game_id=self.game.game_id,
            kills_slots=choises_slots
        )

    def because_handler_process_event(self):
        self.handler(self.kills_event)

    def it_should_save_kills(self, choises_slots):
        our_kills = self._uown.sess.kills.get_by_game_id(game_id=self.game.game_id)

        # For save order of zero number houses (no house)
        # For example [1, 0, 2, 3] => [House1, None, House2, House3]
        killed_houses_expected = []
        for slot in choises_slots:
            killed_houses_expected.append(
                next(filter(lambda house_: house_.slot == slot, self.houses), None)
            )

        # Get dict like {day: house_id} for tests
        circles = {day: house.house_id if house is not None else None for day, house in enumerate(
            killed_houses_expected,
            start=1
        )}

        expect(our_kills).to(have_len(len([slot for slot in choises_slots if slot])))
        for our_kill in our_kills:
            expect(our_kill.killed_house_id).to(equal(circles[our_kill.circle_number]))
