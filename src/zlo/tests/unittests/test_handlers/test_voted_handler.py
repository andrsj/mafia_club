from collections import defaultdict
from typing import Dict

import contexts
from nose.tools import assert_dict_equal, assert_list_equal
from zlo.domain.events import CreateOrUpdateVoted
from zlo.domain.handlers import CreateOrUpdateVotedHandler
from zlo.domain.model import House, Voted
from zlo.tests.unittests.test_handlers.common import BaseTestHandler


class WhenVotedIsCreated(BaseTestHandler):

    @classmethod
    def examples_of_days(cls):
        yield {1: [1], 2: [2]}
        yield {1: [1, 2], 2: [3, 4]}
        yield {1: [1, 2, 3], 2: [4, 5, 6]}
        yield {1: [1, 2, 3, 4]}
        yield {1: [1, 2, 3, 4, 5]}

    def given_fake_uowm_handler_and_info(self, example):

        self.handler = CreateOrUpdateVotedHandler(
            uowm=self._uowm,
            cache=self.cache
        )
        self.days = example

        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.days
        )

    def because_handler_process_event(self):
        self.handler(self.voted_event)

    def it_should_save_voted(self):
        our_votes = self._uowm.sess.voted.get_by_game_id(self.game.game_id)
        our_votes_tuples = [(voted.day, voted.house_id) for voted in our_votes]

        houses = self.cache.get_houses_by_game_id(self.game.game_id)
        expected_votes_tuples = []
        for day, slots in self.days.items():
            for slot in slots:
                house = houses[slot]
                expected_votes_tuples.append((day, house.house_id))

        assert_list_equal(
            sorted(our_votes_tuples, key=lambda v: v[0]),
            sorted(expected_votes_tuples, key=lambda v: v[0])
        )

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenVotedIsUpdated(BaseTestHandler):

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
        self.handler = CreateOrUpdateVotedHandler(uowm=self._uowm, cache=self.cache)

        for day, slots in old_days.items():
            for slot in slots:
                self._uowm.sess.voted.add(
                    Voted(
                        voted_id='voted_id_1',
                        game_id=self.game.game_id,
                        house_id=self.cache.get_houses_by_game_id(self.game.game_id)[slot],
                        day=day
                    )
                )

        # Setup new event
        self.update_days = new_days
        self.voted_event = CreateOrUpdateVoted(
            game_id=self.game.game_id,
            voted_slots=self.update_days
        )

    def because_handler_process_event(self):
        self.handler(self.voted_event)

    def it_should_remove_redundant_days_from_repo(self):
        voted_from_db = self._uowm.sess.voted.get_by_game_id(self.game.game_id)

        houses_by_slot: Dict[int, House] = self.cache.get_houses_by_game_id(self.game.game_id)
        houses_by_id: Dict[str, House] = {house.house_id: house for house in list(houses_by_slot.values())}

        saved_days = defaultdict(list)
        for voted in voted_from_db:
            saved_days[voted.day].append(houses_by_id[voted.house_id].slot)

        assert_dict_equal(dict(saved_days), self.update_days)

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


if __name__ == '__main__':
    contexts.main()
