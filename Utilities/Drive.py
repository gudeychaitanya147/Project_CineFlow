import os
from googleapiclient.http import MediaFileUpload
import googleapiclient.http
googleapiclient.http.DEFAULT_HTTP_TIMEOUT = 200

def upload_to_drive(service, file_path, folder_id=None):

    metadata = {"name": os.path.basename(file_path)}
    if folder_id: metadata["parents"] = [folder_id]

    upload = service.files().create(
        body=metadata,
        media_body=MediaFileUpload(file_path, resumable=True),
        fields="id, name, webViewLink"
    ).execute()

    print(f"Uploaded: {upload['name']} -> Link: {upload['webViewLink']}")
    return upload


def list_drive_files(service, folder_id=None, mime_type="video/mp4"):

    query = " and ".join(filter(None, [
        f"'{folder_id}' in parents" if folder_id else None,
        f"mimeType='{mime_type}'" if mime_type else None
    ])) or None

    files, page_token = [], None
    
    while True:
        res = service.files().list(
            q = query,
            orderBy = "modifiedTime desc",
            pageSize = 1000,
            fields = "nextPageToken, files(id, name, mimeType, webViewLink, modifiedTime, size)",
            pageToken = page_token
        ).execute()

        files.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break

    for f in files:
        print(f"{f['name']} ({float(f.get('size', 0)) / (1024):.1f} KB) -> {f['webViewLink']}")
    return files
