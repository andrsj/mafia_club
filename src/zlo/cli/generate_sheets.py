from os.path import dirname
from typing import Dict, List, Optional
from datetime import datetime


import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from zlo.domain.utils import get_month, get_the_specified_days_by_dates, create_parser_for_blank_generation
from zlo import credentials


CLIENT_SECRET_FILE = dirname(credentials.__file__) + "/zlomafiaclub-bf747a844d45.json"
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1Q7lFrQISWZ6mvJBiPsJvLBSk4kGmcou4'  # Рейтинг/Бланки
SOURCE_FILE_ID = '1aaRjI_imeO5VGjDeygHQBXk-YzeKPgjaYu66R7zMqgo'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, SCOPES)
drive = build(API_NAME, API_VERSION, credentials=credentials)

# create new client for this script (not our Spreadsheet class)
client = gspread.authorize(credentials)


def get_all_files_in_folder(folder_id) -> List[Dict]:
    response = drive.files().list(q=f"parents = '{folder_id}'").execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = drive.files().list(q=f'parents = {folder_id}').execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')

    return files

def filter_folders(files: List[Dict]) -> filter:
    return filter(lambda f: f['mimeType'] == 'application/vnd.google-apps.folder', files)

def get_file_by_name(files, filename: str) -> Optional[Dict]:
    for file_info in files:
        if file_info['name'].lower() == filename.lower():
            return file_info
    return None

def copy_file(source_file_id, folder_id, new_name):
    file_metadata = {
        'name': new_name,
        'parents': [folder_id],
        'description': 'Test file'
    }

    file_resource = drive.files().copy(fileId=source_file_id, body=file_metadata).execute()
    return file_resource

def create_folder_on_drive(parent_folder_id, folder_name):
    body = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder_info = drive.files().create(body=body).execute()
    return folder_info

def generate_blanks_for_spreadsheet(spreadsheet, datetime_of_day: datetime):
    # Format all requests for one batch update:
    list_requests = [{
        # Change title for first sheet
        'updateSheetProperties': {
            'properties': {
                'sheetId': 0,
                'title': 'Стіл1Гра1'
            },
            'fields': 'title'
        }
    }, {
        # Automatically write the date in the appropriate field
        'updateCells': {
            'fields': 'userEnteredValue',
            # Cell D2:
            'range': {
                # Column D:
                "startColumnIndex": 3,
                "endColumnIndex": 4,
                # Row 2:
                "startRowIndex": 1,
                "endRowIndex": 2,
                "sheetId": 0
            },
            'rows': [{
                'values': {
                    # Finally we enter this date
                    'userEnteredValue': {
                        'stringValue': datetime_of_day.strftime('%Y-%m-%d')
                    }
                }
            }],
        }
    }]

    # Append requests for duplicate sheets for other games
    for sheet_index, name in enumerate(['Стіл1Гра2', 'Стіл1Гра3', 'Стіл2Гра1', 'Стіл2Гра2', 'Стіл2Гра3'], start=1):
        list_requests.append(
            {
                'duplicateSheet': {
                    'sourceSheetId': 0,
                    'insertSheetIndex': sheet_index,
                    'newSheetName': name
                }
            }
        )

    spreadsheet.batch_update(body={
        'requests': list_requests
    })

def create_copy_spreadsheet(datetime_of_day: datetime):
    date_string = datetime_of_day.strftime('%d/%m/%Y')
    files_in_parent_folder = get_all_files_in_folder(folder_id=FOLDER_ID)

    # We get files from root folder 'Рейтинг/Бланки'

    folder_by_year = get_file_by_name(filter_folders(files_in_parent_folder), filename=str(datetime_of_day.year))

    if folder_by_year is None:
        folder_by_year = create_folder_on_drive(parent_folder_id=FOLDER_ID, folder_name=str(datetime_of_day.year))
        print(f"Create new folder for '{datetime_of_day.year}': "
              f"https://drive.google.com/drive/folders/{folder_by_year['id']}")
    else:
        print(f"Folder '{folder_by_year['name']}'")

    files_in_year_folder = get_all_files_in_folder(folder_id=folder_by_year['id'])
    # We get files from year folder
    month = get_month(datetime_of_day)

    folder_by_month = get_file_by_name(filter_folders(files_in_year_folder), month)

    if folder_by_month is None:
        folder_by_month = create_folder_on_drive(parent_folder_id=folder_by_year['id'], folder_name=month)
        print(f"Create new folder for '{month}': https://drive.google.com/drive/folders/{folder_by_month['id']}")
    else:
        print(f"Folder '{folder_by_month['name']}'")

    files_in_month_folder = get_all_files_in_folder(folder_id=folder_by_month['id'])

    # We get files from month folder

    # Try to find needed file:
    file_in_month_folder = get_file_by_name(files_in_month_folder, date_string)

    if file_in_month_folder is None:
        new_file = copy_file(
            folder_id=folder_by_month['id'],
            # The clean file to be copied, which is an example
            # https://docs.google.com/spreadsheets/d/1aaRjI_imeO5VGjDeygHQBXk-YzeKPgjaYu66R7zMqgo
            source_file_id=SOURCE_FILE_ID,
            new_name=date_string
        )

        spreadsheet = client.open_by_key(new_file['id'])
        generate_blanks_for_spreadsheet(spreadsheet, datetime_of_day)
        print(f"File '{date_string}' ready to use: "
              f"https://docs.google.com/spreadsheets/d/{new_file['id']}")
    else:
        print(f"File '{date_string}' already exist by this url: "
              f"https://docs.google.com/spreadsheets/d/{file_in_month_folder['id']}")


if __name__ == '__main__':
    parser = create_parser_for_blank_generation()
    arguments = parser.parse_args()

    dates = get_the_specified_days_by_dates(
        start_date=datetime.strptime(arguments.start_date_of_day, '%d/%m/%Y'),
        end_date=datetime.strptime(arguments.end_date_of_day, '%d/%m/%Y')
    )
    for date in dates:
        create_copy_spreadsheet(datetime_of_day=date)
