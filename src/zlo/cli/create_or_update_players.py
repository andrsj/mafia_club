import os
import uuid
import argparse


import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.cli.setup_env_for_test import setup_env_with_test_database
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Player


KEY_DUBLICAT_WORD = '--dublicat--'


@inject.params(
    uowm=UnitOfWorkManager
)
def create_or_update_player(uowm: UnitOfWorkManager, player_data: dict):
    with uowm.start() as tx:
        player = tx.players.get_by_id(player_id=player_data["player_id"])
        if player is None:
            print(f"Create new player {player_data['nickname']}")
            player = Player(
                player_id=player_data["player_id"],
                nickname=player_data["nickname"],
                displayname=player_data["Nickname for official stats"],
                name=player_data.get("name"),
                club=player_data.get("club")
            )
        else:
            # NICKNAME
            if player.nickname != player_data["nickname"]:
                print(f"Update player nickname old nickname '{player.nickname}'; New one {player_data['nickname']}")
            player.nickname = player_data["nickname"]

            # DISPLAYNAME
            if player.displayname and player.displayname != player_data["Nickname for official stats"]:
                print(f'Update player displayname \'{player.displayname}\' ; '
                      f'New one: \'{player_data["Nickname for official stats"]}\'')

            player.displayname = player_data["Nickname for official stats"]

            player.name = player_data.get("name")
            player.club = player_data.get("club")

        tx.players.add(player)
        tx.commit()

def save_or_update_players_in_sheet(sheet):
    players = sheet.get_all_records()

    """[
        {
            "UUID": ...,
            "Nickname": ...,
            "Nickname for official stats": ...,
            "Name": ...,
            "Club": ...
        }
    ]
    """

    for player in players:
        player['Nickname'] = str(player['Nickname']).strip().lower()
        player["Nickname for official stats"] = str(player["Nickname for official stats"]).strip()

    list_nicknames = list()
    uuid_players_list = list()

    for index, player in enumerate(players, start=2):

        # Marking repeateble nicknames
        if player['Nickname'] in list_nicknames:
            sheet.update(f'B{index}', KEY_DUBLICAT_WORD + player['Nickname'])
            print(f"Oppa, dublicat: {player['Nickname']} : {index}")
            uuid_players_list.append(KEY_DUBLICAT_WORD)
            continue

        # Skipping dublicats
        if player['Nickname'].startswith(KEY_DUBLICAT_WORD):
            print(f"Oppa, dublicat: {player['Nickname']} : {index}")
            uuid_players_list.append(KEY_DUBLICAT_WORD)
            continue

        player["Nickname for official stats"] = player.get("Nickname for official stats") or player["Nickname"]

        list_nicknames.append(player['Nickname'])

        player_uuid = player['UUID']

        # If isn't any UUID in sheet
        if not player_uuid:
            print(f"New player nickname {player['Nickname']}, index: {index}")
            player_uuid = str(uuid.uuid4())

        # Add al UUID into list for update
        uuid_players_list.append(player_uuid)

        # Create player into DB
        create_or_update_player(player_data={
            "player_id": player_uuid,
            "name": None,
            "club": None,
            "nickname": player['Nickname'],
            "Nickname for official stats": player["Nickname for official stats"]
        })

    # Massive push UUID for players sheet
    sheet.update(f"A2:A{index}", [[i] for i in uuid_players_list])


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     '--name',
    #     dest='name',
    #     help='Name of spreadsheet of players',
    #     default='СписокГравців'
    # )
    # args = parser.parse_args()

    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    client = inject.instance(SpreadSheetClient)
    # sheet_players = client.client.open(args.name).sheet1
    sheet_players = client.client.open_by_key('1ZYS2QWlzwobBhpKpIIfwARRTVYPy26HT92t-0l1bRJ0').sheet1
    save_or_update_players_in_sheet(sheet_players)
