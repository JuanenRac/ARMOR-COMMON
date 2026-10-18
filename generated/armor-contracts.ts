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
  kind?: "radar" | "panel";
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

export type SolarInverterUnits = {
  unit: number;
  serial?: string;
  mode: "power_on" | "standby" | "line" | "battery" | "fault" | "power_saving" | "shutdown" | "unknown";
  fault_code?: string;
  grid_v?: number;
  out_v?: number;
  out_va?: number;
  out_w?: number;
  load_percent?: number;
  battery_v?: number;
  battery_percent?: number;
  pv_v?: number;
  charging_a?: number;
};

export type SolarInverterRatings = {
  grid_rating_v?: number;
  out_rating_v?: number;
  out_rating_hz?: number;
  out_rating_va?: number;
  out_rating_w?: number;
  battery_rating_v?: number;
  battery_recharge_v?: number;
  battery_under_v?: number;
  battery_bulk_v?: number;
  battery_float_v?: number;
  max_charge_a?: number;
  max_ac_charge_a?: number;
  battery_type?: "agm" | "flooded" | "user";
  input_range?: "appliance" | "ups";
  output_priority?: "utility_first" | "solar_first" | "sbu";
  charger_priority?: "utility_first" | "solar_first" | "solar_and_utility" | "solar_only";
};

export type SolarInverter = {
  kind: "inverter";
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
  warnings_known?: boolean;
  pv2_v?: number;
  pv2_a?: number;
  pv2_w?: number;
  total_out_w?: number;
  total_out_va?: number;
  total_load_percent?: number;
  total_charging_a?: number;
  units?: SolarInverterUnits[];
  bus_v?: number;
  serial?: string;
  firmware?: string;
  pv_energy_total_wh?: number;
  ratings?: SolarInverterRatings;
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
  kind: "battery";
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
  power_w?: number;
  balancing?: number;
  protecting?: boolean;
  charge_mos?: number;
  discharge_mos?: number;
};

export type ElectricalChannel = {
  id: string;
  domain: "ac" | "dc";
  label?: string;
  voltage_v?: number;
  current_a?: number;
  power_w?: number;
  energy_kwh?: number;
  power_estimated?: boolean;
  frequency_hz?: number;
  power_factor?: number;
  state?: "closed" | "open" | "unknown";
  alarm?: boolean;
  alarm_code?: string;
};

export type ElectricalSwitch = {
  id: string;
  kind: "transfer";
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
  kind: "electrical";
  node_id: string;
  timestamp_ms: number;
  switching_enabled?: boolean;
  channels: ElectricalChannel[];
  switches?: ElectricalSwitch[];
};

export type ElectricalCommand = {
  kind: "electrical_command";
  node_id: string;
  timestamp_ms: number;
  command_id: string;
  switch: string;
  action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
  token?: string;
};

export type ElectricalResult = {
  kind: "electrical_result";
  node_id: string;
  timestamp_ms: number;
  command_id: string;
  switch: string;
  action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
  accepted: boolean;
  refusal: "none" | "disabled" | "fault" | "not_armed" | "not_confirmed_open" | "unknown_switch" | "bad_token" | "not_supported";
  token?: string;
};

export type AlarmZone = {
  id: string;
  name?: string;
  kind: "instant" | "entry" | "interior" | "always";
  state: "normal" | "triggered" | "tamper" | "trouble";
  bypassed: boolean;
};

export type AlarmEvent = {
  ago_s: number;
  kind: "armed" | "exit_delay_started" | "entry_delay_started" | "alarm" | "siren_timed_out" | "disarmed" | "bad_pin" | "locked_out" | "zone_bypassed" | "siren_silenced";
  zone?: string;
};

export type Alarm = {
  kind: "alarm";
  node_id: string;
  timestamp_ms: number;
  phase: "disarmed" | "exit_delay" | "armed" | "entry_delay" | "alarm";
  mode: "disarmed" | "away" | "stay";
  siren: boolean;
  locked_out: boolean;
  commands_enabled: boolean;
  zones: AlarmZone[];
  open_zones: string[];
  events: AlarmEvent[];
  arm_profiles?: boolean;
  profile?: string;
};

export type ArmProfileZone = {
  id: string;
  armed?: boolean;
  delay?: "instant" | "entry";
};

export type ArmProfile = {
  id: string;
  name: string;
  base: "away" | "stay";
  exit_delay_s?: number;
  entry_delay_s?: number;
  siren?: boolean;
  notify?: "urgent" | "normal";
  zones?: ArmProfileZone[];
};

export type AlarmCommand = {
  kind: "alarm_command";
  node_id: string;
  timestamp_ms: number;
  command_id: string;
  action: "arm" | "disarm" | "silence";
  mode?: "away" | "stay";
  force?: boolean;
  profile?: ArmProfile;
};

export type AlarmResult = {
  kind: "alarm_result";
  node_id: string;
  timestamp_ms: number;
  command_id: string;
  action: "arm" | "disarm" | "silence";
  accepted: boolean;
  refusal: "none" | "not_disarmed" | "zones_open" | "not_armed" | "bad_pin" | "locked_out";
  phase: "disarmed" | "exit_delay" | "armed" | "entry_delay" | "alarm";
};

export type NodeHealth = {
  kind: "node_health";
  node_id: string;
  timestamp_ms: number;
  family: "radar" | "solar" | "electrical" | "alarm" | "hmi";
  firmware: string;
  board?: string;
  uptime_s: number;
  reset_reason: "power_on" | "external" | "software" | "panic" | "int_wdt" | "task_wdt" | "other_wdt" | "deep_sleep" | "brownout" | "sdio" | "usb" | "jtag" | "efuse" | "power_glitch" | "cpu_lockup" | "unknown";
  heap_free: number;
  heap_min: number;
  link: "wifi" | "ethernet" | "none";
  link_up: boolean;
  rssi_dbm?: number;
  broker_reconnects: number;
  low_stack_tasks?: number;
  last_error?: string;
};

export type ConnectionEvent = {
  id: number;
  at: string;
  type: "connection";
  action: "first_seen" | "login" | "login_failed" | "second_factor_failed" | "logout" | "session_ended" | "session_expired" | "panel_opened";
  client_kind: "studio" | "android" | "node" | "voice" | "other";
  client_id: string;
  user?: string;
  origin?: "local" | "remote";
  two_factor?: boolean;
  app_version?: string;
  subject?: string;
  ip?: string;
  agent?: string;
};

export type SystemEvent = {
  id: number;
  at: string;
  type: "system";
  category: "node" | "broker" | "settings" | "service" | "update" | "alarm" | "backup";
  action: "appeared" | "returned" | "disappeared" | "firmware_changed" | "connected" | "disconnected" | "created" | "changed" | "removed" | "started" | "stopped" | "restarted" | "checked" | "installed" | "rolled_back" | "armed" | "disarmed" | "silenced" | "acknowledged" | "arm_requested" | "disarm_requested" | "silence_requested" | "backup_made" | "backup_restored";
  subject?: string;
  by?: string;
  version?: string;
  previous_version?: string;
  profile?: string;
  outcome?: "allowed" | "denied" | "failed";
};

export type ConnectionClient = {
  id: string;
  kind: "studio" | "android" | "node" | "voice" | "other";
  user?: string;
  label?: string;
  app_version?: string;
  origin?: "local" | "remote";
  two_factor?: boolean;
  first_seen: string;
  last_seen: string;
  last_failure?: string;
  active_sessions: number;
  logins_ok: number;
  logins_failed: number;
  ip?: string;
  agent?: string;
};

export type NetworkInterface = {
  name: string;
  ip: string;
  cidr: string;
  gateway?: string;
  rx_bps?: number;
  tx_bps?: number;
};

export type NetworkProbe = {
  target: string;
  kind: "icmp" | "tcp" | "dns" | "http";
  ok: boolean;
  latency_ms?: number;
};

export type NetworkOutage = {
  started_ms: number;
  ended_ms: number;
  duration_s: number;
};

export type NetworkInternet = {
  state: "up" | "degraded" | "down" | "lan_down" | "unknown";
  since_ms?: number;
  gateway_ok?: boolean;
  latency_ms?: number;
  loss_percent?: number;
  probes?: NetworkProbe[];
  last_outage?: NetworkOutage;
  outages_24h?: number;
  downtime_24h_s?: number;
};

export type NetworkPort = {
  port: number;
  proto: "tcp" | "udp";
  service?: string;
  banner?: string;
};

export type NetworkDevice = {
  id: string;
  ip: string;
  mac?: string;
  randomized_mac?: boolean;
  vendor?: string;
  hostname?: string;
  kind?: "router" | "computer" | "phone" | "tv" | "printer" | "camera" | "iot" | "server" | "nas" | "network" | "unknown";
  os?: string;
  online: boolean;
  first_seen_ms: number;
  last_seen_ms: number;
  latency_ms?: number;
  ports?: NetworkPort[];
  services?: string[];
};

export type NetworkEvent = {
  id: string;
  kind: "new_device" | "device_online" | "device_offline" | "ip_changed" | "arp_conflict" | "port_opened" | "port_closed" | "internet_down" | "internet_up" | "gateway_down" | "gateway_up";
  at_ms: number;
  device_id?: string;
  port?: number;
  outage_s?: number;
  detail?: string;
};

export type NetworkScan = {
  last_ms: number;
  hosts: number;
  duration_ms?: number;
};

export type NetworkPublic = {
  ip: string;
  hostname?: string;
  city?: string;
  region?: string;
  country?: string;
  org?: string;
  timezone?: string;
  checked_ms: number;
  changed_ms?: number;
};

export type NetworkResults = {
  id: string;
  type: "scan_now" | "ping" | "traceroute" | "wake" | "ports" | "http" | "inspect";
  ok: boolean;
  finished_ms: number;
  device_id?: string;
  output?: string;
  ports?: NetworkPort[];
  latency_ms?: number;
};

export type Network = {
  kind: "network";
  node_id: string;
  timestamp_ms: number;
  interface: NetworkInterface;
  internet: NetworkInternet;
  devices: NetworkDevice[];
  events?: NetworkEvent[];
  scan?: NetworkScan;
  public?: NetworkPublic;
  results?: NetworkResults[];
};

export const MAX_TARGETS = 15;
export const MAX_LUX = 200000;
export const NODE_ID_PATTERN = /^[a-z0-9][a-z0-9_-]{0,63}$/;
export const COMMANDS = ["calibrate", "set_thresholds", "restart"] as const;
