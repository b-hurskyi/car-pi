from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import mount_frontend


def test_missing_frontend_build_does_not_block_backend(tmp_path) -> None:
    application = FastAPI()

    mount_frontend(application, tmp_path / "missing")

    assert TestClient(application).get("/").status_code == 404


def test_built_frontend_is_served_from_root(tmp_path) -> None:
    frontend_directory = tmp_path / "dist"
    assets_directory = frontend_directory / "assets"
    assets_directory.mkdir(parents=True)
    (frontend_directory / "index.html").write_text(
        '<main id="root">Car Computer</main>',
        encoding="utf-8",
    )
    (assets_directory / "app.css").write_text(
        "body { background: #111418; }",
        encoding="utf-8",
    )

    application = FastAPI()
    mount_frontend(application, frontend_directory)
    client = TestClient(application)

    index_response = client.get("/")
    asset_response = client.get("/assets/app.css")

    assert index_response.status_code == 200
    assert "Car Computer" in index_response.text
    assert asset_response.status_code == 200
    assert asset_response.text == "body { background: #111418; }"
