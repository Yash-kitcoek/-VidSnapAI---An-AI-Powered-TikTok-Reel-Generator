from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
import uuid
from werkzeug.utils import secure_filename
import os
from pathlib import Path

from config import FLASK_SECRET_KEY
from db import create_job, get_job, init_db, list_jobs

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_CONTENT_LENGTH = 25 * 1024 * 1024

app = Flask(__name__)


def create_app():
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    init_db()
    return app


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

        create_job(rec_id, desc, str(upload_path))
        flash("Your reel has been queued for rendering.", "success")
        return redirect(url_for("job_status", job_id=rec_id))

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    jobs = list_jobs()
    return render_template("gallery.html", jobs=jobs)


@app.route("/jobs/<job_id>")
def job_status(job_id):
    job = get_job(job_id)
    if not job:
        flash("That reel job could not be found.", "error")
        return redirect(url_for("create"))
    return render_template("status.html", job=job)


@app.route("/api/jobs/<job_id>")
def job_status_api(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.errorhandler(413)
def upload_too_large(error):
    return render_template(
        "error.html",
        title="Upload too large",
        message="Your upload is larger than the 25 MB limit. Try fewer or smaller images.",
    ), 413


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "error.html",
        title="Page not found",
        message="The page you requested does not exist.",
    ), 404


@app.errorhandler(500)
def server_error(error):
    return render_template(
        "error.html",
        title="Something went wrong",
        message="The app hit an unexpected error. Please try again in a moment.",
    ), 500

app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
