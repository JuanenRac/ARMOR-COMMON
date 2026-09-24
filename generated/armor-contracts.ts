/** Generated from the A.R.M.O.R. JSON Schemas by tools/generate_types.py. Do not edit. */

export type RadarTrack = {
  sensor_id: number;
  track_id: number;
  x_mm: number;
  y_mm: number;
  speed_mm_s: number;
};

export type Telemetry = {
  node_id: string;
  timestamp_ms: number;
  lux: number;
  targets: RadarTrack[];
};

export type Health = {
  node_id: string;
  timestamp_ms: number;
  online: boolean;
};

export type Command = {
  node_id: string;
  timestamp_ms: number;
  command: "calibrate" | "set_thresholds" | "restart";
  sensitivity?: number;
};

export const MAX_TARGETS = 15;
export const MAX_LUX = 200000;
export const NODE_ID_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;
export const COMMANDS = ["calibrate", "set_thresholds", "restart"] as const;
