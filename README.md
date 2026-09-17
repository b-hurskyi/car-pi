# Raspberry Pi Car Computer

Experimental custom car-computer platform built around Raspberry Pi.

The goal is not to create another generic Raspberry Pi dashboard, but to build a modular platform that can combine vehicle telemetry, custom UI, phone integration, navigation-related features, media information, diagnostics, and future hardware experiments.

## Status

Early development.

The current goal is to establish the basic software architecture and create the first end-to-end telemetry pipeline.

## Initial stack

### Frontend

- React
- TypeScript
- Vite

### Backend

- Python
- FastAPI
- WebSocket

### Target

- Raspberry Pi
- Linux

Development is primarily performed on macOS.

## First milestone

The first milestone is:

```text
Mock telemetry
      ↓
Python backend
      ↓
WebSocket
      ↓
React frontend
```

The frontend should receive live simulated vehicle telemetry such as:

```json
{
  "speedKph": 72,
  "rpm": 2380,
  "gear": "D",
  "ignition": true,
  "engineRunning": true
}
```

The visual design is intentionally not the priority during the first milestone.

The purpose is to establish the data flow and architecture that later real telemetry sources can use.

## Development mode

Run the backend with Python 3.12 or newer:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

In another terminal, run the frontend with Node.js 24:

```bash
nvm use
cd frontend
npm install
npm run dev
```

Vite proxies `/ws/telemetry` to the backend at `127.0.0.1:8000` during development.

## Production build and run

Build the frontend with Node.js 24 before starting the backend:

```bash
nvm use
cd frontend
npm ci
npm run build
```

The generated `frontend/dist` directory is intentionally ignored by Git. FastAPI
detects that directory when the application starts and serves it at `/` alongside
the existing HTTP and WebSocket endpoints.

Run the complete application with Python 3.12 or newer:

```bash
cd ../backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in Chromium. The frontend, `/health`, and
`/ws/telemetry` all use the same FastAPI origin. Node.js and Vite are not required
while the built application is running.

## Future direction

Possible future integrations include:

- OBD-II
- GPS
- recorded trip replay
- phone integration
- media information
- Raspberry Pi system information
- trip history
- diagnostics
- custom automotive UI

These are directions, not committed MVP requirements.

## Safety

Vehicle integrations should initially be read-only.

The software must not send commands to the vehicle CAN bus or modify vehicle systems unless such functionality is explicitly designed and reviewed later.
