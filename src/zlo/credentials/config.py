from os.path import dirname


from oauth2client.service_account import ServiceAccountCredentials


from zlo import credentials


CLIENT_SECRET_FILE = dirname(credentials.__file__) + "/zlomafiaclub-bf747a844d45.json"
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1Q7lFrQISWZ6mvJBiPsJvLBSk4kGmcou4'  # Рейтинг/Бланки
SOURCE_FILE_ID = '1aaRjI_imeO5VGjDeygHQBXk-YzeKPgjaYu66R7zMqgo'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, SCOPES)
