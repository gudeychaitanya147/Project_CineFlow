import os
import json
from Utilities.Youtube import get_authenticated_service, upload_video
from Utilities.Drive import get_authenticated_drive_service

def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def script():
    # Load configuration
    config_path = os.path.join("Keys", "basic_data.json")
    print(f"Loading config from: {config_path}")
    config = load_config(config_path)
    
    # Set up authentication files
    client_secret = os.path.join("Keys", "client_secret.json")
    youtube_token = os.path.join("Keys", "token_youtube.pickle")
    drive_token = os.path.join("Keys", "token_drive.pickle")
    
    print("Authenticating with YouTube...")
    youtube = get_authenticated_service(
        client_secret_file=client_secret,
        token_file=youtube_token
    )
    
    print("Authenticating with Drive...")
    drive = get_authenticated_drive_service(
        client_secret_file=client_secret,
        token_file=drive_token
    )
    
    print("Starting video upload...")
    try:
        response = upload_video(
            youtube=youtube,
            drive=drive,
            title="My Upload Test",
            description="This is a test video uploaded via Python package.",
        )
        print("Video uploaded successfully!")
        print("Video ID:", response.get('id'))
        print("Title:", response.get('snippet', {}).get('title'))
        print("Privacy Status:", response.get('status', {}).get('privacyStatus'))
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        raise

if __name__ == "__main__":
    script()