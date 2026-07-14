from flask import Flask, flash, redirect, render_template, request, url_for
import uuid
from werkzeug.utils import secure_filename
import os
from pathlib import Path

from config import FLASK_SECRET_KEY

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_CONTENT_LENGTH = 25 * 1024 * 1024

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = FLASK_SECRET_KEY


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_job_id(raw_job_id):
    try:
        return str(uuid.UUID(raw_job_id))
    except (TypeError, ValueError):
        return None


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid4()
    if request.method == "POST":
        rec_id = safe_job_id(request.form.get("uuid"))
        desc = (request.form.get("text") or "").strip()
        files = [file for file in request.files.values() if file and file.filename]

        if not rec_id:
            flash("Invalid job id. Please try creating the reel again.", "error")
            return redirect(url_for("create"))

        if not desc:
            flash("Add a short voiceover script before creating the reel.", "error")
            return redirect(url_for("create"))

        if not files:
            flash("Upload at least one image.", "error")
            return redirect(url_for("create"))

        upload_path = Path(app.config['UPLOAD_FOLDER']) / rec_id
        upload_path.mkdir(parents=True, exist_ok=True)

        input_files = []
        for file in files:
            if not allowed_file(file.filename):
                flash(f"{file.filename} is not a supported image type.", "error")
                return redirect(url_for("create"))

            filename = secure_filename(file.filename)
            file.save(upload_path / filename)
            input_files.append(filename)

        with open(upload_path / "desc.txt", "w", encoding="utf-8") as f:
            f.write(desc)

        for fl in input_files:
            with open(upload_path / "input.txt", "a", encoding="utf-8") as f:
                f.write(f"file '{fl}'\nduration 1\n")

        flash("Your reel has been queued. Start the worker to render it.", "success")
        return redirect(url_for("gallery"))

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels_dir = Path("static/reels")
    reels_dir.mkdir(parents=True, exist_ok=True)
    reels = sorted(os.listdir(reels_dir), reverse=True)
    return render_template("gallery.html", reels=reels)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
