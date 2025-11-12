from googleapiclient.discovery import build
from Utilities import *

def script():
    CRED = get_authenticated_cred()
    youtube = get_authenticated_apps("youtube", CRED)
    drive = get_authenticated_apps("drive", CRED)
    sheets = get_authenticated_apps("sheets", CRED)
    
    #clear_sheet_data(sheets, 'Output!2:1000000"')
    #files = list_drive_files(drive, '1eVcjBGKCsr33p7TeWMWHH_mh-u5hSelO')
    #write_drive_files_to_sheet(sheets, 'Output!A2', files)

if __name__ == "__main__":
    script()
