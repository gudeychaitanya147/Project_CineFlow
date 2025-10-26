import os
import shutil
import subprocess
import tempfile

def concat_videos_gpu(input_paths, output_path, ratio="1920:1080", quality=True):

	temp_ts_files = []
	scale = f"scale={ratio}:flags=lanczos"
	tmpdir = tempfile.mkdtemp(prefix="cineflow_concat_")
	ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")

	if quality:
		bv, cq, preset = "20M", "16", "p1"
		maxrate, bufsize, aq, rc_lookahead = "25M", "25M", "1", "32"
	else:
		bv, cq, preset = "10M", "20", "p3"
		maxrate, bufsize, aq, rc_lookahead = "12M", "12M", "0", "0"

	for idx, inp in enumerate(input_paths, start=1):
		base = os.path.join(tmpdir, f"part_{idx}.ts")
		temp_ts_files.append(base)

		cmd = [
			ffmpeg_path, "-y",
			"-i", inp,
			"-vf", scale,
			"-r", "60",
			"-c:v", "h264_nvenc",
			"-preset", preset,
			"-b:v", bv,
			"-maxrate", maxrate,
			"-bufsize", bufsize,
			"-rc", "vbr_hq",
			"-cq", cq,
			"-spatial-aq", aq,
			"-temporal-aq", aq,
			"-rc-lookahead", rc_lookahead,
			"-c:a", "aac",
			"-b:a", "320k",
			"-ar", "48000",
			"-f", "mpegts",
			base ]
		subprocess.run(cmd, check=True, capture_output=True, text=True)
		print("Encoded segment - " + inp)

	list_file = os.path.join(tmpdir, "concat_list.txt")
	with open(list_file, "w", encoding="utf-8") as fh:
		for ts in temp_ts_files:
			fh.write(f"file '{ts}'\n")

	final_cmd = [
		ffmpeg_path,
		"-y",
		"-f","concat",
		"-safe", "0",
		"-i", list_file,
		"-c", "copy",
		"-bsf:a", "aac_adtstoasc",
		output_path ]

	subprocess.run( final_cmd, check=True, capture_output=True, text=True)
	shutil.rmtree(tmpdir)
	print("Merged video saved to " + output_path)
