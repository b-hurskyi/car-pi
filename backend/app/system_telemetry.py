from collections.abc import Callable
from pathlib import Path
from threading import Lock
from typing import NamedTuple, Protocol

from pydantic import BaseModel, ConfigDict, Field


class SystemTelemetrySnapshot(BaseModel):
    """Normalized host metrics exposed to API consumers."""

    model_config = ConfigDict(populate_by_name=True)

    cpu_temperature_c: float | None = Field(alias="cpuTemperatureC")
    cpu_usage_percent: float | None = Field(
        alias="cpuUsagePercent",
        ge=0,
        le=100,
    )
    memory_used_percent: float | None = Field(
        alias="memoryUsedPercent",
        ge=0,
        le=100,
    )
    uptime_seconds: int | None = Field(alias="uptimeSeconds", ge=0)


class SystemTelemetryProvider(Protocol):
    def snapshot(self) -> SystemTelemetrySnapshot:
        """Return the current normalized system telemetry state."""


class CpuTimes(NamedTuple):
    total: int
    idle: int


def parse_cpu_times(content: str) -> CpuTimes:
    fields = content.splitlines()[0].split()
    if not fields or fields[0] != "cpu":
        raise ValueError("Missing aggregate CPU line")

    values = [int(value) for value in fields[1:]]
    if len(values) < 4:
        raise ValueError("Incomplete aggregate CPU line")

    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return CpuTimes(total=sum(values[:8]), idle=idle)


def calculate_cpu_usage_percent(
    previous: CpuTimes,
    current: CpuTimes,
) -> float | None:
    total_delta = current.total - previous.total
    idle_delta = current.idle - previous.idle
    if total_delta <= 0 or idle_delta < 0:
        return None

    usage = (total_delta - idle_delta) / total_delta * 100
    return round(min(100.0, max(0.0, usage)), 1)


def parse_memory_used_percent(content: str) -> float:
    values: dict[str, int] = {}
    for line in content.splitlines():
        name, separator, raw_value = line.partition(":")
        if separator:
            values[name] = int(raw_value.split()[0])

    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if total is None or available is None or total <= 0:
        raise ValueError("Missing usable memory values")

    used_percent = (total - available) / total * 100
    return round(min(100.0, max(0.0, used_percent)), 1)


def parse_temperature_celsius(content: str) -> float:
    return round(float(content.strip()) / 1_000, 1)


def parse_uptime_seconds(content: str) -> int:
    return int(float(content.split()[0]))


def _read_metric[Metric](
    path: Path,
    parser: Callable[[str], Metric],
) -> Metric | None:
    try:
        return parser(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, IndexError):
        return None


class LinuxSystemTelemetryProvider:
    """Read system telemetry from Linux procfs and sysfs interfaces."""

    def __init__(
        self,
        proc_root: Path = Path("/proc"),
        sys_root: Path = Path("/sys"),
    ) -> None:
        self._proc_root = proc_root
        self._sys_root = sys_root
        self._previous_cpu_times: CpuTimes | None = None
        self._lock = Lock()

    def snapshot(self) -> SystemTelemetrySnapshot:
        with self._lock:
            current_cpu_times = _read_metric(
                self._proc_root / "stat",
                parse_cpu_times,
            )
            cpu_usage_percent = (
                calculate_cpu_usage_percent(
                    self._previous_cpu_times,
                    current_cpu_times,
                )
                if self._previous_cpu_times is not None
                and current_cpu_times is not None
                else None
            )
            if current_cpu_times is not None:
                self._previous_cpu_times = current_cpu_times

        return SystemTelemetrySnapshot(
            cpu_temperature_c=_read_metric(
                self._sys_root / "class/thermal/thermal_zone0/temp",
                parse_temperature_celsius,
            ),
            cpu_usage_percent=cpu_usage_percent,
            memory_used_percent=_read_metric(
                self._proc_root / "meminfo",
                parse_memory_used_percent,
            ),
            uptime_seconds=_read_metric(
                self._proc_root / "uptime",
                parse_uptime_seconds,
            ),
        )
