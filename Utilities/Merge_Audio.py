import subprocess
import random
import os

def merge_random_audio(video_path, audio_folder, output_path, volume=0.2):

    random_audio = os.path.join(audio_folder, random.choice([f for f in os.listdir(audio_folder) if f.lower().endswith(('.mp3'))]))
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")

    # FFmpeg command: Mix video and adjusted-volume audio
    cmd = [
        ffmpeg_path, "-y",
        "-i", video_path,
        "-i", random_audio,
        "-stream_loop", "-1",
        "-filter_complex", f"[1:a]volume={volume}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    subprocess.run(cmd, check=True)

# Example usage
merge_random_audio(
    video_path="C:/Users/gudey/Downloads/val.mp4",
    audio_folder="C:/Users/gudey/Downloads/audio",
    output_path="C:/Users/gudey/Downloads/video_with_bg.mp4",
)
