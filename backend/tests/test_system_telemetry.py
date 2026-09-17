from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main
from app.system_telemetry import (
    CpuTimes,
    LinuxSystemTelemetryProvider,
    SystemTelemetrySnapshot,
    calculate_cpu_usage_percent,
    parse_cpu_times,
    parse_memory_used_percent,
    parse_temperature_celsius,
    parse_uptime_seconds,
)


def test_parses_linux_system_metrics() -> None:
    assert parse_cpu_times("cpu  100 20 30 400 10 5 3 2 0 0\n") == CpuTimes(
        total=570,
        idle=410,
    )
    assert (
        parse_memory_used_percent("MemTotal:       1000 kB\nMemAvailable:    250 kB\n")
        == 75.0
    )
    assert parse_temperature_celsius("55321\n") == 55.3
    assert parse_uptime_seconds("12345.67 45678.90\n") == 12345


def test_calculates_cpu_usage_from_counter_deltas() -> None:
    previous = CpuTimes(total=1_000, idle=700)
    current = CpuTimes(total=1_200, idle=780)

    assert calculate_cpu_usage_percent(previous, current) == 60.0


def test_linux_provider_reads_metrics_without_hardware(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    sys_root = tmp_path / "sys"
    thermal_root = sys_root / "class/thermal/thermal_zone0"
    proc_root.mkdir()
    thermal_root.mkdir(parents=True)

    (proc_root / "stat").write_text(
        "cpu  100 20 30 400 10 5 3 2 0 0\n",
        encoding="utf-8",
    )
    (proc_root / "meminfo").write_text(
        "MemTotal:       1000 kB\nMemAvailable:    250 kB\n",
        encoding="utf-8",
    )
    (proc_root / "uptime").write_text("12345.67 45678.90\n", encoding="utf-8")
    (thermal_root / "temp").write_text("55321\n", encoding="utf-8")

    provider = LinuxSystemTelemetryProvider(proc_root=proc_root, sys_root=sys_root)
    first_snapshot = provider.snapshot()

    (proc_root / "stat").write_text(
        "cpu  155 20 50 470 20 8 5 2 0 0\n",
        encoding="utf-8",
    )
    second_snapshot = provider.snapshot()

    assert first_snapshot.cpu_temperature_c == 55.3
    assert first_snapshot.cpu_usage_percent is None
    assert first_snapshot.memory_used_percent == 75.0
    assert first_snapshot.uptime_seconds == 12345
    assert second_snapshot.cpu_usage_percent == 50.0


def test_linux_provider_returns_unavailable_metrics_for_missing_files(
    tmp_path: Path,
) -> None:
    provider = LinuxSystemTelemetryProvider(
        proc_root=tmp_path / "proc",
        sys_root=tmp_path / "sys",
    )

    assert provider.snapshot().model_dump() == {
        "cpu_temperature_c": None,
        "cpu_usage_percent": None,
        "memory_used_percent": None,
        "uptime_seconds": None,
    }


def test_system_endpoint_uses_separate_contract(monkeypatch) -> None:
    snapshot = SystemTelemetrySnapshot(
        cpu_temperature_c=55.3,
        cpu_usage_percent=12.5,
        memory_used_percent=48.2,
        uptime_seconds=12345,
    )

    class StubSystemTelemetryProvider:
        def snapshot(self) -> SystemTelemetrySnapshot:
            return snapshot

    monkeypatch.setattr(
        main,
        "system_telemetry_provider",
        StubSystemTelemetryProvider(),
    )

    response = TestClient(main.app).get("/api/system")

    assert response.status_code == 200
    assert response.json() == {
        "cpuTemperatureC": 55.3,
        "cpuUsagePercent": 12.5,
        "memoryUsedPercent": 48.2,
        "uptimeSeconds": 12345,
    }
