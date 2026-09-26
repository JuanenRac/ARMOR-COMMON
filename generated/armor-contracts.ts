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

export type Info = {
  node_id: string;
  timestamp_ms: number;
  name: string;
  firmware: string;
  ip: string;
  port: number;
};

export type SolarInverter = {
  kind: string;
  node_id: string;
  device: string;
  timestamp_ms: number;
  mode: "power_on" | "standby" | "line" | "battery" | "fault" | "power_saving" | "shutdown" | "unknown";
  grid_v: number;
  grid_hz: number;
  out_v: number;
  out_hz: number;
  out_va: number;
  out_w: number;
  load_percent: number;
  battery_v: number;
  battery_a: number;
  battery_percent: number;
  pv_v: number;
  pv_a: number;
  pv_w: number;
  heatsink_c: number;
  ac_charging: boolean;
  pv_charging: boolean;
  load_on: boolean;
  warnings: string[];
};

export type SolarModule = {
  n: number;
  present: boolean;
  voltage_v?: number;
  current_a?: number;
  temperature_c?: number;
  soc_percent?: number;
  state?: string;
  cells_v?: number[];
  temperatures_c?: number[];
  capacity_ah?: number;
  full_capacity_ah?: number;
  cycles?: number;
  health_percent?: number;
};

export type SolarBattery = {
  kind: string;
  node_id: string;
  device: string;
  timestamp_ms: number;
  modules: number;
  state?: "charging" | "discharging" | "idle";
  voltage_v?: number;
  current_a?: number;
  temperature_min_c?: number;
  temperature_max_c?: number;
  cell_min_v?: number;
  cell_max_v?: number;
  soc_percent?: number;
  alarm?: boolean;
  stack: SolarModule[];
  model?: string;
  capacity_ah?: number;
  full_capacity_ah?: number;
  energy_kwh?: number;
  cycles?: number;
  health_percent?: number;
};

export const MAX_TARGETS = 15;
export const MAX_LUX = 200000;
export const NODE_ID_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;
export const COMMANDS = ["calibrate", "set_thresholds", "restart"] as const;
