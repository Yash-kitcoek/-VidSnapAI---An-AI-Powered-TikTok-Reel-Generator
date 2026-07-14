from text_to_audio import text_to_speech_file
import time
import subprocess
from pathlib import Path

from db import get_next_queued_job, init_db, update_job


def text_to_audio(folder):
    print("TTA - ", folder)
    with open(Path("user_uploads") / folder / "desc.txt", encoding="utf-8") as f:
        text = f.read()
    print(text, folder)
    text_to_speech_file(text, folder)

def create_reel(folder):
    input_file = Path("user_uploads") / folder / "input.txt"
    audio_file = Path("user_uploads") / folder / "audio.mp3"
    output_file = Path("static") / "reels" / f"{folder}.mp4"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(input_file),
        "-i", str(audio_file),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        str(output_file),
    ]
    subprocess.run(command, check=True)
    
    print("CR - ", folder)
    return output_file

if __name__ == "__main__":
    init_db()
    while True:
        print("Processing queue...")
        job = get_next_queued_job()
        if job:
            folder = job["id"]
            try:
                update_job(folder, "processing")
                text_to_audio(folder)
                output_file = create_reel(folder)
                update_job(folder, "completed", output_path=str(output_file).replace("\\", "/"))
            except Exception as exc:
                update_job(folder, "failed", error=str(exc))
                print(f"Job {folder} failed: {exc}")
        time.sleep(4)
