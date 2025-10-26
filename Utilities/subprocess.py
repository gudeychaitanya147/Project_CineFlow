import subprocess

def function_to_merge_videos(videos, output):
        
    # Write file list to a temporary text file
    with open("videos.txt", "w") as f:
        for v in videos:
            f.write(f"file '{v}'\n")

    # Merge using ffmpeg (no re-encoding)
    subprocess.run([
        "./ffmpeg/bin/ffmpeg.exe", "-f", "concat", "-safe", "0",
        "-i", "videos.txt", "-c", "copy", output
    ])

if __name__ == "__main__":
    video_list = [
        "C:/Users/gudey/Downloads/abc.mp4",
        "C:/Users/gudey/Downloads/xyz.mp4",
        "C:/Users/gudey/Downloads/video.mp4",
    ]
    function_to_merge_videos(video_list, "C:/Users/gudey/Downloads/merged_output.mp4")
