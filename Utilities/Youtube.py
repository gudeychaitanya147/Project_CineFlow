import io
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from Utilities.Drive import list_drive_files

def get_authenticated_service(client_secret_file="client_secret.json", token_file="token.pickle"):
    """Get authenticated YouTube service with upload capabilities.
    
    Args:
        client_secret_file: Path to OAuth client secrets file
        token_file: Path to save/load credentials
        
    Returns:
        Authenticated YouTube API service object
    """
    print(f"\nAuthenticating YouTube service...")
    print(f"Using client secrets: {client_secret_file}")
    print(f"Using token file: {token_file}")
    
    if not os.path.exists(client_secret_file):
        raise FileNotFoundError(f"Client secrets file not found: {client_secret_file}")
    
    # Required scopes for video upload
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtube"
    ]
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

    try:
        # Build YouTube API client
        print("Building YouTube service with credentials...")
        youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
        
        # Verify service by getting channel info
        print("Verifying YouTube service access...")
        try:
            channels = youtube.channels().list(
                part="snippet",
                mine=True
            ).execute()
            
            if not channels.get('items'):
                raise Exception("No channel found - please ensure you're logged into the correct account")
                
            channel = channels['items'][0]['snippet']
            print(f"Successfully authenticated as channel: {channel['title']}")
            print(f"Channel ID: {channels['items'][0]['id']}")
            
        except Exception as e:
            print(f"Error verifying YouTube access: {str(e)}")
            print("Please ensure you have a YouTube channel and proper permissions")
            raise
            
        return youtube
        
    except Exception as e:
        print(f"\nError building YouTube service: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Delete token file and try again")
        print("2. Ensure client_secret.json is correct")
        print("3. Check you're signing in with a Google account that has a YouTube channel")
        raise

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


def upload_video(youtube, drive, title, description, tags=None, category_id="22", processing_details=True):
    """
    Upload a video to YouTube from Google Drive with high quality settings.
    
    Args:
        youtube: Authenticated YouTube service object
        drive: Authenticated Drive service object
        title: Video title
        description: Video description
        tags: Optional list of tags
        category_id: YouTube category ID (default: 22 = People & Blogs)
        privacy_status: 'private', 'unlisted', or 'public' (default: private)
        processing_details: Whether to wait and check processing details (default: True)
    """
    print(f"Preparing to upload video: {title}")
    
    # Enhanced upload metadata with high quality settings
    request_body = {
        "snippet": {
            "categoryId": category_id,
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
    try:
        # Get first video from Drive folder
        print("Searching for video in Drive...")
        videos = list_drive_files(drive, '1Nlud2lgR-4E-Q1W25rqopEz4paW1X76q', 'video/mp4')
        if not videos:
            raise ValueError("No video files found in the specified Drive folder")
            
        drive_file_id = videos[0]['id']
        file_metadata = drive.files().get(fileId=drive_file_id).execute()
        print(f"Found video in Drive: {file_metadata['name']}")

        # Stream file from Drive
        print("Streaming video from Drive...")
        file_request = drive.files().get_media(fileId=drive_file_id)
        file_stream = io.BytesIO(file_request.execute())
        
        # Prepare upload with optimized chunk size for better performance
        print("Preparing YouTube upload with optimized settings...")
        media = MediaIoBaseUpload(
            file_stream, 
            mimetype='video/mp4',
            chunksize=256*1024*1024,  # 256MB chunks for faster upload
            resumable=True
        )

        # Enhanced upload request
        print("Creating upload request with high quality settings...")
        request = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media,
            notifySubscribers=False
        )

        print("Starting upload to YouTube...")
        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")
                if response:
                    print(f"Upload Complete! Video ID: {response['id']}")
            except Exception as e:
                print(f"Upload chunk failed: {str(e)}")
                raise

        # Wait for processing and verify high quality settings
        if processing_details and response:
            video_id = response['id']
            while True:
                # Check processing status
                processing_status = youtube.videos().list(
                    part='status',
                    id=video_id
                ).execute()

                if not processing_status['items']:
                    break

                status = processing_status['items'][0]
                
                if 'processingDetails' in status:
                    details = status['processingDetails']
                    
                    if details.get('processingStatus') == 'failed':
                        print(f"Processing failed: {details.get('processingFailureReason')}")
                        break
                    
                    if details.get('processingStatus') == 'terminated':
                        print("\nProcessing complete!")
                        # Check available quality levels
                        print("Available quality levels:", details.get('availableProcessingLevels', []))
                        print("Processing level:", details.get('processingLevel'))
                        break
                        
                    print(f"Processing status: {details.get('processingStatus')}")
                    print(f"Progress: {details.get('processingProgress', {}).get('partsTotal', 0)}%")
                    
                import time
                time.sleep(10)  # Wait 10 seconds before checking again
                
        return response
        
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        raise

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
