from os.path import dirname
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from zlo import credentials
import gspread
from pprint import pp

CLIENT_SECRET_FILE = dirname(credentials.__file__) + "/zlomafiaclub-bf747a844d45.json"
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1Q7lFrQISWZ6mvJBiPsJvLBSk4kGmcou4'  # Рейтинг/Бланки

credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, SCOPES)
drive = build(API_NAME, API_VERSION, credentials=credentials)

files = drive.files()

def get_spreadsheet_url(id: str):
	return f'https://docs.google.com/spreadsheets/d/{id}'

def get_folder_url(id: str):
	return f'https://drive.google.com/drive/folders/{id}'

def file_list():
	response = files.list( 
		orderBy='name, folder', 
		fields='files(id, mimeType, name, permissions), nextPageToken'
	).execute()

	files_list = response.get('files')
	print(len(files_list))
	nextPageToken = response.get('nextPageToken')

	while nextPageToken:
		response = drive.files().list( 
			orderBy='name, folder', 
			fields='files(id, mimeType, name, permissions), nextPageToken',
			pageToken=nextPageToken
		).execute()
		files_list.extend(response.get('files'))
		print(len(files_list))
		nextPageToken = response.get('nextPageToken')

	for file in files_list:
		url = ""
		if file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
			url = get_spreadsheet_url(file['id'])
		elif file['mimeType'] == 'application/vnd.google-apps.folder':
			url = get_folder_url(file['id'])

		name = file['name'] if len(file['name']) < 15 else file['name'][:15] + '...'
		format_string = '\t{:<20} {:<90} {:<10} {}'.format(
			name, 
			url, 
			file['mimeType'].split('.')[-1],
			len(file['permissions'])
		)
		print(format_string)

	print('\t', f"We have {len(files_list)} count of files")

file_list()
