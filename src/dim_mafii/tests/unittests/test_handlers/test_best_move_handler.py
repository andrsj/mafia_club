from random import sample
from typing import List


from expects import expect, equal

from dim_mafii.domain.model import House, BestMove
from dim_mafii.domain.handlers import CreateOrUpdateBestMoveHandler
from dim_mafii.domain.events import CreateOrUpdateBestMove
from dim_mafii.tests.unittests.test_handlers.common import BaseTestHandler


class WhenBestMoveIsCreating(BaseTestHandler):

    def given_fake_uowm_handler_and_info(self):

        self.handler = CreateOrUpdateBestMoveHandler(uowm=self._uowm, cache=self.cache)

        self.choises_houses: List[House] = sample(self.houses, k=4)

        self.best_move_event = CreateOrUpdateBestMove(
            game_id=self.game.game_id,
            killed_player_slot=self.choises_houses[0].slot,
            best_1_slot=self.choises_houses[1].slot,
            best_2_slot=self.choises_houses[2].slot,
            best_3_slot=self.choises_houses[3].slot
        )

    def because_handler_process_event(self):
        self.handler(self.best_move_event)

    def it_should_save_best_move(self):
        our_best_move = self._uowm.sess.best_moves.get_by_game_id(game_id=self.game.game_id)
        expect(our_best_move.game_id).to(equal(self.game.game_id))
        expect(our_best_move.killed_house).to(equal(self.choises_houses[0].house_id))
        expect(our_best_move.best_1).to(equal(self.choises_houses[1].house_id))
        expect(our_best_move.best_2).to(equal(self.choises_houses[2].house_id))
        expect(our_best_move.best_3).to(equal(self.choises_houses[3].house_id))

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()


class WhenBestMoveIsUpdated(BaseTestHandler):

    def given_updated_event(self):
        self.choises_houses: List[House] = sample(self.houses, k=4)

        self.handler = CreateOrUpdateBestMoveHandler(uowm=self._uowm, cache=self.cache)

        self._uowm.sess.best_moves.add(
            BestMove(
                best_move_id='best_move_id_1',
                game_id=self.game.game_id,
                killed_house=self.houses[0].house_id,
                best_1=self.houses[1].house_id,
                best_2=self.houses[2].house_id,
                best_3=self.houses[3].house_id,
            )
        )

        self.new_best_move_event = CreateOrUpdateBestMove(
            game_id=self.game.game_id,
            killed_player_slot=self.choises_houses[0].slot,
            best_1_slot=self.choises_houses[1].slot,
            best_2_slot=self.choises_houses[2].slot,
            best_3_slot=self.choises_houses[3].slot
        )

    def because_handler_process_event(self):
        self.handler(self.new_best_move_event)

    def it_should_update_best_move(self):
        our_best_move = self._uowm.sess.best_moves.get_by_game_id(game_id=self.game.game_id)
        expect(our_best_move.game_id).to(equal(self.game.game_id))
        expect(our_best_move.killed_house).to(equal(self.choises_houses[0].house_id))
        expect(our_best_move.best_1).to(equal(self.choises_houses[1].house_id))
        expect(our_best_move.best_2).to(equal(self.choises_houses[2].house_id))
        expect(our_best_move.best_3).to(equal(self.choises_houses[3].house_id))

    def cleanup(self):
        self._uowm.sess.clean_all()
        self.cache.clean()
