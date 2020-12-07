import os
import uuid


import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.cli.setup_env_for_test import setup_env_with_test_database
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Player


KEY_DUBLICAT_WORD = '--Dublicat--'


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
                name=player_data.get("name"),
                club=player_data.get("club")
            )
        else:
            if player.nickname != player_data["nickname"]:
                print(f"Update player nickname old nickname {player.nickname}; New one {player_data['nickname']}")
            else:
                print(f"Keep old nickname {player.nickname}")
            player.nickname = player_data["nickname"]
            player.name = player_data.get("name")
            player.club = player_data.get("club")
        tx.players.add(player)
        tx.commit()

def save_or_update_players_in_sheet(sheet):
    players = sheet.get_all_records()

    list_nicknames = []
    uuid_players_list = []

    for index, player_ in enumerate(players, start=2):

        if player_['Nickname'] in list_nicknames:
            sheet.update(f'B{index}', KEY_DUBLICAT_WORD + player_['Nickname'])
            print(f"Oppa, dublicat: {player_['Nickname']} : {index}")
            uuid_players_list.append(KEY_DUBLICAT_WORD)
            continue

        if str(player_['Nickname']).startswith(KEY_DUBLICAT_WORD):
            print(f"Oppa, dublicat: {player_['Nickname']} : {index}")
            uuid_players_list.append(KEY_DUBLICAT_WORD)
            continue

        player_uuid = player_['UUID']
        list_nicknames.append(player_['Nickname'])

        if not player_uuid:
            print(f"New player nickname {player_['Nickname']}, index: {index}")
            player_uuid = str(uuid.uuid4())

        uuid_players_list.append(player_uuid)

        create_or_update_player(player_data={
            "player_id": player_uuid,
            "name": None,
            "club": None,
            "nickname": player_['Nickname']
        })

    sheet.update(f"A2:A{index}", [[i] for i in uuid_players_list])

if __name__ == "__main__":

    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    client = inject.instance(SpreadSheetClient)
    sheet_players = client.client.open('СписокГравців1').sheet1

    save_or_update_players_in_sheet(sheet_players)
