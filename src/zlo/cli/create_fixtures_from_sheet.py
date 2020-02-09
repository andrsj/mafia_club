import argparse
import os

import inject
from zlo.adapters.bootstrap import bootstrap
from zlo.sheet_parser.client import SpreadSheetClient
from zlo.tests import fixtures

if __name__ == "__main__":
    cfg = os.environ.copy()
    bootstrap(cfg)

    my_parser = argparse.ArgumentParser(description='Parse data from spreadsheet and fill tables')
    my_parser.add_argument(
        "--sheet",
        dest='sheet_title',
        type=str,
        required=True
    )
    args = my_parser.parse_args()
    client = inject.instance(SpreadSheetClient)
    sheet = client.client.open(args.sheet_title)
    fixtures_path = os.path.dirname(fixtures.__file__)
    for worksheet in sheet.worksheets():
        data = client.parse_worksheet(worksheet)
        path = os.path.join(fixtures_path, f"{worksheet.title}.json")
        client.store_data_in_json_file(data, path)
