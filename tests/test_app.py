import io
import importlib


def load_app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.sqlite3"))
    main = importlib.import_module("main")
    app = main.create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app


def test_create_rejects_missing_description(monkeypatch, tmp_path):
    app = load_app(monkeypatch, tmp_path)

    response = app.test_client().post(
        "/create",
        data={"uuid": "00000000-0000-4000-8000-000000000000", "text": ""},
        content_type="multipart/form-data",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/create")


def test_create_rejects_unsupported_file(monkeypatch, tmp_path):
    app = load_app(monkeypatch, tmp_path)

    response = app.test_client().post(
        "/create",
        data={
            "uuid": "00000000-0000-4000-8000-000000000001",
            "text": "Make a short launch reel.",
            "file1": (io.BytesIO(b"not an image"), "payload.exe"),
        },
        content_type="multipart/form-data",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/create")


def test_unknown_job_returns_404(monkeypatch, tmp_path):
    app = load_app(monkeypatch, tmp_path)

    response = app.test_client().get("/api/jobs/00000000-0000-4000-8000-000000000404")

    assert response.status_code == 404
