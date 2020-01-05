import gspread
from oauth2client.service_account import ServiceAccountCredentials


def auth():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        '/home/dvasilov/Projects/zlo/guiding/credentials/ZloMafiaClub-655c0c73f071.json', scope)
    client = gspread.authorize(creds)
    return client
