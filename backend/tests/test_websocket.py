from fastapi.testclient import TestClient

from app.main import app
from app.telemetry import TelemetrySnapshot


def test_telemetry_websocket_delivers_valid_snapshot() -> None:
    client = TestClient(app)

    with client.websocket_connect("/ws/telemetry") as websocket:
        payload = websocket.receive_json()

    snapshot = TelemetrySnapshot.model_validate(payload)

    assert payload == snapshot.model_dump(by_alias=True)
