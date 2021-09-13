import os
import csv
from datetime import datetime

import inject

from dim_mafii.domain.utils import create_parser_for_rating
from dim_mafii.domain.infrastructure import UnitOfWorkManager
from dim_mafii.adapters.bootstrap import bootstrap
from dim_mafii.domain.config import DATE_FORMAT
from dim_mafii.domain.mmr_calculators.general_calculator import get_mmr

from dim_mafii.cli.setup_env_for_test import setup_env_with_test_database


if __name__ == '__main__':
    cfg = os.environ.copy()
    setup_env_with_test_database(cfg)
    bootstrap(cfg)

    parser = create_parser_for_rating()
    args = parser.parse_args()

    start = datetime.strptime(args.start_date_of_day, DATE_FORMAT)

    end = datetime.strptime(args.end_date_of_day, DATE_FORMAT)
    # 01.01.2021 - 04.04.2021 - First MMR
    # 01.01.2021 - 08.05.2021 - Second MMR
    # 01.01.2021 - 31.08.2021 - Third MMR

    uowm = inject.instance(UnitOfWorkManager)
    with uowm.start() as tx:
        players = tx.players.all()

    rating, detail_rating = get_mmr(
        uowm,
        start_date=start,
        end_date=end,
        club_name=args.club
    )

    rating = {next(filter(lambda p: p.player_id == i, players)).displayname: j
              for i, j in sorted(rating.items(), key=lambda x: x[1])}

    detail_rating = {next(filter(lambda p: p.player_id == i, players)).displayname: j
                     for i, j in detail_rating.items()}

    rating = {i: j for i, j in rating.items() if detail_rating.get(i)}

    for i, j in sorted(rating.items(), key=lambda x: x[1], reverse=True):
        print(i, j, len(detail_rating.get(i)))

    with open('rating_{}.csv'.format(args.club), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Nickname', 'MMR', 'Games'])
        writer.writeheader()
        for i, j in sorted(rating.items(), key=lambda x: x[1], reverse=True):
            writer.writerow({
                'Nickname': i.capitalize(),
                'MMR': j,
                'Games': len(detail_rating.get(i, []))
            })

    with open('rating_{}-15.csv'.format(args.club), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Nickname', 'MMR', 'Games'])
        writer.writeheader()
        for i, j in sorted(rating.items(), key=lambda x: x[1], reverse=True):
            if len(detail_rating.get(i, [])) >= 15:
                writer.writerow({
                    'Nickname': i.capitalize(),
                    'MMR': j,
                    'Games': len(detail_rating.get(i, []))
                })
