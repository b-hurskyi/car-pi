import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from app.system_telemetry import (
    LinuxSystemTelemetryProvider,
    SystemTelemetryProvider,
    SystemTelemetrySnapshot,
)
from app.telemetry import MockTelemetryProvider, TelemetryProvider

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

app = FastAPI(title="Car Computer API")
telemetry_provider: TelemetryProvider = MockTelemetryProvider()
system_telemetry_provider: SystemTelemetryProvider = LinuxSystemTelemetryProvider()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/system")
def system_telemetry() -> SystemTelemetrySnapshot:
    return system_telemetry_provider.snapshot()


@app.websocket("/ws/telemetry")
async def telemetry(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            snapshot = telemetry_provider.snapshot()
            await websocket.send_json(snapshot.model_dump(by_alias=True))

            try:
                message = await asyncio.wait_for(websocket.receive(), timeout=0.5)
            except TimeoutError:
                continue

            if message["type"] == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass


def mount_frontend(application: FastAPI, directory: Path) -> None:
    if directory.is_dir():
        application.mount(
            "/", StaticFiles(directory=directory, html=True), name="frontend"
        )


mount_frontend(app, FRONTEND_DIST)
