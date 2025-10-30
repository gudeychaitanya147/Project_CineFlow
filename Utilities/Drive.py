import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_authenticated_drive_service(client_secret_file="client_secret.json", token_file="token_drive.pickle"):
    """
    Authenticate Google Drive API once (user-level OAuth, not service account).
    Automatically reuses stored credentials from token_drive.pickle.
    """
    scopes = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    # Load token if exists
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    # Refresh or prompt login if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    # Build Drive API client
    drive = build("drive", "v3", credentials=creds)
    return drive


def upload_to_drive(drive, file_path, folder_id=None):
    """
    Uploads a file to Google Drive (to My Drive or a specific folder).
    """
    file_name = os.path.basename(file_path)

    metadata = {"name": file_name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)

    upload = drive.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, webViewLink"
    ).execute()

    print(f"Uploaded: {upload['name']}")
    print(f"Link: {upload['webViewLink']}")
    return upload


def list_drive_files(drive, max_results=10):
    """
    Lists recent files in your Google Drive.
    """
    results = (
        drive.files()
        .list(pageSize=max_results, fields="files(id, name, mimeType, webViewLink)")
        .execute()
    )
    files = results.get("files", [])
    if not files:
        print("No files found.")
        return []
    for f in files:
        print(f"{f['name']} ({f['mimeType']}) -> {f['webViewLink']}")
    return files


# Example usage
if __name__ == "__main__":
    drive = get_authenticated_drive_service('C:/Users/gudey/Documents/Github/Project_CineFlow/Keys/client_secret.json', 'C:/Users/gudey/Documents/Github/Project_CineFlow/Keys/token_drive.pickle')
    # Upload example file
    upload_to_drive(drive, "C:/Users/gudey/Downloads/video.mp4")
    # List recent files
    list_drive_files(drive)
