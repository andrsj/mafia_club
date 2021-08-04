from os.path import dirname


from oauth2client.service_account import ServiceAccountCredentials


from dim_mafii import credentials


CLIENT_SECRET_FILE = dirname(credentials.__file__) + "/zlomafiaclub-bf747a844d45.json"
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
# FOLDER_ID = '1Q7lFrQISWZ6mvJBiPsJvLBSk4kGmcou4'  # Рейтинг/Бланки
FOLDER_ID = '19UAtKHmQCr1YGkgD_b72mJuyDYftMIaZ'  # Рейтинг-Бланки
# SOURCE_FILE_ID = '1aaRjI_imeO5VGjDeygHQBXk-YzeKPgjaYu66R7zMqgo'  # Old
SOURCE_FILE_ID = '1TSmU7pTWiW-TxgCs0RWqbOdI5VhRVC5Wtde2KQ79-xU'  # New

LIST_OF_PLAYERS_SPREADSHEET = '1ZYS2QWlzwobBhpKpIIfwARRTVYPy26HT92t-0l1bRJ0'  # СписокГравців
LIST_OF_ERRORS_SPREADSHEET = '1rNX_PVdrTVr2z9N5jCcxoVWLGamByzz18lO6yyg33jQ'  # Errors

credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, SCOPES)
