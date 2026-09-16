import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.telemetry import MockTelemetryProvider, TelemetryProvider

app = FastAPI(title="Car Computer API")
telemetry_provider: TelemetryProvider = MockTelemetryProvider()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
