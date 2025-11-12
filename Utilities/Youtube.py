import io
from googleapiclient.http import MediaIoBaseUpload

def upload_video(youtube, drive, title, description, tags=None, processing_details=True, file_id=None):

    file_stream = io.BytesIO(drive.files().get_media(fileId=file_id).execute())
    
    media = MediaIoBaseUpload(
        file_stream, 
        mimetype='video/mp4',
        chunksize=256*1024*1024,
        resumable=True
    )

    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": title,
            "description": description,
            "tags": tags or []
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
            "license": "youtube",
            "embeddable": True,
            "publicStatsViewable": True
        }
    }

    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media,
        notifySubscribers=False
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
        if response:
            print(f"Upload Complete! Video ID: {response['id']}")

    return response
