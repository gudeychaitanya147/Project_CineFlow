import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service(
    client_secret_file="client_secret.json",
    token_file="token.pickle",
    scopes=SCOPES
):
    """
    Authenticate once as a Gmail user and reuse stored credentials.
    If token exists, auto-login without prompt.
    """
    creds = None

    # Load existing token if it exists
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, login manually once
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # First-time login: opens a browser only once
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)

        # Save credentials for future automatic use
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    # Build YouTube API client
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def get_public_service(api_key):
    """Create a YouTube Data API client using an API key (read-only)."""
    return build("youtube", "v3", developerKey=api_key)

def search_videos(youtube, query, max_results=5):
    """
    Search for YouTube videos by keyword.
    """
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    return response["items"]

def get_channel_stats(youtube, for_username=None, channel_id=None):
    """
    Fetch channel statistics using username or channel ID.
    """
    if not (for_username or channel_id):
        raise ValueError("Provide either for_username or channel_id")

    request = youtube.channels().list(
        part="snippet,statistics",
        forUsername=for_username,
        id=channel_id
    )
    response = request.execute()
    return response["items"]


def upload_video(youtube, file_path, title, description, tags=None, category_id="22", privacy_status="private"):
    """
    Upload a video to YouTube.
    """
    request_body = {
        "snippet": {
            "categoryId": category_id,
            "title": title,
            "description": description,
            "tags": tags or []
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media_file = MediaFileUpload(file_path)
    upload = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )
    response = upload.execute()
    return response

def print_video_list(videos):
    """
    Print basic info of video search results.
    """
    for video in videos:
        snippet = video["snippet"]
        print(f"Title: {snippet['title']}")
        print(f"Channel: {snippet['channelTitle']}")
        print(f"Published at: {snippet['publishedAt']}")
        print(f"Video ID: {video['id']['videoId']}")
        print("-" * 50)
