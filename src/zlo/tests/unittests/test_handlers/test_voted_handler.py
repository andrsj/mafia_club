from collections import defaultdict
from typing import Dict

import contexts
import expects
from nose.tools import assert_list_equal, assert_dict_equal
from zlo.domain.events import CreateOrUpdateVoted
from zlo.domain.handlers import CreateOrUpdateVotedHandler
from zlo.domain.model import House
from zlo.tests.fakes import FakeHouseCacheMemory
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
        self.handler = CreateOrUpdateVotedHandler(
            uowm=self._uown,
            cache=FakeHouseCacheMemory()
        )
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
            our_voted = [voted for voted in our_votes if voted.day == day]
            for voted in our_voted:
                assert voted.house_id in [
                    house.house_id for house in self.houses
                    if house.slot in self.days[day]
                ]


class WhenVotedIsUpdated(BaseTestHadnler):

    @classmethod
    def examples_of_days(cls):
        # Change day when someone was voted
        yield {1: [1], 3: [3]}, {1: [1], 4: [3]}
        # Add more person to day
        yield {1: [1], 3: [3]}, {1: [1, 2], 3: [3]}
        # Change who was voted
        yield {1: [1], 3: [3]}, {1: [2], 2: [3]}
        # Remove second person who was voted
        yield {1: [1, 2]}, {1: [1]}
        # Changes second voted person
        yield {1: [1, 2]}, {1: [1, 3]}

    def given_fake_uowm_handler_and_info(self, old_days, new_days):
        self.cache = FakeHouseCacheMemory()
        self.handler = CreateOrUpdateVotedHandler(uowm=self._uown, cache=self.cache)

        self.cache.add_houses_by_game(game_id=self.game.game_id, houses=self.houses)
        # Create data in repository
        self.handler(CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=old_days
        ))

        # Setup new event
        self.update_days = new_days
        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.update_days
        )

    def because_handler_process_event(self):
        self.handler(self.voted_event)

    def it_should_remove_redundant_days_from_repo(self):
        voted_from_db = self._uown.sess.voted.get_by_game_id(self.game.game_id)

        houses_by_slot: Dict[int, House] = self.cache.get_houses_by_game_id(self.game.game_id)
        houses_by_id: Dict[str, House] = {house.house_id: house for house in list(houses_by_slot.values())}

        saved_days = defaultdict(list)
        for voted in voted_from_db:
            saved_days[voted.day].append(houses_by_id[voted.house_id].slot)

        assert_dict_equal(dict(saved_days), self.update_days)


if __name__ == '__main__':
    contexts.main()
