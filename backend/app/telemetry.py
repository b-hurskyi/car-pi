import math
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class TelemetrySnapshot(BaseModel):
    """Normalized vehicle telemetry exposed to API consumers."""

    model_config = ConfigDict(populate_by_name=True)

    speed_kph: int = Field(alias="speedKph", ge=0)
    rpm: int = Field(ge=0)
    gear: str
    ignition: bool
    engine_running: bool = Field(alias="engineRunning")


class TelemetryProvider(Protocol):
    def snapshot(self) -> TelemetrySnapshot:
        """Return the provider's current normalized telemetry state."""


class MockTelemetryProvider:
    """Generate deterministic telemetry for local development."""

    _cycle_steps = 80
    _peak_speed_kph = 100

    def __init__(self) -> None:
        self._step = 0

    def snapshot(self) -> TelemetrySnapshot:
        cycle_position = self._step % self._cycle_steps
        rising_steps = self._cycle_steps // 2
        distance_from_stop = min(
            cycle_position,
            self._cycle_steps - cycle_position,
        )
        speed_kph = round(distance_from_stop * self._peak_speed_kph / rising_steps)

        if speed_kph == 0:
            gear = "P"
            rpm = 750
        else:
            gear = "D"
            rpm = round(900 + speed_kph * 28 + 120 * math.sin(self._step / 2))

        self._step += 1

        return TelemetrySnapshot(
            speed_kph=speed_kph,
            rpm=rpm,
            gear=gear,
            ignition=True,
            engine_running=True,
        )
