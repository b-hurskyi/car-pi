import "./App.css";
import {
  type TelemetryConnectionState,
  useTelemetry,
} from "./useTelemetry";

const connectionLabels: Record<TelemetryConnectionState, string> = {
  connecting: "Connecting",
  connected: "Connected",
  disconnected: "Disconnected",
  error: "Connection error",
};

export function App() {
  const { telemetry, connectionState } = useTelemetry();

  return (
    <main className="app-shell">
      <section className="status-panel" aria-labelledby="app-title">
        <p className="eyebrow" data-state={connectionState}>
          Telemetry: {connectionLabels[connectionState]}
        </p>
        <h1 id="app-title">Car Computer</h1>

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
      </section>
    </main>
  );
}
