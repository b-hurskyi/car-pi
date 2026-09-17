import "./App.css";
import {
  type TelemetryConnectionState,
  useTelemetry,
} from "./useTelemetry";
import { useSystemTelemetry } from "./useSystemTelemetry";

const connectionLabels: Record<TelemetryConnectionState, string> = {
  connecting: "Connecting",
  connected: "Connected",
  disconnected: "Disconnected",
  error: "Connection error",
};

function formatMetric(value: number | null | undefined, suffix: string): string {
  return value == null ? "Unavailable" : `${value.toLocaleString()}${suffix}`;
}

export function App() {
  const { telemetry, connectionState } = useTelemetry();
  const systemTelemetry = useSystemTelemetry();

  return (
    <main className="app-shell">
      <section className="status-panel" aria-labelledby="app-title">
        <p className="eyebrow" data-state={connectionState}>
          Telemetry: {connectionLabels[connectionState]}
        </p>
        <h1 id="app-title">Car Computer</h1>

        <div className="dashboard-content">
          {telemetry ? (
            <div className="telemetry" aria-live="polite">
              <p className="speed">
                <strong>{telemetry.speedKph}</strong> km/h
              </p>
              <p className="rpm">{telemetry.rpm} RPM</p>
              <p className="gear">Gear {telemetry.gear}</p>
              <dl className="vehicle-state">
                <div>
                  <dt>Ignition</dt>
                  <dd>{telemetry.ignition ? "ON" : "OFF"}</dd>
                </div>
                <div>
                  <dt>Engine</dt>
                  <dd>{telemetry.engineRunning ? "RUNNING" : "STOPPED"}</dd>
                </div>
              </dl>
            </div>
          ) : (
            <p className="status-text">Waiting for telemetry</p>
          )}

          <section className="system-panel" aria-labelledby="system-title">
            <h2 id="system-title">System</h2>
            <dl className="system-metrics">
              <div>
                <dt>CPU temperature</dt>
                <dd>
                  {formatMetric(systemTelemetry?.cpuTemperatureC, " °C")}
                </dd>
              </div>
              <div>
                <dt>CPU usage</dt>
                <dd>{formatMetric(systemTelemetry?.cpuUsagePercent, "%")}</dd>
              </div>
              <div>
                <dt>RAM usage</dt>
                <dd>{formatMetric(systemTelemetry?.memoryUsedPercent, "%")}</dd>
              </div>
              <div>
                <dt>Uptime</dt>
                <dd>{formatMetric(systemTelemetry?.uptimeSeconds, " s")}</dd>
              </div>
            </dl>
          </section>
        </div>
      </section>
    </main>
  );
}
