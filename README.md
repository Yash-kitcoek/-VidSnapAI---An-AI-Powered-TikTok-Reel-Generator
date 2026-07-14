# VidSnapAI

VidSnapAI is a Flask-based AI reel generator that accepts image uploads, creates a voiceover with ElevenLabs, and renders a vertical reel with FFmpeg.

## Current Level

This codebase is moving from proof-of-concept toward a deployable portfolio project. The current implementation is suitable for local demos after configuring secrets, but it still needs a real job queue, job status UI, and cloud storage before it should be marketed as production-ready.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system flow and next engineering milestones.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your ElevenLabs API key.
4. Install FFmpeg and make sure `ffmpeg` is available on your PATH.
5. Start the web app:

```bash
python main.py
```

6. In a second terminal, start the worker:

```bash
python generate_process.py
```

## Docker

Run both the Flask web app and the background worker:

```bash
docker compose up --build
```

The compose setup mounts `data/`, `user_uploads/`, and `static/reels/` so jobs and generated videos survive container restarts.

## Tests

```bash
pytest
```

## Security Notes

Never commit real API keys. The ElevenLabs key must live in `.env` or in your deployment provider's secret manager.

## Portfolio Roadmap

- Add SQLite or Postgres job tracking with queued, processing, completed, and failed states.
- Replace `done.txt` with a real queue such as RQ or Celery plus Redis.
- Add a status page so users can watch render progress and download the final reel.
- Store uploads and generated reels in S3-compatible object storage.
- Add Docker and docker-compose for one-command local deployment.
- Add tests and GitHub Actions for linting and basic route coverage.
