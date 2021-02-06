import os


import inject
import contexts
from zlo.adapters.bootstrap import bootstrap
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.cli.setup_env_for_test import setup_env_with_test_database
from zlo.cli.create_or_update_players import save_or_update_players_in_sheet
from zlo.tests.fixture import get_excepted_models
from zlo.tests.fakes import Arguments
from zlo.adapters import orm
from zlo import config


from zlo.cli.feel_games_blank_2 import update_game_id, parse_and_write_in_db


class WhenGameParserFromSheet:

    def given_auth_client_and_args_and_players_in_db(self):
        self.cfg = os.environ.copy()
        setup_env_with_test_database(self.cfg)
        bootstrap(self.cfg)

        # --sheet="TestBlankForEndToEnd" --blank="TestBlank" --full
        self.args = Arguments(
            sheet_title='TestBlankForEndToEnd',
            blank_title='TestBlank',
            full=True
        )

        self.client = inject.instance(SpreadSheetClient)

        # Push players in DB from sheet
        sheet_players = self.client.client.open('СписокГравців1').sheet1
        save_or_update_players_in_sheet(sheet_players)

        postgres_url = config.get_postgres_url(self.cfg)
        sqlalchemy = orm.make_sqlalchemy(postgres_url)
        self.unit_of_work = sqlalchemy.unit_of_work_manager()

    def because_script_process_sheet(self):
        parse_and_write_in_db(self.client, self.args)

    def it_should_save_full_game(self):
        sheet = self.client.client.open(self.args.sheet_title)

        # Get one worksheet and GameID
        worksheet = sheet.worksheet(self.args.blank_title)
        game_id = worksheet.acell('D8').value

        with self.unit_of_work.start() as tx:
            matrix = self.client.get_matrix_for_one_worksheet(worksheet)

            # todo Creating all models for ALL games

            game = tx.games.get_by_game_id(game_id)
            houses = tx.houses.get_by_game_id(game_id)
            kills = tx.kills.get_by_game_id(game_id)
            votes = tx.voted.get_by_game_id(game_id)
            misses = tx.misses.get_by_game_id(game_id)
            best_move = tx.best_moves.get_by_game_id(game_id)
            don_checks = tx.don_checks.get_by_game_id(game_id)
            hand_of_mafia = tx.hand_of_mafia.get_by_game_id(game_id)
            disqualifieds = tx.disqualifieds.get_by_game_id(game_id)
            sheriff_checks = tx.sheriff_checks.get_by_game_id(game_id)
            sheriff_versions = tx.sheriff_versions.get_by_game_id(game_id)
            nominated_for_best = tx.nominated_for_best.get_by_game_id(game_id)
            bonus_from_players = tx.bonuses_from_players.get_by_game_id(game_id)
            bonus_tolerant_from_players = tx.bonuses_tolerant.get_by_game_id(game_id)

            excepted_models = get_excepted_models(matrix, tx)
            assert game == excepted_models.game
            assert houses == excepted_models.houses
            assert kills == excepted_models.kills
            assert votes == excepted_models.votes
            assert misses == excepted_models.misses
            assert best_move == excepted_models.best_move
            assert don_checks == excepted_models.don_checks
            assert hand_of_mafia == excepted_models.hand_of_mafia
            assert disqualifieds == excepted_models.disqualifieds
            assert sheriff_checks == excepted_models.sheriff_checks
            assert sheriff_versions == excepted_models.sheriff_versions
            assert nominated_for_best == excepted_models.nominated_for_best
            assert bonus_from_players == excepted_models.bonus_from_players
            assert bonus_tolerant_from_players == excepted_models.bonus_tolerant_from_players

    def cleanup(self):
        sheet = self.client.client.open(self.args.sheet_title)
        worksheet = sheet.worksheet(self.args.blank_title)
        update_game_id(worksheet, '')

        # Clear tables in DB
        with self.unit_of_work.start() as tx:
            # Using execute function because we created schema by Metadata
            # In Metadata we cant do cascade models
            # https://docs.sqlalchemy.org/en/14/core/metadata.html

            # We can't use query.delete() because we need to CASCADE delete

            # Execute 'truncate' do all clear tables
            # Players <- Games <- Houses <- Other models
            tx.session.execute('TRUNCATE players CASCADE')
            tx.session.commit()


if __name__ == '__main__':
    contexts.main()
