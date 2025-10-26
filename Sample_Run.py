from Utilities import *
import json

def script(data):
    # Authenticate (for upload)
    youtube = get_authenticated_service(client_secret_file="Keys/client_secret.json", token_file="Keys/token_account.pickle")

    # Upload a video
    response = upload_video(
        youtube,
        file_path=data["download_dir"] + "Video.mp4",
        title="My Upload Test",
        description="This is a test video uploaded via Python package."
    )
    print("Video uploaded:", response)

    # Public service (API key)
    youtube_public = get_public_service(data["API_key"])

    # Get channel stats
    stats = get_channel_stats(youtube_public, channel_id=data["channel_id"])
    print(stats)

    # Search for videos
    results = search_videos(youtube_public, "Python tutorial", max_results=3)
    print_video_list(results)


# Open and load JSON file
with open("Keys/basic_data.json", "r") as file:
    data = json.load(file)

# ===========================
# Example Usage
# ===========================
if __name__ == "__main__":
    input_file = data["download_dir"] + "Video.mp4"
    user_prompt = "Give me 4 sets of { Title, Description, Hashtags, Thumbnails } for the attached video"

    files, summary = process_file_with_perplexity(input_file, user_prompt)

    print("✅ Response Summary:", summary)
    print("✅ Files generated:")
    for f in files:
        print(" -", f)
