from text_to_audio import text_to_speech_file
import logging
import time
import subprocess
from pathlib import Path

from config import WORKER_POLL_SECONDS
from db import get_next_queued_job, init_db, update_job


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("vidsnapai.worker")


def text_to_audio(folder):
    logger.info("Generating voiceover for job %s", folder)
    with open(Path("user_uploads") / folder / "desc.txt", encoding="utf-8") as f:
        text = f.read()
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

    logger.info("Rendered reel for job %s", folder)
    return output_file

if __name__ == "__main__":
    init_db()
    logger.info("Worker started with %s second polling", WORKER_POLL_SECONDS)
    while True:
        job = get_next_queued_job()
        if job:
            folder = job["id"]
            try:
                logger.info("Processing job %s", folder)
                update_job(folder, "processing")
                text_to_audio(folder)
                output_file = create_reel(folder)
                update_job(folder, "completed", output_path=str(output_file).replace("\\", "/"))
            except Exception as exc:
                update_job(folder, "failed", error=str(exc))
                logger.exception("Job %s failed", folder)
        time.sleep(WORKER_POLL_SECONDS)
