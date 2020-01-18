import os
import time
import uuid

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.cli.auth import auth
from zlo.cli.zlo_logger import get_logger
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Player


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


if __name__ == "__main__":

    cfg = os.environ.copy()
    bootstrap(cfg)

    client = auth()
    sheet = client.open('СписокГравців').sheet1

    start_index = 220
    step = 0
    while step <= 205:
        player_row = sheet.row_values(start_index + step)
        player_nickname = player_row[1]
        player_uuid = player_row[0]
        if not player_nickname:
            break
        if not player_uuid:
            print(f"New player nickname {player_nickname}")
            player_uuid = str(uuid.uuid4())
            sheet.update_cell(start_index + step, 1, player_uuid)
        time.sleep(1)
        create_or_update_player(player_data={
            "player_id": player_uuid,
            "name": None,
            "club": None,
            "nickname": player_nickname
        })
        step += 1
        time.sleep(2)

