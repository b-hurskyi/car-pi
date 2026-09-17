import { useEffect, useState } from "react";

export interface SystemTelemetrySnapshot {
  cpuTemperatureC: number | null;
  cpuUsagePercent: number | null;
  memoryUsedPercent: number | null;
  uptimeSeconds: number | null;
}

const pollIntervalMs = 2_000;

function isNullableNumber(value: unknown): value is number | null {
  return value === null || (typeof value === "number" && Number.isFinite(value));
}

function isSystemTelemetrySnapshot(
  value: unknown,
): value is SystemTelemetrySnapshot {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const snapshot = value as Record<string, unknown>;

  return (
    isNullableNumber(snapshot.cpuTemperatureC) &&
    isNullableNumber(snapshot.cpuUsagePercent) &&
    isNullableNumber(snapshot.memoryUsedPercent) &&
    isNullableNumber(snapshot.uptimeSeconds)
  );
}

export function useSystemTelemetry(): SystemTelemetrySnapshot | null {
  const [telemetry, setTelemetry] = useState<SystemTelemetrySnapshot | null>(null);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    const loadTelemetry = async () => {
      try {
        const response = await fetch("/api/system", {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error("System telemetry request failed");
        }

        const payload: unknown = await response.json();
        if (!isSystemTelemetrySnapshot(payload)) {
          throw new Error("Invalid system telemetry payload");
        }

        if (active) {
          setTelemetry(payload);
        }
      } catch {
        if (active) {
          setTelemetry(null);
        }
      }
    };

    void loadTelemetry();
    const interval = window.setInterval(() => {
      void loadTelemetry();
    }, pollIntervalMs);

    return () => {
      active = false;
      controller.abort();
      window.clearInterval(interval);
    };
  }, []);

  return telemetry;
}
