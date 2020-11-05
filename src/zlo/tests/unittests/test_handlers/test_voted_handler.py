from zlo.domain.handlers import CreateOrUpdateVotedHundler
from zlo.domain.events import CreateOrUpdateVoted
from zlo.tests.unittests.test_handlers.common import BaseTestHadnler


class WhenVotedIsCreating(BaseTestHadnler):

    @classmethod
    def examples_of_days(cls):
        yield {1: [1], 2: [2]}
        yield {1: [1, 2], 2: [3, 4]}
        yield {1: [1, 2, 3], 2: [4, 5, 6]}
        yield {1: [1, 2, 3, 4]}
        yield {1: [1, 2, 3, 4, 5]}

    def given_fake_uowm_handler_and_info(self, example):
        self.handler = CreateOrUpdateVotedHundler(uowm=self._uown)

        self.days = example

        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.days
        )

    def because_handler_process_event(self):
        self.handler(self.voted_event)

    def it_should_save_voted(self):
        our_votes = self._uown.sess.voted.get_by_game_id(self.game.game_id)
        for day, slots in self.days.items():
            our_voted = [voted for voted in our_votes if voted.voted_day == day]
            for voted in our_voted:
                assert voted.voted_house_id in [
                    house.house_id for house in self.houses
                    if house.slot in self.days[day]
                ]


class WhenVotedIsUpdated(BaseTestHadnler):

    @classmethod
    def examples_of_days(cls):
        yield {1: [1], 4: [3]}
        yield {1: [1, 2], 3: [3]}
        yield {1: [1], 2: [3]}

    def given_fake_uowm_handler_and_info(self, example):
        self.handler = CreateOrUpdateVotedHundler(uowm=self._uown)

        # Create data in repository
        self.old_days = {1: [1], 3: [3]}
        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.old_days
        )
        self.handler(self.voted_event)

        # New updated data
        self.update_days = example
        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.update_days
        )

    def because_handler_process_event(self):
        self.handler(self.voted_event)

    def it_should_update_voted(self):
        our_votes = self._uown.sess.voted.get_by_game_id(self.game.game_id)
        for day, slots in self.update_days.items():
            our_voted = [voted for voted in our_votes if voted.voted_day == day]
            for voted in our_voted:
                assert voted.voted_house_id in [
                    house.house_id for house in self.houses
                    if house.slot in self.update_days[day]
                ]
