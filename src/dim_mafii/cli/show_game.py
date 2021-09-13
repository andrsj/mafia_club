import argparse
import os
from datetime import datetime


import inject

from dim_mafii.domain.config import DATE_FORMAT
from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.domain.utils import get_house_from_list_by_house_id, get_houses_from_list_of_house_ids
from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database
from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.domain.game_info_builder import GameInfoBuilder


if __name__ == "__main__":
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    parser = argparse.ArgumentParser(description='Show full game info')
    parser.add_argument(
        '--game_id',
        dest='game_id'
    )
    parser.add_argument(
        '--date',
        dest='date'
    )
    args = parser.parse_args()

    uowm = inject.instance(UnitOfWorkManager)

    with uowm.start() as tx:
        games = []
        if args.date:
            date = datetime.strptime(args.date, DATE_FORMAT)
            games = tx.games.get_by_datetime_range(start_date=date, end_date=date)

        if args.game_id:
            games = [tx.games.get_by_game_id(args.game_id)]

        for game in games:
            game_info = GameInfoBuilder(). \
                with_game(game=game). \
                with_houses(houses=tx.houses.get_by_game_id(game.game_id)). \
                with_kills(kills=tx.kills.get_by_game_id(game.game_id)). \
                with_votes(votes=tx.voted.get_by_game_id(game.game_id)). \
                with_breaks(breaks=tx.breaks.get_by_game_id(game.game_id)). \
                with_misses(misses=tx.misses.get_by_game_id(game.game_id)). \
                with_devises(devises=tx.devises.get_by_game_id(game.game_id)). \
                with_don_checks(don_checks=tx.don_checks.get_by_game_id(game.game_id)). \
                with_best_move(best_move=tx.best_moves.get_by_game_id(game.game_id)). \
                with_disqualifieds(disqualifieds=tx.disqualifieds.get_by_game_id(game.game_id)). \
                with_sheriff_checks(sheriff_checks=tx.sheriff_checks.get_by_game_id(game.game_id)). \
                with_hand_of_mafia(hand_of_mafia=tx.hand_of_mafia.get_by_game_id(game.game_id)). \
                with_sheriff_versions(sheriff_versions=tx.sheriff_versions.get_by_game_id(game.game_id)). \
                with_nominated_for_best(nominated_for_best=tx.nominated_for_best.get_by_game_id(game.game_id)). \
                with_bonuses_from_player(bonuses=tx.bonuses_from_players.get_by_game_id(game.game_id)). \
                with_bonuses_from_heading(bonuses=tx.bonuses_from_heading.get_by_game_id(game.game_id)). \
                with_bonuses_for_tolerant(bonuses=tx.bonuses_tolerant.get_by_game_id(game.game_id)). \
                build()

            print(game_info.game)
            print(f'\tHeading nickname: \'{tx.players.get_by_id(game_info.game.heading).nickname}\'\n')

            for house in game_info.houses:
                print(
                    f"\tHouse:"
                    f"  Nickname: {tx.players.get_by_id(house.player_id).nickname:<15s}"
                    f"  Role: {house.role}"
                    f"  Slot: {house.slot}"
                    f"  Bonus: {house.bonus_mark}"
                    f"  Fouls: {house.fouls}"
                )

            print()

            for kill in game_info.kills:
                killed_house = get_house_from_list_by_house_id(game_info.houses, kill.killed_house_id)
                print('\tKilled | slot:', killed_house.slot, 'Day:', kill.circle_number)

            for vote in game_info.votes:
                voted_house = get_house_from_list_by_house_id(game_info.houses, vote.house_id)
                print('\tVoted | slot:', voted_house.slot, 'Vote day', vote.day)

            for check in game_info.sheriff_checks:
                print('\tSheriff check | day:', check.circle_number,
                      'Slot:', get_house_from_list_by_house_id(game_info.houses, check.checked_house_id).slot)

            for check in game_info.don_checks:
                print('\tDon check | day:', check.circle_number,
                      'Slot:', get_house_from_list_by_house_id(game_info.houses, check.checked_house_id).slot)

            for b in game_info.breaks:
                breaked_house = get_house_from_list_by_house_id(game_info.houses, b.house_to)
                who_break_house = get_house_from_list_by_house_id(game_info.houses, b.house_from)
                print('\tBreak:\t\tCount:', b.count, 'Breaked house:',
                      breaked_house.slot, 'Who break:', who_break_house.slot)

            print('\tSheriff versions:', list(map(lambda h: h.slot, get_houses_from_list_of_house_ids(
                game_info.houses, list(map(lambda d: d.house, game_info.sheriff_versions))))))

            for miss in game_info.misses:
                house = get_house_from_list_by_house_id(game_info.houses, miss.house_id)
                print('\tMiss:', house.slot, 'Miss day:', miss.circle_number)

            for devise in game_info.devises:
                house = get_house_from_list_by_house_id(game_info.houses, devise.killed_house)
                houses = get_houses_from_list_of_house_ids(game_info.houses, [
                    devise.house_1,
                    devise.house_2,
                    devise.house_3,
                ])
                print('\tDevise from house:', house.slot,
                      '\t\tChoosen slots:', list(map(lambda h: h.slot, houses)))

            print('\tDisq:', list(map(lambda h: h.slot, get_houses_from_list_of_house_ids(
                game_info.houses, list(map(lambda d: d.house, game_info.disqualifieds))))))

            if game_info.hand_of_mafia:
                hand_of_mafia_house = get_house_from_list_by_house_id(
                    game_info.houses, game_info.hand_of_mafia.house_hand_id)

                victim_house = get_house_from_list_by_house_id(
                    game_info.houses, game_info.hand_of_mafia.victim_id)

                print('\tHand of mafia:', hand_of_mafia_house.slot, 'Victim house:', victim_house.slot)

            if game_info.best_move:
                house = get_house_from_list_by_house_id(game_info.houses, game_info.best_move.killed_house)
                houses = get_houses_from_list_of_house_ids(game_info.houses, [
                    game_info.best_move.best_1,
                    game_info.best_move.best_2,
                    game_info.best_move.best_3,
                ])
                print('\tBest move from:', house.slot, '\t\tChoosen slots:', list(map(lambda h: h.slot, houses)))

            print('\n\n\n')
