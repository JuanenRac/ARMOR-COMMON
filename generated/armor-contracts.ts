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
  pv2_v?: number;
  pv2_a?: number;
  pv2_w?: number;
  total_out_w?: number;
  total_out_va?: number;
  total_load_percent?: number;
  total_charging_a?: number;
  units?: unknown[];
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

export type ElectricalChannel = {
  id: string;
  domain: "ac" | "dc";
  label?: string;
  voltage_v?: number;
  current_a?: number;
  power_w?: number;
  energy_kwh?: number;
  frequency_hz?: number;
  power_factor?: number;
  state?: "closed" | "open" | "unknown";
  alarm?: boolean;
  alarm_code?: string;
};

export type ElectricalSwitch = {
  id: string;
  kind: string;
  label?: string;
  source_a?: string;
  source_b?: string;
  a_closed: boolean;
  b_closed: boolean;
  selected: "none" | "a" | "b";
  wanted: "none" | "a" | "b";
  closing: boolean;
  armed: boolean;
  fault: "none" | "did_not_close" | "did_not_open" | "both_closed" | "disabled";
};

export type Electrical = {
  kind: string;
  node_id: string;
  timestamp_ms: number;
  switching_enabled?: boolean;
  channels: ElectricalChannel[];
  switches?: ElectricalSwitch[];
};

export type ElectricalCommand = {
  kind: string;
  node_id: string;
  timestamp_ms: number;
  command_id: string;
  switch: string;
  action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
  token?: string;
};

export type ElectricalResult = {
  kind: string;
  node_id: string;
  timestamp_ms: number;
  command_id: string;
  switch: string;
  action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
  accepted: boolean;
  refusal: "none" | "disabled" | "fault" | "not_armed" | "not_confirmed_open" | "unknown_switch" | "bad_token" | "not_supported";
  token?: string;
};

export const MAX_TARGETS = 15;
export const MAX_LUX = 200000;
export const NODE_ID_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;
export const COMMANDS = ["calibrate", "set_thresholds", "restart"] as const;
