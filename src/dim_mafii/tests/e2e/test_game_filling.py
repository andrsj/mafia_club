import json
import os

from expects import expect, equal

from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.cli.create_or_update_players import save_or_update_players_in_sheet
from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database
from dim_mafii.credentials.config import LIST_OF_PLAYERS_SPREADSHEET
from dim_mafii.domain.blank_worker import filling_one_game_in_db
from dim_mafii import config
from dim_mafii.adapters import orm
from dim_mafii.domain.utils import create_parser_for_blank_feeling
from dim_mafii.sheet_parser.client2 import SpreadSheetManager
from dim_mafii.tests import fixtures
from dim_mafii.tests.fixture import get_excepted_models, TEST_VALUE_FOR_DATE


class BlankParserMixin:
    parser = create_parser_for_blank_feeling()
    args = parser.parse_args(['--full'])

    @staticmethod
    def get_matrix_data(file_name):
        file_path = os.path.join(os.path.dirname(fixtures.__file__), file_name + '.json')
        with open(file_path, 'r') as f:
            matrix = json.load(f)
        return matrix


class WhenCleanCitizenWritten(BlankParserMixin):

    # Game 'СухаПеремогаМирних' doesn't have these models:
    # best_move = tx.best_moves.get_by_game_id(self.matrix[6][2])
    # hand_of_mafia = tx.hand_of_mafia.get_by_game_id(self.matrix[6][2])
    title = 'СухаПеремогаМирних'

    def given_matrix_of_game(self):
        self.cfg = os.environ.copy()
        setup_env_with_test_database(self.cfg)
        bootstrap(self.cfg)

        postgres_url = config.get_postgres_url(self.cfg)
        sqlalchemy = orm.make_sqlalchemy(postgres_url)
        self.unit_of_work = sqlalchemy.unit_of_work_manager()

        self.matrix = self.get_matrix_data(self.title)

        manager = SpreadSheetManager()
        sheet_players = manager.get_spreadsheet_by_id(LIST_OF_PLAYERS_SPREADSHEET)
        save_or_update_players_in_sheet(sheet_players.sheet1)

    def because_we_write_game(self):
        self.result = filling_one_game_in_db(self.matrix, TEST_VALUE_FOR_DATE, self.title, self.args)

    def it_should_return(self):
        expect(self.result).to(equal(f"Blank {self.title} was saved"))

    def it_should_save_game(self):
        with self.unit_of_work.start() as tx:
            game = tx.games.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert game == excepted_models.game

    def it_should_save_houses(self):
        with self.unit_of_work.start() as tx:
            houses = tx.houses.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            for i, j in zip(
                sorted(houses, key=lambda h: h.slot),
                sorted(excepted_models.houses, key=lambda h: h.slot)
            ):
                assert i == j

    def it_should_save_kills(self):
        with self.unit_of_work.start() as tx:
            kills = tx.kills.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert kills == excepted_models.kills

    def it_should_save_votes(self):
        with self.unit_of_work.start() as tx:
            votes = tx.voted.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert votes == excepted_models.votes

    def it_should_save_misses(self):
        with self.unit_of_work.start() as tx:
            misses = tx.misses.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert misses == excepted_models.misses

    def it_should_save_don_checks(self):
        with self.unit_of_work.start() as tx:
            don_checks = tx.don_checks.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert don_checks == excepted_models.don_checks

    def it_should_save_don_disqs(self):
        with self.unit_of_work.start() as tx:
            disqualifieds = tx.disqualifieds.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert disqualifieds == excepted_models.disqualifieds

    def it_should_save_sheriff_checks(self):
        with self.unit_of_work.start() as tx:
            sheriff_checks = tx.sheriff_checks.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert sheriff_checks == excepted_models.sheriff_checks

    def it_should_save_sheriff_vestions(self):
        with self.unit_of_work.start() as tx:
            sheriff_versions = tx.sheriff_versions.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert sheriff_versions == excepted_models.sheriff_versions

    def it_should_save_nominated_for_best(self):
        with self.unit_of_work.start() as tx:
            nominated_for_best = tx.nominated_for_best.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert nominated_for_best == excepted_models.nominated_for_best

    def it_should_save_bonus_from_players(self):
        with self.unit_of_work.start() as tx:
            bonus_from_players = tx.bonuses_from_players.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert bonus_from_players == excepted_models.bonus_from_players

    def it_should_save_bonus_tolerant_from_players(self):
        with self.unit_of_work.start() as tx:
            bonus_tolerant_from_players = tx.bonuses_tolerant.get_by_game_id(self.matrix[6][2])
            excepted_models = get_excepted_models(self.matrix, tx)
            assert bonus_tolerant_from_players == excepted_models.bonus_tolerant_from_players

    def cleanup(self):
        with self.unit_of_work.start() as tx:
            """
            Using execute function because we created schema by Metadata
            In Metadata we cant do cascade models
            https://docs.sqlalchemy.org/en/14/core/metadata.html

            We can't use query.delete() because we need to CASCADE delete

            Execute 'truncate' do all clear tables
                Players <- Games <- Houses <- Other models
            """

            tx.session.execute('TRUNCATE players CASCADE')
            tx.session.commit()
