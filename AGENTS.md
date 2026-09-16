# AGENTS.md

## Project

This repository contains software for a custom Raspberry Pi based car computer.

The Raspberry Pi is the target runtime device, but most development is performed on macOS.

The project is intended to evolve into a modular car-computer platform rather than a single dashboard application.

## Main goals

The system should eventually support features such as:

- custom automotive dashboard UI
- vehicle telemetry
- OBD-II integration
- GPS
- phone integration
- media information and controls
- trip statistics and telemetry history
- Raspberry Pi system information
- additional hardware integrations where useful

Not all of these features belong to the initial MVP.

Do not implement future functionality unless explicitly requested.

## Technology direction

Frontend:

- React
- TypeScript
- Vite

Backend:

- Python
- FastAPI
- WebSocket for real-time telemetry
- HTTP API where request/response semantics are more appropriate

Target platform:

- Raspberry Pi running Linux

Development platform:

- macOS

## Architecture principles

Prefer a modular architecture with clear boundaries between:

- UI
- application logic
- vehicle/hardware integrations
- telemetry transport
- data providers

The frontend must not depend directly on Raspberry Pi hardware or a specific telemetry source.

Vehicle data should be exposed through abstractions so that different providers can be used.

Expected provider types include:

- mock provider for development
- replay provider for recorded telemetry
- OBD-II provider for real vehicle data

The same frontend should work regardless of which provider produces telemetry.

## Current development phase

The project is currently at the foundation stage.

The first vertical slice should prove this flow:

Mock telemetry
→ Python backend
→ WebSocket
→ React frontend

Initial telemetry can contain only a minimal vehicle state such as:

- speed
- RPM
- gear
- ignition state
- engine running state

Do not build a large dashboard, OBD integration, GPS integration, authentication, persistence, cloud infrastructure, or other future functionality during this phase unless explicitly requested.

## Development rules

Prioritize:

- simple solutions
- readable code
- strong typing
- testable components
- explicit interfaces
- separation of concerns
- graceful error handling
- code that can run both during macOS development and on Raspberry Pi

Avoid:

- unnecessary abstractions
- premature microservices
- premature database usage
- unnecessary dependencies
- hardware-specific logic leaking into application or UI layers
- implementing speculative future requirements

Do not overengineer.

Introduce an abstraction only when it has a clear purpose in the current architecture.

## Hardware safety

Vehicle integrations must default to read-only behavior.

Do not implement CAN bus writes, ECU modifications, lock/unlock control, ignition control, window control, or other vehicle commands unless explicitly requested.

OBD-II/CAN integrations should initially be treated as telemetry sources only.

## Workflow

Before implementing a significant feature:

1. inspect the existing architecture
2. identify the smallest change required
3. explain any architectural decision that affects future development
4. implement the change
5. add or update tests
6. run relevant formatting, linting, tests, and builds
7. update documentation when architecture or project assumptions change

Do not silently change major technology or architectural decisions.

## Documentation

Keep documentation aligned with the implementation.

Update `docs/ARCHITECTURE.md` when:

- components or boundaries change
- communication mechanisms change
- new telemetry providers are introduced
- deployment/runtime architecture changes

Update this file when development rules or project-wide conventions change.
