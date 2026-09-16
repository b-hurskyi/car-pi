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
