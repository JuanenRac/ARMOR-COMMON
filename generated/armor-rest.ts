// Generated from openapi/armor-server.yaml by tools/generate_rest_types.py. Do not edit.
import type * as Contracts from "./armor-contracts";

export type Accepted = {
  accepted: true;
  /** Only for telemetry and health */
  revision?: number;
  /** Fields this server does not know yet, from a newer node */
  ignored?: string[];
  /** Only for the example reading of a solar device */
  example?: boolean;
};

export type AccountChange = {
  currentPassword: string;
  username?: string;
  newPassword?: string;
};

export type AccountUser = {
  id: string;
  username: string;
  role: "admin" | "operator" | "viewer" | "panel";
};

export type AdminAvailability = {
  available: boolean;
  reason?: string;
  hint?: string;
  console?: boolean;
};

export type AdminFile = {
  id: string;
  path: string;
  format: string;
  description: string;
  units: string[];
  /** Whether the file is there (a file that is not has no content yet) */
  exists: boolean;
  content: string;
  mtime: number;
  /** Only for an env file: its secrets are shown as stars */
  masked?: boolean;
};

export type AdminFileSaved = {
  ok: boolean;
  restarted: boolean;
};

export type AdminFiles = {
  /** The settings files the agent manages, without their content */
  files: {
    id: string;
    path: string;
    format: string;
    description: string;
    units: string[];
    exists: boolean;
    mtime: number;
  }[];
};

export type AdminServices = {
  services: {
    id: string;
    unit: string;
    description: string;
    installed: boolean;
    /** The state systemd reports (active, inactive, failed ...) */
    active: string;
    sub: string;
    enabled: string;
    pid: number;
    since: string;
    paused: boolean;
  }[];
};

/** What the maintenance agent answered, passed on as it is */
export type AgentReply = {
  [key: string]: unknown;
};

export type AiContext = {
  mode: "armed" | "disarmed";
  nodes: {
    id: string;
    online: boolean;
    targets: number;
    lux: number | null;
  }[];
  cameras: {
    id: string;
    name: string;
  }[];
};

export type AiObservationResult = {
  raised: boolean;
  alarm_id?: string;
  reason?: string;
};

export type Alarm = {
  id: string;
  key: string;
  source: AlarmSource;
  severity: "critical" | "high" | "warning";
  /** A stable code the client translates (intrusion, node_down, camera_down, smoke, water_leak, door_open, tamper, low_battery, device_offline ...) */
  code: string;
  raised_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  cleared_at?: string;
  /** Plain facts a person needs to act on it */
  detail?: {
    [key: string]: string | number | boolean;
  };
  /** A duress disarm; only an administrator sees it */
  silent?: true;
  acknowledged_unverified?: true;
};

/** The status of the commands sent to the alarm panels */
export type AlarmCommandStatus = {
  /** False unless the server runs with ARMOR_ALARM_COMMANDS=1 */
  enabled: boolean;
  /** The commands sent to a panel that has not answered yet */
  pending: {
    command_id: string;
    node_id: string;
    action: "arm" | "disarm" | "silence";
    mode?: "away" | "stay";
    profile?: string;
    actor: string;
    at: string;
  }[];
  /** What became of the latest commands, the newest first */
  recent: {
    command_id: string;
    node_id: string;
    action: "arm" | "disarm" | "silence";
    mode?: "away" | "stay";
    profile?: string;
    accepted: boolean;
    refusal: "none" | "not_disarmed" | "zones_open" | "not_armed" | "bad_pin" | "locked_out" | "timeout";
    phase?: "disarmed" | "exit_delay" | "armed" | "entry_delay" | "alarm";
    actor: string;
    at: string;
  }[];
};

/** The saved design of the alarm panels; revision 0 and a null document when none has been saved. */
export type AlarmDesign = {
  revision: number;
  updated_at?: string;
  updated_by?: string;
  alarm_design?: {
    [key: string]: unknown;
  } | null;
};

export type AlarmList = {
  active: Alarm[];
  recent: Alarm[];
};

export type AlarmNodes = {
  nodes: {
    node_id: string;
    state: Contracts.Alarm;
    received_at: string;
    stale: boolean;
  }[];
  totals: {
    nodes: number;
    stale: number;
    armed: number;
    sounding: number;
  };
};

export type AlarmSource = {
  type: "node" | "camera" | "device" | "solar" | "electrical" | "network" | "alarm";
  id: string;
};

/** The body of a refused request. Some routes answer a refusal with the bare status text instead (text/plain), which each such response also lists. */
export type ApiError = {
  /** What was wrong, in words */
  error: string;
  /** A stable code when the route has one (for example not_found) */
  code?: string;
  reason?: string;
};

/** The arming profiles and the number of them that may be kept */
export type ArmProfiles = {
  revision: number;
  updated_at: string;
  updated_by: string;
  profiles: Contracts.ArmProfile[];
  max: number;
};

/** One thing that changed. The fields besides id, at and type depend on the type (alert, node, camera, mode, device or alarm); the ones every client reads are named here. */
export type ArmorEvent = {
  id: number;
  at: string;
  type: "alert" | "node" | "camera" | "mode" | "device" | "alarm" | "connection" | "system";
  /** What it is about: a node, a camera, a device or an alarm source */
  subject?: string;
  /** What it was before */
  from?: string | number | boolean | null;
  /** What it is now */
  to?: string | number | boolean | null;
  mode?: "armed" | "disarmed";
  targets?: number;
  /** The code of an alarm, as in the table of alarm codes */
  code?: string;
  severity?: "critical" | "high" | "warning";
  source_type?: string;
  field?: string;
  [key: string]: unknown;
};

export type AuditEntries = {
  entries: {
    at: string;
    action: string;
    outcome: "allowed" | "denied" | "failed";
    actor?: string;
    target?: string;
    detail?: string;
  }[];
};

export type Automation = {
  id: string;
  name: string;
  enabled: boolean;
  when_mode: "any" | "armed" | "disarmed";
  trigger: AutomationTrigger;
  actions: AutomationAction[];
  created_at: string;
  /** When it last ran; null when it never did */
  last_run: string | null;
  runs: number;
};

/** What an automation does */
export type AutomationAction = {
  type: "device";
  device_id: string;
  command: "on" | "off" | "toggle";
  /** Switch back after this many seconds */
  for_s?: number;
} | {
  type: "notify";
};

export type AutomationInput = {
  name?: string;
  enabled?: boolean;
  when_mode?: "any" | "armed" | "disarmed";
  trigger?: AutomationTrigger;
  actions?: AutomationAction[];
};

export type AutomationList = {
  automations: Automation[];
};

/** What starts an automation */
export type AutomationTrigger = {
  type: "device";
  device_id: string;
  field: string;
  /** The value to wait for; with op gt or lt, the limit */
  equals: boolean | number;
  /** Numbers only: eq waits for the value, gt for it to go above, lt for it to go below */
  op?: "eq" | "gt" | "lt";
} | {
  type: "alarm";
  severity?: "critical" | "high" | "warning";
  source_type?: "node" | "camera" | "device" | "solar" | "electrical" | "network" | "alarm";
  source_id?: string;
} | {
  type: "mode";
  mode: "armed" | "disarmed";
};

export type BatteryArmRequest = {
  node: string;
  port: number;
  /** One of the operations of the catalog */
  op: string;
  /** The values of the operation (see the catalog); for firmware_update, { image_id } from POST /images */
  params?: {
    [key: string]: unknown;
  };
  /** The serial number of the battery, typed by the person (NOSERIAL for a battery that has none) */
  serial: string;
};

export type BatteryExecuteRequest = {
  /** The serial number again; it must be the one typed to arm */
  serial: string;
};

export type BatteryImage = {
  image_id: string;
  size: number;
  crc32: number;
  sha256: string;
  /** The name of the board the image is for, read at offset 0x418 */
  board: string;
  /** Major.minor read at offset 0x400 */
  version: string;
};

export type BatteryOperation = {
  id: string;
  node: string;
  port: number;
  op: string;
  params: {
    [key: string]: unknown;
  };
  actor: string;
  created_at: string;
  updated_at: string;
  stage: "arming" | "armed" | "starting" | "running" | "done" | "rejected" | "expired" | "lost" | "withdrawn";
  summary?: string;
  risk?: "low" | "medium" | "high" | "irreversible";
  atomic?: boolean;
  canonical?: string;
  /** Who the battery says it is */
  battery?: {
    model: string;
    serial: string;
    soft_version: string;
    board: string;
    capacity_ah?: number;
  };
  refusal?: string;
  snapshot_before?: string;
  outcome?: "running" | "ok" | "failed" | "partial" | "retry" | "rejected";
  code?: string;
  steps_done?: number;
  steps_total?: number;
  packets_sent?: number;
  packets_total?: number;
  before?: string;
  after?: string;
  diff?: {
    label: string;
    before: string;
    after: string;
  }[];
  transcript?: string;
  /** When an armed operation stops being executable */
  armed_until?: string;
  /** The operation that puts back what this one changed, when there is one */
  restore?: {
    op: string;
    params: {
      [key: string]: unknown;
    };
  } | null;
  /** How much of a firmware image the node has kept */
  staging?: {
    sent: number;
    total: number;
  };
  writes_started?: boolean;
  image?: {
    id: string;
    board: string;
    version: string;
    sha256: string;
    size: number;
  };
  cancel_requested?: boolean;
};

export type BatteryOperationList = {
  enabled: boolean;
  operations: BatteryOperation[];
};

export type BatteryOpsCatalog = {
  /** False unless the server runs with ARMOR_BATTERY_WRITE=1 */
  enabled: boolean;
  /** The table of ARMOR-COMMON battery_ops.json: ops (id, risk, needs_idle, alarm_ok, atomic, group, params), models, limit_groups, protections, expert_blocked, limits, refusals */
  catalog: {
    [key: string]: unknown;
  };
};

/** A camera as an operator sees it (the password is never shown) */
export type Camera = {
  id: string;
  name: string;
  host: string;
  snapshotUrl: string;
  rtspPath: string;
  previewPath?: string;
  onvifPort: number;
  rtspPort: number;
  username: string;
  hasCredentials: boolean;
  liveVideoAvailable: boolean;
};

export type CameraDiscovery = {
  cameras: {
    host: string;
    /** The camera ports that answered (80, 554, 8000, 8080, 8899) */
    ports: number[];
  }[];
  /** The networks that were scanned, as 192.168.0.0/24 */
  scanned: string[];
};

export type CameraInput = {
  id: string;
  name: string;
  host: string;
  username?: string;
  /** Write-only; an empty value keeps the stored one */
  password?: string;
  rtspPath?: string;
  snapshotUrl?: string;
  onvifPort?: number;
  rtspPort?: number;
};

export type CameraList = {
  cameras: Camera[];
};

export type CameraStatusList = {
  cameras: {
    id: string;
    status: "unknown" | "online" | "offline";
    since_ms: number | null;
    last_checked_ms: number | null;
    consecutive_failures: number;
  }[];
};

/** A camera as any local viewer sees it (no username, no credentials) */
export type CameraView = {
  id: string;
  name: string;
  host: string;
  snapshotUrl: string;
  rtspPath: string;
  previewPath?: string;
  onvifPort: number;
  rtspPort: number;
  hasCredentials: boolean;
  liveVideoAvailable: boolean;
};

export type CameraViewList = {
  cameras: CameraView[];
};

export type CaptureSettings = {
  enabled: boolean;
  photo: boolean;
  photo_count: number;
  photo_interval_s: number;
  video: boolean;
  video_seconds: number;
  cooldown_s: number;
};

export type CaptureSettingsSaved = {
  settings: CaptureSettings;
};

export type CaptureSettingsState = {
  settings: CaptureSettings;
  /** The latest automatic captures */
  recent: {
    camera_id: string;
    at: string;
    photos: number;
    video: boolean;
  }[];
};

export type CommandAccepted = {
  accepted: true;
  command_id: string;
};

export type ConnectionClient = Contracts.ConnectionClient;

export type ConnectionEvent = Contracts.ConnectionEvent;

export type ConnectionList = {
  clients: ConnectionClient[];
};

export type ConnectionState = {
  active: {
    host: string;
    port: number;
    tls: boolean;
    studio_origins: string[];
  };
  /** Whether the server's link to the MQTT broker is encrypted and, when the installation's own authority is pinned, which one (never a path or a key) */
  mqtt_tls?: {
    configured: boolean;
    tls: boolean;
    pinned_ca: boolean;
    ca?: {
      fingerprint256: string;
      subject: string;
      valid_to: string;
    };
  };
  /** What the settings file holds */
  saved: {
    host?: string;
    port?: number;
    studio_port?: number;
  };
  restart_required: boolean;
};

export type ConsoleState = {
  available: boolean;
  enabled: boolean;
  /** Epoch milliseconds, 0 when locked */
  unlocked_until: number;
};

export type ConsoleUnlocked = {
  unlocked_until: number;
};

/** How many things a bulk call touched (the name of the field says which) */
export type Count = {
  acknowledged?: number;
  deleted?: number;
  removed?: number;
};

export type DeleteMediaRequest = {
  kind: "snapshot" | "recording" | "all";
};

export type DeletePushRegisterRequest = {
  token?: string;
};

export type DeleteStudioTotpRequest = {
  password: string;
};

export type DesignSaved = {
  revision: number;
  updated_at: string;
  updated_by: string;
};

export type DesignVersions = {
  versions: {
    id: string;
    revision: number;
    saved_at: string;
    updated_by: string;
    /** How many of each kind of element that version held */
    counts?: {
      [key: string]: number;
    };
  }[];
};

export type Device = {
  id: string;
  name: string;
  kind: "smoke" | "co" | "gas" | "water_leak" | "panic_button" | "door" | "window" | "motion" | "glass_break" | "vibration" | "climate" | "temperature" | "humidity" | "light_level" | "smart_plug" | "smart_light" | "smart_switch" | "siren" | "lock" | "valve";
  protocol: "wifi" | "bluetooth" | "zigbee" | "zwave" | "thread" | "lora" | "rf433" | "wired" | "other";
  location: string;
  source?: DeviceSource;
  commands?: DeviceCommands;
  expected_interval_s: number;
  risk?: string;
  state: DeviceState;
  online: boolean;
  last_seen: string | null;
  created_at: string;
};

export type DeviceCommandResult = {
  ok: true;
  via: string;
  command: string;
  device: Device;
};

/** How the server switches the device: by MQTT and/or by an address on the local network */
export type DeviceCommands = {
  mqtt?: {
    topic: string;
    on?: string;
    off?: string;
    toggle?: string;
    /** Set the state as soon as the command is sent, for devices that never report back */
    assume_state?: boolean;
  };
  /** URLs on the local network only */
  http?: {
    on?: string;
    off?: string;
    toggle?: string;
  };
};

export type DeviceInput = {
  id?: string;
  name?: string;
  kind?: "smoke" | "co" | "gas" | "water_leak" | "panic_button" | "door" | "window" | "motion" | "glass_break" | "vibration" | "climate" | "temperature" | "humidity" | "light_level" | "smart_plug" | "smart_light" | "smart_switch" | "siren" | "lock" | "valve";
  protocol?: "wifi" | "bluetooth" | "zigbee" | "zwave" | "thread" | "lora" | "rf433" | "wired" | "other";
  location?: string;
  source?: DeviceSource;
  commands?: DeviceCommands;
  /** Seconds of silence after which the device is offline; 0 never */
  expected_interval_s?: number;
};

export type DeviceList = {
  devices: Device[];
  kinds: string[];
  protocols: string[];
};

/** Where the state of a device comes from: push (it reports with the ingest token) or mqtt (a state topic, an optional availability topic and a map from its payload to canonical fields) */
export type DeviceSource = {
  type: "push";
} | {
  type: "mqtt";
  topic: string;
  /** A topic that says online or offline (Zigbee2MQTT, Tasmota, ESPHome) */
  availability_topic?: string;
  map?: {
    field: string;
    /** A dotted path in the payload; $ is the whole payload */
    path: string;
    invert?: boolean;
  }[];
};

/** Canonical fields only; anything else is dropped. Booleans: triggered, open, on, locked, tamper. Numbers: temperature, humidity, battery, brightness, power_w, energy_kwh, lux, rssi, co_ppm. */
export type DeviceState = {
  triggered?: boolean;
  open?: boolean;
  on?: boolean;
  locked?: boolean;
  tamper?: boolean;
  temperature?: number;
  humidity?: number;
  battery?: number;
  brightness?: number;
  power_w?: number;
  energy_kwh?: number;
  lux?: number;
  rssi?: number;
  co_ppm?: number;
};

export type DiagnosticLogAnswer = {
  node_id: string;
  at: string;
  log: string;
  truncated: boolean;
};

export type DiagnosticNodes = {
  scope: "read_only";
  nodes: {
    node_id: string;
    family?: "radar" | "solar" | "electrical" | "alarm" | "hmi";
    firmware?: string;
    status: "ok" | "warning" | "stale" | "unknown";
    /** When the node last delivered a package */
    package_at?: string;
    /** When the node last delivered a log */
    log_at?: string;
  }[];
};

export type DiagnosticPackageAnswer = {
  node_id: string;
  /** When the node delivered it */
  at: string;
  package: Contracts.NodeControlResultDiagnosticsPackage;
};

export type DiagnosticTokenList = {
  tokens: Contracts.DiagnosticTokenInfo[];
};

/** The saved electrical scheme; revision 0 and a null document when none has been saved. */
export type ElectricalDesign = {
  revision: number;
  updated_at?: string;
  updated_by?: string;
  electrical?: {
    [key: string]: unknown;
  } | null;
};

export type ElectricalDevices = {
  elements: {
    id: string;
    name: string;
    kind: string;
    protocol: string;
    location: string;
    online: boolean;
    last_seen: string | null;
    risk: string;
    on?: boolean;
    power_w?: number;
    voltage_v?: number;
    current_a?: number;
    energy_kwh?: number;
    switchable: boolean;
  }[];
  totals: {
    elements: number;
    online: number;
    on: number;
    power_w: number;
    energy_kwh: number;
  };
};

export type ElectricalEnergy = {
  channels: {
    node: string;
    channel: string;
    days: {
      day: string;
      kwh: number;
      resets: number;
    }[];
  }[];
};

export type ElectricalHistory = {
  node_id: string;
  channel: string;
  minutes: number;
  samples: {
    /** Milliseconds since 1970 */
    t: number;
    voltage_v?: number;
    current_a?: number;
    power_w?: number;
    energy_kwh?: number;
  }[];
};

export type ElectricalReadings = {
  nodes: {
    node_id: string;
    reading: Contracts.Electrical;
    received_at: string;
    stale: boolean;
  }[];
  totals: {
    nodes: number;
    channels: number;
    stale: number;
    grid_w: number | null;
    grid_estimated: boolean;
    grid_kwh: number | null;
    alarms: number;
  };
};

/** The status of the switching commands (what is armed, what was sent and what the node answered) */
export type ElectricalSwitching = {
  /** False unless the server runs with ARMOR_ELECTRICAL_SWITCHING=1 */
  enabled: boolean;
  /** The commands sent to a node that has not answered yet */
  pending: {
    command_id: string;
    node_id: string;
    switch: string;
    action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
    actor: string;
    at: string;
  }[];
  /** What became of the latest commands, the newest first */
  recent: {
    command_id: string;
    node_id: string;
    switch: string;
    action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
    accepted: boolean;
    refusal: "none" | "disabled" | "fault" | "not_armed" | "not_confirmed_open" | "unknown_switch" | "bad_token" | "not_supported" | "timeout";
    actor: string;
    at: string;
  }[];
};

export type Elevated = {
  elevated_for_s: number;
};

export type EnergyAlarmSettings = {
  /** A battery under this charge (percent) raises low */
  soc_low: number;
  /** The charge at which the low alarm ends; higher than soc_low */
  soc_ok: number;
  /** The gap between the highest and the lowest cell (millivolts) above which the cells are unbalanced */
  cell_spread_mv: number;
  /** Minutes the gap must last before it raises the alarm (0 - at once) */
  cell_spread_minutes: number;
  battery_temp_high_c: number;
  battery_temp_low_c: number;
  heatsink_high_c: number;
  health_low_percent: number;
};

/** A signed statement of what a file was, with the chain of what was done to it */
export type EvidenceProof = {
  version: 1;
  issued_at: string;
  issuer: "armor-server";
  file: {
    camera: string;
    kind: string;
    name: string;
    bytes: number;
    created_at: string;
    sha256: string;
    protected: boolean;
  };
  /** Every line of the audit trail that touched the file */
  custody: {
    at: string;
    action: string;
    outcome: string;
    actor?: string;
    target?: string;
  }[];
  /** Whether the audit trail reaches back to the moment the file was made; absent in the proofs issued before this was recorded */
  custody_complete?: boolean;
  /** The time of the oldest line of the audit trail that is still kept */
  audit_from?: string | null;
  signature: {
    algorithm: "HMAC-SHA256";
    value: string;
  };
};

export type EvidenceVerdict = {
  /** The signature is ours */
  genuine: boolean;
  /** The file in the library still has the digest the proof states */
  matches: boolean;
  issued_at?: string;
};

export type FirmwareProbe = {
  nodes: {
    address: string;
    reachable: boolean;
    node_id?: string;
    version?: string;
    board?: string;
    /** radar, solar, electrical or hmi, from the firmware that says it */
    kind?: string;
  }[];
};

export type FirmwareRelease = {
  kind: "radar" | "solar" | "electrical" | "hmi" | "alarm";
  repo: string;
  version: string;
  bytes: number;
  /** Whether the release carries the checksum of its image */
  checksum: boolean;
};

export type FirmwareUpload = {
  id: string;
  name: string;
  bytes: number;
  sha256: string;
};

export type HealthzStatus = {
  ok: true;
  service: "armor-server";
};

export type HistoryPage = {
  events: (ConnectionEvent | SystemEvent | ArmorEvent)[];
  next_before: number | null;
  next_after?: number | null;
};

/** How many events were removed and how many remain */
export type HistoryRemoved = {
  deleted: number;
  remaining: number;
};

export type HistorySummary = {
  total: number;
  oldest_at: string | null;
  newest_at: string | null;
  /** Events per type */
  by_type: {
    alert: number;
    node: number;
    camera: number;
    mode: number;
    device: number;
    alarm: number;
    connection: number;
    system: number;
  };
  last_24h: {
    events: number;
    high_alerts: number;
    node_incidents: number;
    camera_incidents: number;
  };
};

/** A rectangle as fractions of the picture, from the top left */
export type IgnoreZone = {
  x: number;
  y: number;
  w: number;
  h: number;
};

export type IgnoreZones = {
  camera_id: string;
  zones: IgnoreZone[];
};

export type IgnoreZonesInput = {
  zones: IgnoreZone[];
};

export type IngestLog = {
  topics: {
    topic: string;
    accepted: number;
    rejected: number;
    ignored_fields?: number;
    last_ok_at?: string | null;
    last_error?: string | null;
    last_error_at?: string | null;
    last_payload?: string | null;
  }[];
};

export type InstallationBundle = {
  format: "armor-installation";
  version: number;
  exported_at: string;
  exported_by: string;
  parts: {
    [key: string]: unknown;
  };
};

/** What importing an installation file did, by part (cameras, site, rules, automations, devices, solar_devices, energy_alarms, users...) */
export type InstallationReport = {
  /** For each part that was applied: what happened to it, in words */
  applied: {
    [key: string]: string;
  };
  /** For each part that was left out: why */
  skipped: {
    [key: string]: string;
  };
  /** For each part that did not check out: the reason (nothing of it was applied) */
  failed: {
    [key: string]: string;
  };
  cameras_need_credentials: string[];
};

/** A background job and how far it got */
export type Job = {
  id: string;
  state?: string;
  [key: string]: unknown;
};

export type JobStarted = {
  id: string;
};

export type MediaDigest = {
  sha256: string;
};

export type MediaItem = {
  id: string;
  cameraId: string;
  kind: "snapshot" | "recording";
  file: string;
  createdAt: string;
  bytes: number;
  protected: boolean;
};

export type MediaItemResult = {
  item: MediaItem;
};

export type MediaList = {
  items: MediaItem[];
  activeCameraIds: string[];
};

export type MqttAccountCreated = {
  ok: boolean;
  user: string;
  /** Shown once */
  password: string;
};

export type MqttAccounts = {
  accounts: {
    user: string;
    /** The kind of identity (field-node, solar-node, electrical-node, network-node, alarm-node, alarm, device, bridge) or other */
    role: string;
    name: string;
    /** Whether Studio may remove it */
    manageable: boolean;
    /** What it may read and write, as the access list words it */
    topics: string[];
  }[];
};

export type NetworkAccepted = {
  accepted: true;
  /** The orders waiting for the node that reported */
  commands: unknown;
};

/** An order for a network node and how far it got */
export type NetworkCommand = {
  id: string;
  status?: "queued" | "sent" | "done" | "expired";
  type?: "scan_now" | "ping" | "traceroute" | "wake" | "ports" | "http" | "inspect";
  node_id?: string;
  by?: string;
  created_at?: string;
  sent_at?: string;
  /** What the node did with it (ok, finished_ms, output, ports, latency_ms) */
  result?: {
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type NetworkCommandList = {
  commands: NetworkCommand[];
};

/** The saved network map; revision 0 and a null document when none has been saved. */
export type NetworkDesign = {
  revision: number;
  updated_at?: string;
  updated_by?: string;
  network?: {
    [key: string]: unknown;
  } | null;
};

export type NetworkDeviceLogin = {
  id: string;
  login: {
    /** Who the stored login is for, never the password */
    user: string;
  };
};

export type NetworkDeviceNote = {
  id: string;
  note: string;
};

export type NetworkHistory = {
  node_id: string;
  minutes: number;
  samples: {
    t: number;
    state: string;
    latency_ms?: number;
    loss_percent?: number;
    rx_bps?: number;
    tx_bps?: number;
  }[];
};

export type NetworkOverview = {
  nodes: {
    node_id: string;
    received_at: string;
    stale: boolean;
    /** The version of the network contract the node says it speaks (1 when it says nothing) */
    contract: number;
    /** Whether that version is older than the one the server speaks */
    outdated: boolean;
    /** The interface the node watches, as the network message has it */
    interface: Contracts.NetworkInterface;
    /** The state of the internet, as the network message has it */
    internet: Contracts.NetworkInternet;
    /** The last sweep */
    scan?: Contracts.NetworkScan;
    /** What the internet sees of the connection */
    public?: Contracts.NetworkPublic;
    devices: (Contracts.NetworkDevice & {
      note?: {
        name?: string;
        notes?: string;
        trusted?: boolean;
        kind?: "router" | "computer" | "phone" | "tv" | "printer" | "camera" | "iot" | "server" | "nas" | "network" | "unknown";
        /** Left out of the list */
        hidden?: boolean;
        /** Tell me the next time it comes onto the network */
        watch?: boolean;
        updated_at: string;
      };
      /** The user of the login kept for its web administration (never the password) */
      login?: {
        user: string;
      };
    })[];
    /** How many devices an operator hid */
    hidden: number;
  }[];
  totals: {
    nodes: number;
    stale: number;
    devices: number;
    online: number;
    unknown: number;
    internet: "up" | "degraded" | "down" | "lan_down" | "unknown" | null | null;
  };
  events: {
    id: string;
    kind: "new_device" | "device_online" | "device_offline" | "ip_changed" | "arp_conflict" | "port_opened" | "port_closed" | "internet_down" | "internet_up" | "gateway_down" | "gateway_up";
    at_ms: number;
    node_id: string;
    device_id?: string;
    port?: number;
    outage_s?: number;
    detail?: string;
  }[];
  outages: {
    node_id: string;
    kind: "internet" | "gateway";
    started_ms: number;
    ended_ms: number;
    duration_s: number;
  }[];
};

export type NewUser = {
  username: string;
  /** 12 characters or more when the server is reachable from the network */
  password: string;
  /** An administrator also manages users */
  role?: "admin" | "operator";
};

export type NodeControlAllRequest = {
  operation: "restart" | "pause" | "resume" | "standby" | "identify" | "diagnostics" | "maintenance_on" | "maintenance_off";
  /** rolling is only for a restart: one after another, thirty seconds apart, the alarm panel last */
  mode: "now" | "rolling";
  /** The word of the operation, typed by the person; required for restart, pause and standby */
  confirm?: "RESTART" | "PAUSE" | "STANDBY";
  /** As for one node */
  duration_s?: number;
};

export type NodeControlLine = {
  node_id: string;
  family: "radar" | "solar" | "electrical" | "alarm" | "hmi";
  /** pending: waiting for the node to arm; armed: it gave its token; sent: the order was sent; acknowledged: it said it is restarting; applied: it did what was asked (see state); offline: it stopped reporting; back: it reports again; refused, no_answer and not_back: it did not */
  stage: "pending" | "armed" | "sent" | "acknowledged" | "applied" | "offline" | "back" | "refused" | "no_answer" | "not_back";
  /** After an applied order: the state of the node */
  state?: "running" | "paused" | "standby";
  maintenance?: boolean;
  /** The reason the node gave when it refused (busy_update, busy_upload, busy_slot_copy, busy_battery, rate_limited, already_in_state ...) */
  refusal?: string;
  /** Its place in a rolling restart */
  slot?: number;
  /** What the node said: seconds until it goes */
  restart_in_s?: number;
  /** Seconds left of the pause, identify or maintenance window */
  until_s?: number;
  firmware_before?: string;
  firmware_after?: string;
  acknowledged_at?: string;
  applied_at?: string;
  offline_at?: string;
  back_at?: string;
  /** Seconds from the order to the first report after the restart */
  back_after_s?: number;
  /** After a diagnostics order, the snapshot the node gave */
  diagnostics?: {
    firmware: string;
    uptime_s: number;
    reset_reason: string;
    heap_free: number;
    heap_min: number;
    psram_free?: number;
    stack_min_free?: number;
    rssi?: number;
    mqtt_connected: boolean;
    state: "running" | "paused" | "standby";
    maintenance: boolean;
  };
};

export type NodeControlList = {
  operations: NodeControlOperation[];
};

export type NodeControlOperation = {
  id: string;
  scope: "node" | "all";
  operation: "restart" | "pause" | "resume" | "standby" | "identify" | "diagnostics" | "maintenance_on" | "maintenance_off";
  mode: "now" | "rolling";
  duration_s?: number;
  actor: string;
  /** Where the order came from (local, vpn or remote), as the server saw it */
  origin?: string;
  created_at: string;
  updated_at: string;
  /** done: every node has answered or has failed to */
  state: "arming" | "running" | "done";
  nodes: NodeControlLine[];
};

export type NodeControlRequest = {
  operation: "restart" | "pause" | "resume" | "standby" | "identify" | "diagnostics" | "maintenance_on" | "maintenance_off";
  /** The name of the node, typed again by the person; required for restart, pause and standby */
  confirm?: string;
  /** Only for pause (60..3600, default 3600), identify (5..300, default 30) and maintenance_on (60..28800, default 3600) */
  duration_s?: number;
  /** Only for diagnostics, one node at a time: ask for the diagnostic package (memory, tasks, why the node last started, versions, the allowed part of its settings, the core dump summary, the newest log - never a secret) or for the log alone; the node delivers one at most every fifteen seconds and the server keeps the latest of each (GET /api/v1/nodes/{id}/diagnostics) */
  detail?: "package" | "log";
};

export type NodeDiagnostics = {
  node_id: string;
  package?: StoredDiagnostic;
  log?: StoredDiagnostic;
};

/** One node with the history of its memory and signal (up to 120 reports) and the log of its restarts, newest first */
export type NodeHealthDetail = NodeHealthEntry & {
  samples: {
    at: number;
    heap_free: number;
    heap_min: number;
    heap_internal_free?: number;
    heap_internal_largest?: number;
    rssi_dbm?: number;
    link_up: boolean;
    uptime_s: number;
    broker_reconnects: number;
  }[];
  restarts: NodeHealthRestart[];
};

/** The latest health report of one node, with what the server makes of it */
export type NodeHealthEntry = {
  node_id: string;
  family: "radar" | "solar" | "electrical" | "alarm" | "hmi";
  firmware: string;
  board?: string;
  report: Contracts.NodeHealth;
  received_at: string;
  /** No report for a few minutes - what is shown is the last one */
  stale: boolean;
  status: "ok" | "warning" | "stale";
  warnings: {
    code: "node_low_memory" | "node_frequent_resets" | "node_link_flapping" | "node_weak_signal" | "node_sensor_bluetooth_open" | "node_radar_masked" | "node_wifi_jam";
    detail: {
      [key: string]: string | number | boolean;
    };
  }[];
  restarts_24h: number;
  last_restart?: NodeHealthRestart;
  /** What remote control has done to the node, and its planned-maintenance window; absent while nothing is known */
  control?: {
    state: "running" | "paused" | "standby";
    maintenance: boolean;
    since_ms?: number;
    by?: string;
    until_s?: number;
    maintenance_until_s?: number;
    window?: {
      source: "node" | "operator" | "both";
      reason: "restart" | "pause" | "standby" | "update" | "upload" | "operator";
      remaining_s: number;
      requested_by?: string;
    };
    /** Who knows: the node's own report, or what the server remembers of the orders it gave */
    source: "node" | "server";
  };
};

export type NodeHealthList = {
  nodes: NodeHealthEntry[];
  /** Nodes the server knows that have not reported their health yet */
  waiting: {
    node_id: string;
    family: "radar" | "solar" | "electrical" | "alarm" | "hmi";
  }[];
  totals: {
    nodes: number;
    stale: number;
    with_warnings: number;
  };
  /** The levels the server judges by, so a console can say what low means */
  levels: {
    low_heap_b: number;
    low_heap_clear_b: number;
    low_internal_b?: number;
    low_internal_clear_b?: number;
    low_block_b?: number;
    restarts_per_day: number;
    abnormal_window_min: number;
    flap_reconnects: number;
    flap_window_min: number;
    weak_signal_dbm: number;
    weak_signal_reports: number;
    silent_after_s: number;
  };
};

export type NodeHealthRestart = {
  at: string;
  reason: string;
  /** A restart nobody asked for */
  abnormal: boolean;
  uptime_before_s?: number;
  boot?: Contracts.NodeHealthBoot;
};

export type NodeMaintenanceList = {
  windows: NodeMaintenanceWindow[];
};

/** A planned-maintenance window the server holds for a node (the retained `node_maintenance` message of the shared contract, or the operator window of maintenance_on). While it is active the node-offline alert and the tamper inference are held back, but a window the node announced is bounded by the server (10 minutes unless set) and ends as `maintenance_expired` in the history if the node does not return. */
export type NodeMaintenanceWindow = {
  node_id: string;
  source: "node" | "operator" | "both";
  reason: "restart" | "pause" | "standby" | "update" | "upload" | "operator";
  active: boolean;
  /** Seconds left before the window ends or is cut by the server bound */
  expires_in_s?: number;
  requested_by?: string;
};

export type NodePanel = {
  id: string;
  address: string;
  scheme: "http" | "https";
  port: number;
  fingerprint?: string;
  label?: string;
};

export type NodePanelFingerprint = {
  fingerprint: string;
  trusted: boolean;
  previous: string | null;
  changed: boolean;
};

export type NodePanelList = {
  panels: NodePanel[];
};

export type NodeProvisioned = {
  ok: boolean;
  /** False when the panel of the node could not be written to */
  written: boolean;
  why: string;
  /** What to type by hand when written is false */
  broker: {
    uri: string;
    username: string;
    password: string;
  };
};

export type NodeToken = {
  node_id: string;
  token: string;
  strict: boolean;
};

export type NotificationChannels = {
  /** Whether the signed webhook is set up */
  webhook: boolean;
  /** Whether the MQTT output is connected */
  mqtt: boolean;
  telegram: boolean;
  homeassistant: boolean;
  ntfy?: boolean;
  language: string;
  /** What each place the alarms went to has come to since the server started, by place (webhook, telegram, homeassistant, ntfy); a place that has been sent nothing is not listed. No message and no address is in it. */
  metrics?: {
    [key: string]: {
      /** Messages taken by the place */
      delivered: number;
      /** Messages that never arrived after the retries */
      failed: number;
      /** Messages thrown out of a full queue */
      dropped: number;
      /** Messages waiting now */
      queued: number;
      last_delivered_at?: string;
      last_failure_at?: string;
      /** Why the last one failed (an HTTP status or a kind of network error), at most 80 characters */
      last_failure?: string;
    };
  };
};

export type NotificationTest = {
  results: {
    channel: string;
    ok: boolean;
    detail?: string;
  }[];
};

export type Ok = {
  ok: boolean;
};

export type OperatorSessionOpened = {
  expiresAt: string;
};

export type PanelSummary = {
  mode: "armed" | "disarmed";
  revision: number;
  time_ms: number;
  nodes: {
    online: number;
    total: number;
  };
  /** The solar part of the summary, in the words of a small panel */
  energy: {
    /** Whether any inverter or battery has reported */
    reporting: boolean;
    pv_w: number;
    load_w: number;
    battery_w: number | null;
    soc_percent: number | null;
    mode: string | null;
    inverters: number;
    batteries: number;
    stale: number;
  };
  alarms: {
    active: number;
    unacknowledged: number;
    items: {
      id: string;
      code: string;
      severity: string;
      source_type: string;
      source_id: string;
      raised_at: string;
      acknowledged: boolean;
    }[];
  };
};

/** Text for a person to read, as the log of a node is */
export type PlainText = string;

export type PostAdminConsoleRunRequest = {
  command: string;
  cwd?: string;
  timeout_s?: number;
};

export type PostAdminConsoleUnlockRequest = {
  password: string;
};

export type PostAdminFirmwareJobsRequest = {
  kind: "radar" | "solar" | "electrical" | "alarm" | "hmi";
  source: "github" | "upload";
  upload_id?: string;
  targets: {
    address: string;
    node_id?: string;
  }[];
  panel_user: string;
  panel_password: string;
};

export type PostAdminFirmwareProbeRequest = {
  addresses: string[];
};

export type PostAdminInstallationRequest = {
  bundle: {
    [key: string]: unknown;
  };
  parts?: ("cameras" | "site" | "electrical" | "network" | "rules" | "automations" | "devices" | "solar_devices" | "energy_alarms" | "users")[];
};

export type PostAdminMqttAccountsRequest = {
  role: "node" | "solar-node" | "electrical-node" | "network-node" | "consumer" | "device" | "bridge";
  name: string;
};

export type PostAdminNodePanelsIdFingerprintRequest = {
  trust?: boolean;
};

export type PostAdminNodesProvisionRequest = {
  node_id: string;
  address: string;
  panel_user?: string;
  panel_password?: string;
  broker_host: string;
  broker_port?: number;
};

export type PostAdminNotificationsTestRequest = {
  channel?: "webhook" | "mqtt" | "telegram" | "homeassistant";
};

export type PostAdminRemoteDdnsSetupRequest = {
  provider: "duckdns" | "cloudflare" | "url";
  domain?: string;
  token?: string;
  zone?: string;
  record_name?: string;
  url?: string;
};

export type PostAdminRemoteWireguardPeersRequest = {
  name: string;
  full_tunnel?: boolean;
};

export type PostAdminRemoteWireguardSetupRequest = {
  endpoint: string;
  port?: number;
  lan?: string;
  subnet?: string;
  route_lan?: string;
};

export type PostAdminSystemUpgradeRequest = {
  mode?: "upgrade" | "full" | "repair";
};

export type PostAdminUpdatesRequest = {
  components?: string[];
  force?: boolean;
};

export type PostAiObservationsRequest = {
  camera_id: string;
  severity: "review" | "high";
  reasons: string[];
  profile: "daylight" | "low-light";
  motion: number;
  radar_tracks: number;
};

export type PostAlarmCommandRequest = {
  pin?: string;
  node: string;
  action: "arm" | "disarm" | "silence";
  mode?: "away" | "stay";
  force?: boolean;
  /** The id of an arming profile (GET /api/v1/alarm/profiles); only on an arm. Its base is the mode, which may then be left out. The server puts the whole profile inside the command to the node, and only a node whose state says arm_profiles: true is sent one. */
  profile?: string;
};

export type PostAlarmsAcknowledgeRequest = {
  /** Only for the account of a wall panel: its PIN, checked under the lockout of the disarm PIN. Without it the acknowledgement stays unverified and a critical alarm keeps being escalated */
  pin?: string;
};

export type PostCamerasIdStreamTicketRequest = {
  /** auto gives the lighter picture to a person who came from outside the house and the normal one otherwise */
  quality?: "auto" | "normal" | "low";
};

export type PostDevicesIdCommandRequest = {
  command: "on" | "off" | "toggle";
};

export type PostDevicesIdStateRequest = {
  state: DeviceState;
};

export type PostDevicesStateRequest = {
  device_id: string;
  state: DeviceState;
};

export type PostElectricalSwitchRequest = {
  node: string;
  switch: string;
  action: "arm" | "close_a" | "close_b" | "open" | "acknowledge";
};

export type PostModeRequest = {
  mode: "armed" | "disarmed";
  pin?: string;
};

export type PostPushRegisterRequest = {
  token: string;
};

export type PostPushUnregisterRequest = {
  token?: string;
};

export type PostSolarDevicesRequest = {
  kind: "inverter" | "battery";
  name: string;
  node_id: string;
  /** Taken from the name when omitted */
  device?: string;
  model?: string;
  connection?: "rs232" | "rs485" | "usb" | "can" | "wifi" | "other";
  notes?: string;
};

export type PostSolarRequest = Contracts.SolarInverter | Contracts.SolarBattery;

export type PostStudioElevateRequest = {
  password?: string;
  code?: string;
};

export type PostStudioSessionTotpRequest = {
  challenge: string;
  code: string;
};

export type PostStudioTotpEnableRequest = {
  code: string;
};

export type PostStudioTotpSetupRequest = {
  password: string;
};

export type PostVoiceCommandRequest = {
  text: string;
  language?: "en" | "es" | "de" | "fr" | "it" | "ja" | "zh" | "pt";
  confirmation?: string;
};

export type Preferences = {
  language?: string;
  theme?: string;
  /** The place the weather is shown for; null when none is chosen */
  weatherPlace?: {
    name: string;
    region: string;
    country: string;
    lat: number;
    lon: number;
  } | null;
};

export type Preflight = {
  ready: boolean;
  checked_at: string;
  blocking: number;
  warnings: number;
  issues: {
    kind: "node" | "panel" | "zone" | "camera" | "device" | "alarm";
    level: "block" | "warn";
    code: "node_offline" | "panel_silent" | "zone_open" | "camera_down" | "opening_open" | "device_offline" | "alarm_unseen";
    id: string;
    /** What the issue is about, such as the zone that is open */
    detail?: string;
  }[];
};

export type PreviewTicket = {
  path: string;
  expiresAt: string;
};

export type PtzCommand = {
  command: "left" | "right" | "up" | "down" | "zoomIn" | "zoomOut" | "stop";
};

export type PtzResult = {
  camera: Camera;
  command: string;
};

export type PublicUser = {
  id: string;
  username: string;
  role: "admin" | "operator" | "viewer" | "panel";
  createdAt: string;
  updatedAt: string;
  hasPin: boolean;
  hasDuress: boolean;
};

export type PushRegistered = {
  registered: boolean;
  devices: number;
};

export type PushStatus = {
  enabled: boolean;
  devices: number;
};

export type PutAccountPinRequest = {
  currentPassword: string;
  pin?: string;
  duress_pin?: string;
  clear?: boolean;
};

export type PutAdminFilesIdRequest = {
  content: string;
  restart?: boolean;
  expect_mtime?: number;
};

export type PutAdminNodePanelsIdRequest = {
  address: string;
  scheme: "http" | "https";
  port?: number;
  fingerprint?: string;
  label?: string;
};

export type PutAlarmDesignRequest = {
  revision: number;
  alarm_design: {
    [key: string]: unknown;
  };
};

export type PutAlarmProfilesRequest = {
  revision?: number;
  profiles: Contracts.ArmProfile[];
};

export type PutElectricalDesignRequest = {
  revision: number;
  electrical: {
    [key: string]: unknown;
  };
};

export type PutMediaCameraIdKindFileProtectedRequest = {
  protected: boolean;
};

export type PutNetworkDesignRequest = {
  revision: number;
  network: {
    [key: string]: unknown;
  };
};

export type PutNetworkDevicesIdLoginRequest = {
  user: string;
  password: string;
};

export type PutNetworkDevicesIdRequest = {
  name?: string;
  notes?: string;
  trusted?: boolean;
  kind?: string;
};

export type PutPreferencesRequest = {
  language?: string;
  theme?: string;
  weatherPlace?: {
    [key: string]: unknown;
  } | null;
};

export type PutSiteRequest = {
  revision: number;
  site: {
    [key: string]: unknown;
  };
};

export type PutSystemConnectionRequest = {
  host?: string;
  port?: number;
  studio_port?: number;
};

export type PutUsersIdPinRequest = {
  pin: string;
  duress_pin?: string;
};

export type RadarEventList = {
  events: (Contracts.RadarEvent & {
    received_at: string;
  })[];
  nodes: string[];
};

export type RecordingStarted = {
  cameraId: string;
  recording: true;
  startedAt: string;
};

export type RemoteCheck = {
  ip: string;
  /** Where this request comes from */
  origin: "local" | "remote";
  /** Where the session was opened; null without a session */
  session_origin: "local" | "remote" | null | null;
  protocol: string;
  forwarded_for: string | null;
  cookie_secure: boolean;
  trust_proxy: boolean | number | string;
  totp_policy: "off" | "remote" | "always";
  totp_enabled: boolean;
  remote_session_ttl_s: number;
  remote_idle_s: number;
  elevation_s: number;
};

export type RemoteState = {
  wireguard: {
    tool: boolean;
    script: boolean;
    configured: boolean;
    running: boolean;
    qr: boolean;
    peers: {
      [key: string]: unknown;
    }[];
    endpoint?: string;
    subnet?: string;
    port?: number;
    lan?: string;
    route_lan?: boolean;
  };
  ddns: {
    script: boolean;
    configured: boolean;
    provider?: string;
    name?: string;
    last_address?: string;
  };
};

export type RemoteTls = {
  /** Whether the root certificate of the installation's authority was found */
  present: boolean;
  /** SHA-256 of the public key of the authority (its SubjectPublicKeyInfo), in base64 */
  pin?: string;
  /** What to paste in the app or to put in a QR code: armor-pin:<host>:<pin>, or armor-pin:<pin> without a host */
  text?: string;
  subject?: string;
  /** When the authority ends */
  not_after?: string;
  /** Why the certificate could not be read (openssl_failed, unreadable_certificate) */
  error?: string;
};

export type RtspDiscovery = {
  paths: string[];
  camera: Camera;
};

export type Rules = {
  schema?: 1;
  /** Time a two-target condition must persist before it is high */
  dwell_ms: number;
  zones: {
    id: string;
    name: string;
    action: "ignore";
    node_id?: string;
    sensor_id?: number;
    x_min_mm: number;
    x_max_mm: number;
    y_min_mm: number;
    y_max_mm: number;
  }[];
};

/** The security options an administrator sets in Studio. The default of each is the way the server always behaved. nodes.nvs_encryption secrets = the alarm nodes keep the secrets they store (passwords, token, keys) encrypted in their flash (told in the policy message; off by default; no eFuse is burned). alarm.disarm_pin never = no PIN is asked to disarm or silence a siren (the duress PIN is untouched), if_set = asked of a user who has one, always = asked of everybody and a user without one cannot disarm (ARMOR_DISARM_PIN=required fixes it to always and wins over the setting). voice.silence_confirmation is sent to the voice service with every turn (header X-Armor-Policy). alarm.config_hash, server.zone_feed, server.zone_feed_signature and alarm.disarm_pin (left out of the message while it is if_set) reach the panels as the policy message (armor/alarm/{node_id}/policy). media.rtsp_proxy off puts the camera login in the command line of FFmpeg, visible to every user of the machine. voice.multipart_turn on lets the wall panel send a spoken turn as multipart/form-data with the audio as raw bytes (off: only the older raw request is taken and a multipart one is answered 415). network.login_secure_only on keeps the login stored for a device of the network from a node whose request did not come over TLS or from the machine of the server (off by default: any request of the node). panel.live_events on lets the wall panel listen to the WebSocket /api/v1/panel/events instead of asking the summary every few seconds (off: the panels on it are closed with 4403 and ask as before). client.device_lock is what the phone app asks of its user with the lock of the phone (fingerprint, face or the phone PIN): user = the switches of the app decide, sensitive = also before arming, disarming and unlocking, always = also to open the app; it can only raise what the person chose, and a phone without any lock is never shut out. voice.turn_max_bytes and voice.reply_audio_max_bytes are the most audio of a spoken turn and the most spoken answer handed back in the binary form, in bytes (the environment of the server is where they start) */
export type SecuritySettings = {
  "alarm.disarm_pin"?: "never" | "if_set" | "always";
  "voice.silence_confirmation"?: "off" | "pin" | "double_turn";
  "alarm.config_hash"?: boolean;
  "server.zone_feed"?: boolean;
  "server.zone_feed_signature"?: boolean;
  "media.rtsp_proxy"?: boolean;
  "network.login_secure_only"?: boolean;
  "voice.multipart_turn"?: boolean;
  "panel.live_events"?: boolean;
  "client.device_lock"?: "user" | "sensitive" | "always";
  "nodes.nvs_encryption"?: "off" | "secrets";
  "voice.turn_max_bytes"?: number;
  "voice.reply_audio_max_bytes"?: number;
};

export type SecuritySettingsState = {
  settings: SecuritySettings;
  stored: SecuritySettings;
  defaults: SecuritySettings;
  locked: string[];
};

export type ServerInfo = {
  service: "armor-server";
  /** Only for a signed-in client */
  version?: string;
  /** Only for a signed-in client */
  uptime_s?: number;
  /** Only for an operator */
  mode?: "armed" | "disarmed";
  /** Only for an operator */
  live_video?: boolean;
  /** Only for an operator */
  mqtt?: boolean;
};

export type ServiceList = {
  time_ms: number;
  /** False where the machine has none */
  systemd: boolean;
  services: {
    id: string;
    name: string;
    family: string;
    description?: string;
    kind: string;
    state: string;
    sub_state?: string;
    unit?: string;
    enabled?: boolean;
    pid?: number;
    since_ms?: number;
    memory_bytes?: number;
    restarts?: number;
    port?: number;
  }[];
};

/** The saved design of the house; revision 0 and a null document when none has been saved. The document is stored as the editor wrote it and its size is limited, not its shape. */
export type SiteDesign = {
  revision: number;
  updated_at?: string;
  updated_by?: string;
  site?: {
    [key: string]: unknown;
  } | null;
};

export type SolarAlarmSettings = {
  settings: EnergyAlarmSettings;
  defaults: EnergyAlarmSettings;
};

export type SolarDeviceRegistration = {
  node_id: string;
  device: string;
  kind: "inverter" | "battery";
  name: string;
  model: string;
  connection: "rs232" | "rs485" | "usb" | "can" | "wifi" | "other";
  notes: string;
  created_at: string;
};

export type SolarEnergy = {
  days: {
    date: string;
    pv_kwh: number;
    load_kwh: number;
    battery_in_kwh: number;
    battery_out_kwh: number;
  }[];
};

export type SolarHistory = {
  node_id: string;
  device: string;
  kind: "inverter" | "battery";
  minutes: number;
  samples: {
    t: number;
    [key: string]: unknown;
  }[];
};

export type SolarOverview = {
  devices: {
    node_id: string;
    device: string;
    kind: "inverter" | "battery";
    /** The latest message of the solar contract, an inverter or a battery */
    reading: Contracts.SolarInverter | Contracts.SolarBattery;
    received_at: string;
    stale: boolean;
    example?: boolean;
    /** Battery only - the extremes of the cells today, per module (the lowest and highest cell with its number and the moment, the widest gap of the module) and the widest gap of the whole bank */
    day_cells?: {
      date: string;
      bank_delta_v: number;
      modules: {
        n: number;
        delta_v: number;
        min: {
          v: number;
          cell: number;
          /** Milliseconds since 1970 */
          at: number;
        };
        max: {
          v: number;
          cell: number;
          /** Milliseconds since 1970 */
          at: number;
        };
      }[];
    };
    /** Battery only - the newest entries of the modules' own event logs that the node has read, newest first, in the battery's words (the protection names are never decoded) */
    events?: {
      n: number;
      /** Milliseconds since 1970 when the server first saw the entry */
      seen_at: number;
      event: {
        index: number;
        /** The battery's own clock as it prints it */
        time: string;
        voltage_v?: number;
        current_a?: number;
        temperature_c?: number;
        percent?: number;
        base_state?: string;
        voltage_state?: string;
        current_state?: string;
        temperature_state?: string;
        coulomb_state?: string;
        /** As the console prints it, the number and the mnemonic (0x2 PHV) */
        power_events?: string;
        battery_events?: string;
        system_fault?: string;
      };
    }[];
    registered?: SolarDeviceRegistration;
  }[];
  /** Declared devices with no reading yet */
  waiting: SolarDeviceRegistration[];
  totals: {
    inverters: number;
    batteries: number;
    stale: number;
    pv_w: number;
    load_w: number;
    battery_w: number | null;
    soc_percent: number | null;
    capacity_ah: number | null;
    full_capacity_ah: number | null;
    energy_kwh: number | null;
    grid_present: boolean;
    mode: "power_on" | "standby" | "line" | "battery" | "fault" | "power_saving" | "shutdown" | "unknown" | null | null;
  };
  catalog: {
    /** The inverter families that can be declared (the last is other) */
    inverter_models: string[];
    /** The battery models that can be declared (the last is other) */
    battery_models: string[];
    connections: ("rs232" | "rs485" | "usb" | "can" | "wifi" | "other")[];
    /** By model, the figures of the manuals of the models that have them */
    battery_profiles?: {
      [key: string]: {
        [key: string]: unknown;
      };
    };
    /** By model, the name to show (other is worded by each client, in its language) */
    labels?: {
      [key: string]: string;
    };
    /** By inverter family, the dialect of its serial protocol */
    inverter_dialects?: {
      [key: string]: string;
    };
    ant_bms?: {
      cell_counts: number[];
      currents_a: number[];
    };
  };
};

/** The bare status text (Unauthorized, Not Found) that a route answers with when it sends the status alone */
export type StatusText = string;

export type StoredDiagnostic = {
  at: string;
  /** The administrator who asked for it */
  requested_by: string;
  data: Contracts.NodeControlResultDiagnosticsPackage;
};

export type StreamTicket = {
  path: string;
  expiresAt: string;
  /** The picture the ticket gives */
  quality?: "normal" | "low";
};

/** What the signed-in person may do and what this server offers, so Studio and the phone show or hide from one place. The routes still check the role. A client that finds no such field (an older server) allows what the role allows, as before, and hides what needs a feature it was not told about */
export type StudioCapabilities = {
  version: 1;
  actions: {
    arm: boolean;
    disarm: boolean;
    acknowledge: boolean;
    /** Change devices, cameras, rules and the installation */
    operate: boolean;
    /** Move, record and take photos with the cameras */
    camera_control: boolean;
    administer: boolean;
    manage_users: boolean;
    security_settings: boolean;
  };
  /** The parts of this server that exist in this version */
  features: ("security_settings" | "zone_feed_key" | "rtsp_tunnel")[];
  security: SecuritySettings & {
    /** The options the environment of the server fixes */
    locked?: string[];
  };
};

export type StudioLogin = {
  username: string;
  password: string;
};

export type StudioSessionList = {
  sessions: {
    id: string;
    created: string;
    last_seen: string;
    origin?: string;
    ip?: string;
    agent?: string;
    current: boolean;
  }[];
};

/** A session was opened (201), or the second factor is still needed (200 with totp_required) */
export type StudioSessionOpened = {
  expiresAt?: string;
  user?: AccountUser;
  totp_required?: true;
  challenge?: string;
  expires_in_s?: number;
};

export type StudioSessionState = {
  authenticated: boolean;
  user?: AccountUser;
  capabilities?: StudioCapabilities;
};

export type SystemEvent = Contracts.SystemEvent;

/** The latest sample (cpu, memory, temperatures, disks, network, uptime) and the samples before it */
export type SystemMetrics = {
  at_ms?: number;
  cpu?: {
    percent: number | null;
    cores: number;
    load: number[];
    mhz?: number;
  };
  memory?: {
    total: number;
    used: number;
    available: number;
    swap_total: number;
    swap_used: number;
  };
  temperatures?: {
    name: string;
    celsius: number;
  }[];
  disks?: {
    mount: string;
    device: string;
    kind: "sd" | "usb" | "nvme" | "other";
    fs: string;
    total: number;
    used: number;
  }[];
  network?: {
    name: string;
    up: boolean;
    rx_bps: number | null;
    tx_bps: number | null;
    rx_bytes: number;
    tx_bytes: number;
  }[];
  uptime_s?: number;
  history: {
    t: number;
    cpu: number | null;
    memory: number;
    swap: number;
    temperature: number | null;
    rx_bps: number;
    tx_bps: number;
  }[];
};

export type SystemState = {
  mode: "armed" | "disarmed";
  revision: number;
  updated_at: string;
  nodes: {
    [key: string]: {
      node_id: string;
      /** Reported online and heard from recently */
      online: boolean;
      /** Silent for longer than ARMOR_NODE_STALE_AFTER_S */
      stale: boolean;
      timestamp_ms: number;
      lux: number | null;
      target_count: number;
      /** Where the node's own web panel is, as the node said itself in its information message; null until it has. Not stored, the node repeats it. */
      panel: {
        name: string;
        firmware: string;
        ip: string;
        port: number;
      } | null;
      /** The targets of the node's latest report, in the radar's own frame; empty until it reports and after a restart. `counted` is false inside an ignore zone. */
      targets?: {
        sensor_id: number;
        track_id: number;
        /** Sideways, millimetres */
        x_mm: number;
        /** Forward, millimetres */
        y_mm: number;
        speed_mm_s: number;
        counted: boolean;
      }[];
      alert_level: "normal" | "review" | "high";
    };
  };
};

export type SystemSummary = {
  service: string;
  version: string;
  /** The version of Node.js the server runs on */
  node: string;
  uptime_s: number;
  mode: "armed" | "disarmed";
  revision: number;
  mqtt: boolean;
  live_video: boolean;
  webhook: boolean;
  cameras_check_s: number;
  counts: {
    nodes: number;
    nodes_online: number;
    cameras: number;
    devices: number;
    devices_online: number;
    alarms_active: number;
    automations: number;
    users: number;
    events: number;
  };
  storage: {
    media_files: number;
    media_bytes: number;
    media_limit_bytes: number;
    disk: {
      free_bytes: number;
      total_bytes: number;
    } | null;
  };
  [key: string]: unknown;
};

export type TotpEnabled = {
  enabled: true;
  recovery_codes: string[];
};

export type TotpSetup = {
  secret: string;
  uri: string;
};

export type TotpState = {
  enabled: boolean;
  recovery_left: number;
  policy: "off" | "remote" | "always";
};

export type UserChange = {
  username?: string;
  password?: string;
  role?: "admin" | "operator";
};

export type UserList = {
  users: (PublicUser & {
    current: boolean;
  })[];
  minPasswordLength: number;
};

export type VoiceCommandResult = {
  accepted: boolean;
  executed: boolean;
  intent: string;
  outcome: "accepted" | "confirmation-needed" | "confirmation-refused" | "not-understood";
  speech: string;
  confirmation_token?: string;
  reason?: string;
  result?: {
    [key: string]: unknown;
  };
};

export type VoiceStatus = {
  available: boolean;
};

export type VoiceTurn = {
  heard: string;
  reply: string;
  /** 16 kHz 16-bit mono PCM */
  audio?: string;
  /** Set by the server, to a request in the binary form, when the spoken answer was above its limit and was left out */
  audio_omitted?: "too_large";
};

/** The binary form of a spoken turn: meta (optional) and audio, see docs/CONTRACTS.md, Voice turn */
export type VoiceTurnForm = {
  meta?: VoiceTurnMeta;
  /** Raw 16 kHz 16-bit signed little-endian mono PCM, an even number of bytes */
  audio: string;
};

export type VoiceTurnMeta = {
  language: "en" | "es" | "de" | "fr" | "it" | "ja" | "zh" | "pt";
  encoding: "pcm_s16le";
  sample_rate: 16000;
  channels: 1;
  /** How the spoken answer comes back; base64 when absent */
  reply_audio?: "base64" | "binary" | "none";
};

export type WireguardPeer = {
  name: string;
  /** The configuration file for the peer, with its private key */
  config: string;
  /** The same configuration as an SVG QR code */
  qr_svg: string;
};

export type ZoneFeedKey = {
  node_id: string;
  key: string;
  algorithm: "HMAC-SHA256";
};

export type ZoneLink = {
  device_id: string;
  node_id: string;
  zone_id: string;
};

export type ZoneLinks = {
  links: ZoneLink[];
};
