# This file looks for new folders inside user uploads and converts them to reel if they are not already converted
import os 
from text_to_audio import text_to_speech_file
import time
import subprocess
from pathlib import Path


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

if __name__ == "__main__":
    while True:
        print("Processing queue...")
        Path("done.txt").touch()
        with open("done.txt", "r", encoding="utf-8") as f:
            done_folders = f.readlines()

        done_folders = [f.strip() for f in done_folders]
        folders = os.listdir("user_uploads") 
        for folder in folders:
            if(folder not in done_folders): 
                text_to_audio(folder) # Generate the audio.mp3 from desc.txt
                create_reel(folder) # Convert the images and audio.mp3 inside the folder to a reel
                with open("done.txt", "a", encoding="utf-8") as f:
                    f.write(folder + "\n")
        time.sleep(4)
