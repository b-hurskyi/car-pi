from app.telemetry import MockTelemetryProvider


def test_mock_provider_generates_changing_coherent_telemetry() -> None:
    provider = MockTelemetryProvider()

    snapshots = [provider.snapshot() for _ in range(81)]

    assert len({snapshot.speed_kph for snapshot in snapshots}) > 1
    assert len({snapshot.rpm for snapshot in snapshots}) > 1

    for snapshot in snapshots:
        assert 0 <= snapshot.speed_kph <= 100
        assert 0 <= snapshot.rpm <= 4_000
        assert snapshot.engine_running is snapshot.ignition
        assert snapshot.gear == ("P" if snapshot.speed_kph == 0 else "D")


def test_telemetry_snapshot_uses_normalized_api_names() -> None:
    payload = MockTelemetryProvider().snapshot().model_dump(by_alias=True)

    assert set(payload) == {
        "speedKph",
        "rpm",
        "gear",
        "ignition",
        "engineRunning",
    }
