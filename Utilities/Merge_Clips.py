import subprocess
import os
import shutil
import tempfile

# Helper: normalize audio of inputs to avoid decoder errors seen with some AAC variants
def _normalize_inputs(input_paths, ffmpeg_exe):
    """
    Transcode each input's audio to AAC LC 48kHz stereo while copying video stream.
    Returns list of paths to normalized temporary files.
    """
    normalized = []
    for inp in input_paths:
        # Create a temp file next to system temp
        fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)
        cmd_norm = [
            ffmpeg_exe,
            "-y",
            "-i", inp,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            tmp_path ]
        try:
            proc = subprocess.run(cmd_norm, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode != 0:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise RuntimeError(f"Failed to normalize input {inp}: {proc.stderr.strip()}")
        except OSError as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise RuntimeError(f"Failed to run ffmpeg for normalization (is ffmpeg available?): {e}") from e
        normalized.append(tmp_path)
    return normalized


def merge_videos(videos, output, re_encode=True, use_nvenc=True):
    """Concatenate multiple videos using ffmpeg's concat demuxer.

    - If re_encode=True (default), re-encodes using libx264 (safe) or h264_nvenc when use_nvenc=True.
    - If re_encode=False, attempts stream copy (requires identical codecs/parameters).
    """

    # Locate ffmpeg: first look in PATH, then in a local Utilities/ffmpeg/bin folder
    local_ff = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")
    ffmpeg_exe = (shutil.which("ffmpeg") or shutil.which("ffmpeg.exe") or local_ff)

    # Fail fast if ffmpeg isn't available
    if not (shutil.which("ffmpeg") or shutil.which("ffmpeg.exe") or os.path.exists(local_ff)):
        raise FileNotFoundError(
            "ffmpeg executable not found. Install ffmpeg and ensure it's on PATH, or place ffmpeg.exe in Utilities/ffmpeg/bin/")

    # Create a temporary file list for the concat demuxer (safer than concat: URI when re-encoding)
    list_file = None
    try:
        # Optionally normalize inputs to avoid decoder errors (AAC variants, timestamps)
        temp_normalized = _normalize_inputs(videos, ffmpeg_exe) if re_encode else None
        inputs_for_list = temp_normalized if temp_normalized is not None else videos

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as f:
            list_file = f.name
            for p in inputs_for_list:
                # ffmpeg concat demuxer expects lines like: file 'path/to/file'
                f.write("file '")
                f.write(p.replace("'", "'\\''"))
                f.write("'\n")

        # Build command depending on whether we re-encode or copy streams
        if not re_encode:
            cmd = [
                ffmpeg_exe,
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                output ]
        else:
            if use_nvenc:
                # Optimized settings for RTX 4060
                cmd = [
                    ffmpeg_exe,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c:v", "h264_nvenc",
                    "-preset", "p2",         # Lower preset number = faster encoding
                    "-tune", "hq",           # High quality tuning
                    "-rc", "vbr",           # Variable bitrate
                    "-cq", "24",            # Quality-based VBR (lower = better quality)
                    "-qmin", "20",          # Minimum QP value
                    "-qmax", "28",          # Maximum QP value
                    "-b:v", "8M",           # Target bitrate 8Mbps
                    "-maxrate", "12M",      # Maximum bitrate 12Mbps
                    "-bufsize", "16M",      # Buffer size
                    "-profile:v", "high",   # High profile for better compression
                    "-spatial-aq", "1",     # Spatial AQ for better quality
                    "-c:a", "aac",
                    "-b:a", "192k",
                    output ]
                
                """
                # NVENC encoder options (ensure they are appropriate for your ffmpeg build)
                cmd = [
                    ffmpeg_exe,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c:v", "h264_nvenc",
                    "-preset", "p1",
                    "-rc", "vbr_hq",
                    "-b:v", "5M",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    output ]
                """
            else:
                # Software encode with libx264 (widely supported)
                cmd = [
                    ffmpeg_exe,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    output ]

        # Run ffmpeg and capture output to provide clearer error messages
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode != 0:
                raise RuntimeError(
                    f"ffmpeg failed (return code {proc.returncode}).\nCOMMAND: {' '.join(cmd)}\nSTDERR:\n{proc.stderr.strip()}")
        except OSError as e:
            raise RuntimeError(f"Failed to execute ffmpeg (is the path valid?): {e}") from e

    finally:
        # Clean up the temporary list file
        if list_file and os.path.exists(list_file):
            os.remove(list_file)
        # Clean up normalized temp files if any
        if 'temp_normalized' in locals() and temp_normalized:
            for t in temp_normalized:
                if os.path.exists(t):
                    os.remove(t)

if __name__ == "__main__":
    # Example usage (won't run on import)
    video_list = [
        "C:/Users/gudey/Downloads/mr.mp4",
        "C:/Users/gudey/Downloads/val.mp4",
        "C:/Users/gudey/Downloads/video.mp4",
        "C:/Users/gudey/Downloads/sm.mkv"
    ]
    # Default: re-encode with libx264. To attempt copy (fast), use reencode=False.
    merge_videos(video_list, "C:/Users/gudey/Downloads/side_by_side.mp4")
