import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import googleapiclient.http

googleapiclient.http.DEFAULT_HTTP_TIMEOUT = 120

def get_authenticated_drive_service(client_secret_file="client_secret.json", token_file="token_drive.pickle"):
    """
    Authenticate Google Drive API once (user-level OAuth, not service account).
    Automatically reuses stored credentials from token_drive.pickle.
    """
    scopes = [
        "https://www.googleapis.com/auth/drive.readonly",  # For listing all files
        "https://www.googleapis.com/auth/drive.file"      # For creating/uploading files
    ]
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


def list_drive_files(drive, folder_id=None, mime_type=None, order_by="name"):
    query_parts = []
    
    # Build query
    if folder_id:
        query_parts.append(f"'{folder_id}' in parents")
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    
    query = " and ".join(query_parts) if query_parts else None
    
    files = []
    page_token = None
    
    while True:
        # Get files page by page
        results = drive.files().list(
            q=query,
            orderBy=order_by,
            pageSize=1000,  # Maximum allowed page size
            fields="nextPageToken, files(id, name, mimeType, webViewLink, modifiedTime, size)",
            pageToken=page_token
        ).execute()
        
        batch = results.get("files", [])
        files.extend(batch)
        
        # Get next page token
        page_token = results.get("nextPageToken")
        if not page_token:
            break
            
    if not files:
        print("No files found.")
        return []
        
    for f in files:
        size_mb = float(f.get('size', 0)) / (1024 * 1024)
        print(f"{f['name']} ({size_mb:.1f}MB) -> {f['webViewLink']}")
        
    return files
