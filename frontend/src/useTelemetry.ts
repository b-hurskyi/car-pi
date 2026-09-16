import { useEffect, useState } from "react";

export interface TelemetrySnapshot {
  speedKph: number;
  rpm: number;
  gear: string;
  ignition: boolean;
  engineRunning: boolean;
}

export type TelemetryConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

interface TelemetryConnection {
  telemetry: TelemetrySnapshot | null;
  connectionState: TelemetryConnectionState;
}

const initialReconnectDelayMs = 2_000;
const maximumReconnectDelayMs = 30_000;

function getTelemetryUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws/telemetry`;
}

function isTelemetrySnapshot(value: unknown): value is TelemetrySnapshot {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const snapshot = value as Record<string, unknown>;

  return (
    Number.isFinite(snapshot.speedKph) &&
    Number.isFinite(snapshot.rpm) &&
    typeof snapshot.gear === "string" &&
    typeof snapshot.ignition === "boolean" &&
    typeof snapshot.engineRunning === "boolean"
  );
}

export function useTelemetry(): TelemetryConnection {
  const [telemetry, setTelemetry] = useState<TelemetrySnapshot | null>(null);
  const [connectionState, setConnectionState] =
    useState<TelemetryConnectionState>("connecting");

  useEffect(() => {
    let active = true;
    let reconnectTimer: number | undefined;
    let reconnectDelayMs = initialReconnectDelayMs;
    let socket: WebSocket | undefined;

    const connect = () => {
      const nextSocket = new WebSocket(getTelemetryUrl());
      let connectionErrored = false;
      socket = nextSocket;

      nextSocket.addEventListener("open", () => {
        if (active) {
          reconnectDelayMs = initialReconnectDelayMs;
          setConnectionState("connected");
        }
      });

      nextSocket.addEventListener("message", (event) => {
        if (!active) {
          return;
        }

        try {
          const payload: unknown = JSON.parse(String(event.data));

          if (!isTelemetrySnapshot(payload)) {
            throw new Error("Invalid telemetry payload");
          }

          setTelemetry(payload);
        } catch {
          connectionErrored = true;
          setConnectionState("error");
          nextSocket.close();
        }
      });

      nextSocket.addEventListener("error", () => {
        if (active) {
          connectionErrored = true;
          setConnectionState("error");
        }
      });

      nextSocket.addEventListener("close", () => {
        if (!active) {
          return;
        }

        if (!connectionErrored) {
          setConnectionState("disconnected");
        }

        reconnectTimer = window.setTimeout(() => {
          if (active) {
            setConnectionState("connecting");
            connect();
          }
        }, reconnectDelayMs);
        reconnectDelayMs = Math.min(
          reconnectDelayMs * 2,
          maximumReconnectDelayMs,
        );
      });
    };

    connect();

    return () => {
      active = false;
      window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  return { telemetry, connectionState };
}
