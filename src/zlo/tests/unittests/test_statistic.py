# import datetime
#
# from expects import expect, have_len, be_above_or_equal, be_below
# from zlo.domain.statistic import generate_statistic_by_date
# from zlo.domain.types import GameResult, ClassicRole
# from zlo.tests.fakes import FakeUnitOfWorkManager
# from zlo.tests.fixture import DEFAULT_PLAYERS as players, generate_ten_slots_for_game, prepare_game


# class When_statistic_calculated_for_one_game:
#     start_date = datetime.datetime.now() - datetime.timedelta(days=5)
#     end_date = datetime.datetime.now() + datetime.timedelta(days=5)
#
#     def given_fake_uow_and_games(self):
#         self.uowm = FakeUnitOfWorkManager()
#
#         for player in players:
#             self.uowm.sess.players.add(player)
#
#         self.game = prepare_game(self.uowm.sess, result=GameResult.mafia)
#
#         self.houses = generate_ten_slots_for_game(self.game.game_id)
#
#         self.houses[0].role = ClassicRole.don
#         self.houses[1].role = ClassicRole.mafia
#         self.houses[2].role = ClassicRole.mafia
#         self.houses[3].role = ClassicRole.sheriff
#
#         for slot in self.houses:
#             self.uowm.sess.houses.add(slot)
#
#     def because_statistic_run_on_them(self):
#         self.result = generate_statistic_by_date(uowm=self.uowm, start_date=self.start_date, end_date=self.end_date)
#
#     def it_should_has_non_zero_result(self):
#         expect(self.result).to(have_len(10))
#
#     def it_should_add_marks_for_mafia(self):
#         # print("Len of games in session", len(self.uowm.sess.games.games))
#         for player, mark in list(self.result.items())[:3]:
#             # print(player, mark)
#             expect(mark).to(be_above_or_equal(1))
#
#     def it_should_not_add_marks_for_citizens(self):
#         # print("Len of games in session", len(self.uowm.sess.games.games))
#         for player, mark in list(self.result.items())[3:]:
#             # print(player, mark)
#             expect(mark).to(be_below(1))
#
#
# class When_statistic_calculated_for_more_than_one_game:
#     start_date = datetime.datetime.now() - datetime.timedelta(days=5)
#     end_date = datetime.datetime.now() + datetime.timedelta(days=5)
#
#     def given_fake_uow_and_games(self):
#         self.uowm = FakeUnitOfWorkManager()
#
#         for player in players:
#             self.uowm.sess.players.add(player)
#
#         # Create two games
#         self.game_one = prepare_game(self.uowm.sess, result=GameResult.citizen)
#         self.game_two = prepare_game(self.uowm.sess, result=GameResult.mafia)
#
#         # for each game generate 10 houses with citizen roles
#         self.houses_game_one = generate_ten_slots_for_game(self.game_one.game_id)
#         self.houses_game_two = generate_ten_slots_for_game(self.game_two.game_id)
#
#         # Prepare roles for first game
#         self.houses_game_one[0].role = ClassicRole.don
#         self.houses_game_one[1].role = ClassicRole.mafia
#         self.houses_game_one[2].role = ClassicRole.mafia
#         self.houses_game_one[3].role = ClassicRole.sheriff
#
#         # Prepare roles for second game
#         self.houses_game_two[0].role = ClassicRole.don
#         self.houses_game_two[1].role = ClassicRole.mafia
#         self.houses_game_two[2].role = ClassicRole.mafia
#         self.houses_game_two[3].role = ClassicRole.sheriff
#
#         for house_game_one in self.houses_game_one:
#             self.uowm.sess.houses.add(house_game_one)
#
#         for house_game_two in self.houses_game_two:
#             self.uowm.sess.houses.add(house_game_two)
#
#     def because_statistic_run_on_them(self):
#         self.result = generate_statistic_by_date(uowm=self.uowm, start_date=self.start_date, end_date=self.end_date)
#
#     def it_should_has_non_zero_result(self):
#         expect(self.result).to(have_len(10))
#
#     def it_should_has_one_mark_for_every_player(self):
#         for value in self.result.values():
#             expect(value).to(be_above_or_equal(1))
