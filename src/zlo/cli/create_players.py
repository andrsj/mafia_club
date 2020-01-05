import os
import time
import uuid

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.cli.auth import auth
from zlo.domain.infrastructure import UnitOfWorkManager
from zlo.domain.model import Player


@inject.params(
    uowm=UnitOfWorkManager
)
def create_player(uowm, player_data: dict):
    print(f"Creating player {player_data}")
    with uowm.start() as tx:
        player = Player(
            player_id=player_data["player_id"],
            nickname=player_data["nickname"],
            name=player_data.get("name"),
            club=player_data.get("club")
        )
        tx.players.add(player)
        tx.commit()


if __name__ == "__main__":

    cfg = os.environ.copy()
    bootstrap(cfg)

    client = auth()
    sheet = client.open('СписокГравців').sheet1

    start_index = 3
    step = 0
    while step <= 200:
        player_row = sheet.row_values(start_index + step)
        player_nickname = player_row[1]
        player_uuid = player_row[0]
        # player_nickname = sheet.cell(start_index + step, 2).value
        # player_uuid = sheet.cell(start_index + step, 1).value
        if not player_nickname:
            break
        if not player_uuid:
            player_uuid = str(uuid.uuid4())
            sheet.update_cell(start_index + step, 1, player_uuid)
        time.sleep(1)
        create_player(player_data={
            "player_id": player_uuid,
            "name": None,
            "club": None,
            "nickname": player_nickname
        })
        step += 1
        time.sleep(2)
