// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_types.py. Do not edit.
package es.electrohobby3d.armor.contracts

data class RadarTrack(
    val sensor_id: Long,
    val track_id: Long,
    val x_mm: Double,
    val y_mm: Double,
    val speed_mm_s: Double
)

data class Telemetry(
    val kind: String? = null,
    val node_id: String,
    val timestamp_ms: Long,
    val lux: Double,
    val targets: List<RadarTrack>
)

data class Health(
    val node_id: String,
    val timestamp_ms: Long,
    val online: Boolean,
    val kind: String? = null
)

data class Command(
    val kind: String? = null,
    val node_id: String,
    val timestamp_ms: Long,
    val command: String,
    val sensitivity: Long? = null
)

data class Info(
    val kind: String? = null,
    val node_id: String,
    val timestamp_ms: Long,
    val name: String,
    val firmware: String,
    val ip: String,
    val port: Long,
    val contract: String? = null
)

data class SolarInverterUnits(
    val unit: Long,
    val serial: String? = null,
    val mode: String,
    val fault_code: String? = null,
    val grid_v: Double? = null,
    val out_v: Double? = null,
    val out_va: Double? = null,
    val out_w: Double? = null,
    val load_percent: Double? = null,
    val battery_v: Double? = null,
    val battery_percent: Double? = null,
    val pv_v: Double? = null,
    val charging_a: Double? = null
)

data class SolarInverterRatings(
    val grid_rating_v: Double? = null,
    val out_rating_v: Double? = null,
    val out_rating_hz: Double? = null,
    val out_rating_va: Double? = null,
    val out_rating_w: Double? = null,
    val battery_rating_v: Double? = null,
    val battery_recharge_v: Double? = null,
    val battery_under_v: Double? = null,
    val battery_bulk_v: Double? = null,
    val battery_float_v: Double? = null,
    val max_charge_a: Double? = null,
    val max_ac_charge_a: Double? = null,
    val battery_type: String? = null,
    val input_range: String? = null,
    val output_priority: String? = null,
    val charger_priority: String? = null
)

data class SolarInverter(
    val kind: String = "inverter",
    val node_id: String,
    val device: String,
    val timestamp_ms: Long,
    val mode: String,
    val grid_v: Double,
    val grid_hz: Double,
    val out_v: Double,
    val out_hz: Double,
    val out_va: Double,
    val out_w: Double,
    val load_percent: Double,
    val battery_v: Double,
    val battery_a: Double,
    val battery_percent: Double,
    val pv_v: Double,
    val pv_a: Double,
    val pv_w: Double,
    val heatsink_c: Double,
    val ac_charging: Boolean,
    val pv_charging: Boolean,
    val load_on: Boolean,
    val warnings: List<String>,
    val warnings_known: Boolean? = null,
    val clamped: List<String>? = null,
    val pv2_v: Double? = null,
    val pv2_a: Double? = null,
    val pv2_w: Double? = null,
    val total_out_w: Double? = null,
    val total_out_va: Double? = null,
    val total_load_percent: Double? = null,
    val total_charging_a: Double? = null,
    val units: List<SolarInverterUnits>? = null,
    val bus_v: Double? = null,
    val serial: String? = null,
    val firmware: String? = null,
    val pv_energy_total_wh: Double? = null,
    val ratings: SolarInverterRatings? = null
)

data class SolarModuleLastEvent(
    val index: Long,
    val time: String,
    val voltage_v: Double? = null,
    val current_a: Double? = null,
    val temperature_c: Double? = null,
    val percent: Long? = null,
    val base_state: String? = null,
    val voltage_state: String? = null,
    val current_state: String? = null,
    val temperature_state: String? = null,
    val coulomb_state: String? = null,
    val power_events: String? = null,
    val battery_events: String? = null,
    val system_fault: String? = null
)

data class SolarModule(
    val n: Long,
    val present: Boolean,
    val voltage_v: Double? = null,
    val current_a: Double? = null,
    val temperature_c: Double? = null,
    val soc_percent: Long? = null,
    val state: String? = null,
    val cells_v: List<Double>? = null,
    val counters: Map<String, Long>? = null,
    val temperatures_c: List<Double>? = null,
    val capacity_ah: Double? = null,
    val full_capacity_ah: Double? = null,
    val cycles: Long? = null,
    val health_percent: Long? = null,
    val model: String? = null,
    val cell_count: Long? = null,
    val max_charge_a: Double? = null,
    val max_discharge_a: Double? = null,
    val console_baud: Long? = null,
    val soh_counts: List<Long>? = null,
    val soh_abnormal: List<Long>? = null,
    val last_event: SolarModuleLastEvent? = null,
    val board_version: String? = null,
    val main_soft_version: String? = null,
    val soft_version: String? = null
)

data class SolarBattery(
    val kind: String = "battery",
    val node_id: String,
    val device: String,
    val timestamp_ms: Long,
    val modules: Long,
    val state: String? = null,
    val voltage_v: Double? = null,
    val current_a: Double? = null,
    val temperature_min_c: Double? = null,
    val temperature_max_c: Double? = null,
    val cell_min_v: Double? = null,
    val cell_max_v: Double? = null,
    val soc_percent: Long? = null,
    val alarm: Boolean? = null,
    val stack: List<SolarModule>,
    val model: String? = null,
    val capacity_ah: Double? = null,
    val full_capacity_ah: Double? = null,
    val energy_kwh: Double? = null,
    val cycles: Long? = null,
    val health_percent: Long? = null,
    val power_w: Double? = null,
    val balancing: Long? = null,
    val protecting: Boolean? = null,
    val charge_mos: Long? = null,
    val discharge_mos: Long? = null
)

data class ElectricalChannel(
    val id: String,
    val domain: String,
    val label: String? = null,
    val voltage_v: Double? = null,
    val current_a: Double? = null,
    val power_w: Double? = null,
    val energy_kwh: Double? = null,
    val reading_age_ms: Long? = null,
    val errors: Long? = null,
    val power_estimated: Boolean? = null,
    val frequency_hz: Double? = null,
    val power_factor: Double? = null,
    val state: String? = null,
    val alarm: Boolean? = null,
    val alarm_code: String? = null
)

data class ElectricalSwitch(
    val id: String,
    val kind: String = "transfer",
    val label: String? = null,
    val source_a: String? = null,
    val source_b: String? = null,
    val a_closed: Boolean,
    val b_closed: Boolean,
    val selected: String,
    val wanted: String,
    val closing: Boolean,
    val armed: Boolean,
    val fault: String
)

data class Electrical(
    val kind: String = "electrical",
    val node_id: String,
    val timestamp_ms: Long,
    val switching_enabled: Boolean? = null,
    val channels: List<ElectricalChannel>,
    val switches: List<ElectricalSwitch>? = null
)

data class ElectricalCommand(
    val kind: String = "electrical_command",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val switch: String,
    val action: String,
    val token: String? = null
)

data class ElectricalResult(
    val kind: String = "electrical_result",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val switch: String,
    val action: String,
    val accepted: Boolean,
    val refusal: String,
    val token: String? = null
)

data class SolarBatteryStage(
    val id: String,
    val index: Long,
    val total: Long,
    val size: Long,
    val crc32: Long,
    val data: String
)

data class SolarBatteryCommandParamsValues(
    val pov: Long? = null,
    val povr: Long? = null,
    val phv: Long? = null,
    val phvr: Long? = null,
    val plv: Long? = null,
    val plvr: Long? = null,
    val puv: Long? = null,
    val puvr: Long? = null,
    val pslp: Long? = null,
    val bov: Long? = null,
    val bovr: Long? = null,
    val bhv: Long? = null,
    val bhvr: Long? = null,
    val blv: Long? = null,
    val blvr: Long? = null,
    val buv: Long? = null,
    val buvr: Long? = null,
    val bslp: Long? = null,
    val cot: Long? = null,
    val cotr: Long? = null,
    val cht: Long? = null,
    val chtr: Long? = null,
    val clt: Long? = null,
    val cltr: Long? = null,
    val cut: Long? = null,
    val cutr: Long? = null
)

data class SolarBatteryCommandParamsItems(
    val bov: String? = null,
    val bhv: String? = null,
    val blv: String? = null,
    val buv: String? = null,
    val bslp: String? = null,
    val pov: String? = null,
    val phv: String? = null,
    val plv: String? = null,
    val puv: String? = null,
    val pslp: String? = null,
    val coc: String? = null,
    val coc2: String? = null,
    val doc: String? = null,
    val doc2: String? = null
)

data class SolarBatteryCommandParams(
    val which: String? = null,
    val group: String? = null,
    val values: SolarBatteryCommandParamsValues? = null,
    val items: SolarBatteryCommandParamsItems? = null,
    val accept_risk: Boolean? = null,
    val output: String? = null,
    val state: String? = null,
    val serial: String? = null,
    val restore_barcode: Boolean? = null,
    val image_size: Long? = null,
    val image_crc32: Long? = null,
    val image_version: String? = null,
    val clear_eeprom: Boolean? = null,
    val line: String? = null
)

data class SolarBatteryCommand(
    val kind: String = "solar_battery_command",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val port: Long,
    val action: String,
    val op: String? = null,
    val params: SolarBatteryCommandParams? = null,
    val serial: String? = null,
    val token: String? = null,
    val stage: SolarBatteryStage? = null
)

data class SolarBatteryIdentity(
    val model: String,
    val serial: String,
    val soft_version: String,
    val board: String,
    val capacity_ah: Long? = null
)

data class SolarBatteryResult(
    val kind: String = "solar_battery_result",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val port: Long,
    val action: String,
    val op: String? = null,
    val stage: String,
    val accepted: Boolean,
    val refusal: String,
    val token: String? = null,
    val canonical: String? = null,
    val summary: String? = null,
    val risk: String? = null,
    val atomic: Boolean? = null,
    val battery: SolarBatteryIdentity? = null,
    val snapshot_before: String? = null,
    val outcome: String? = null,
    val code: String? = null,
    val steps_done: Long? = null,
    val steps_total: Long? = null,
    val writes_done: Long? = null,
    val packets_sent: Long? = null,
    val packets_total: Long? = null,
    val truncated: Boolean? = null,
    val before: String? = null,
    val after: String? = null,
    val transcript: String? = null,
    val received: Long? = null
)

data class NodeControlCommand(
    val kind: String = "node_control_command",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val action: String,
    val operation: String,
    val mode: String,
    val delay_s: Long? = null,
    val slot: Long? = null,
    val duration_s: Long? = null,
    val token: String? = null,
    val requested_by: String,
    val detail: String? = null
)

data class NodeControlResultDiagnosticsPackageHeap(
    val internal_free: Long,
    val internal_min: Long,
    val internal_largest: Long,
    val total_free: Long,
    val total_min: Long,
    val psram_free: Long? = null
)

data class NodeControlResultDiagnosticsPackageTasks(
    val name: String,
    val stack_free: Long,
    val priority: Long,
    val state: String
)

data class NodeControlResultDiagnosticsPackageResets(
    val reason: String,
    val uptime_s: Long,
    val guard_restarts_in_hour: Long
)

data class NodeControlResultDiagnosticsPackageBoot(
    val cause: String,
    val reset_reason: String,
    val uptime_before_s: Long? = null,
    val heap_internal_free: Long? = null,
    val heap_internal_largest: Long? = null,
    val coredump: Boolean,
    val deliberate: Boolean,
    val guard: Boolean
)

data class NodeControlResultDiagnosticsPackageMemoryGate(
    val closed: Boolean,
    val transitions: Long,
    val close_free: Long,
    val close_block: Long,
    val open_free: Long,
    val open_block: Long
)

data class NodeControlResultDiagnosticsPackageVersionsSensors(
    val name: String,
    val version: String
)

data class NodeControlResultDiagnosticsPackageVersions(
    val firmware: String,
    val idf: String,
    val board: String? = null,
    val sensors: List<NodeControlResultDiagnosticsPackageVersionsSensors>
)

data class NodeControlResultDiagnosticsPackageCoredumpSummary(
    val task: String,
    val reason: String? = null,
    val pc: String? = null,
    val backtrace: List<String>? = null,
    val app_sha256: String? = null
)

data class NodeControlResultDiagnosticsPackageCoredump(
    val present: Boolean,
    val size: Long? = null,
    val summary: NodeControlResultDiagnosticsPackageCoredumpSummary? = null
)

data class NodeControlResultDiagnosticsPackage(
    val detail: String,
    val heap: NodeControlResultDiagnosticsPackageHeap? = null,
    val tasks: List<NodeControlResultDiagnosticsPackageTasks>? = null,
    val resets: NodeControlResultDiagnosticsPackageResets? = null,
    val boot: NodeControlResultDiagnosticsPackageBoot? = null,
    val memory_gate: NodeControlResultDiagnosticsPackageMemoryGate? = null,
    val versions: NodeControlResultDiagnosticsPackageVersions? = null,
    val config: Map<String, String>? = null,
    val coredump: NodeControlResultDiagnosticsPackageCoredump? = null,
    val log: String,
    val truncated: Boolean
)

data class NodeControlResultDiagnostics(
    val firmware: String,
    val uptime_s: Long,
    val reset_reason: String,
    val heap_free: Long,
    val heap_min: Long,
    val psram_free: Long? = null,
    val stack_min_free: Long? = null,
    val rssi: Long? = null,
    val mqtt_connected: Boolean,
    val state: String,
    val maintenance: Boolean,
    val `package`: NodeControlResultDiagnosticsPackage? = null
)

data class NodeControlResult(
    val kind: String = "node_control_result",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val action: String,
    val operation: String,
    val stage: String,
    val accepted: Boolean,
    val refusal: String,
    val token: String? = null,
    val token_ttl_s: Long? = null,
    val reason: String? = null,
    val mode: String? = null,
    val restart_in_s: Long? = null,
    val uptime_s: Long? = null,
    val firmware: String? = null,
    val requested_by: String? = null,
    val state: String? = null,
    val maintenance: Boolean? = null,
    val until_s: Long? = null,
    val since_ms: Long? = null,
    val diagnostics: NodeControlResultDiagnostics? = null
)

data class NodeMaintenance(
    val kind: String = "node_maintenance",
    val node_id: String,
    val timestamp_ms: Long,
    val active: Boolean,
    val reason: String,
    val expected_s: Long? = null,
    val firmware: String,
    val requested_by: String? = null
)

data class RadarEvent(
    val kind: String = "radar_event",
    val node_id: String,
    val timestamp_ms: Long,
    val boot: Long,
    val seq: Long,
    val event: String,
    val name: String? = null,
    val sensor_id: Long? = null,
    val track_id: Long? = null,
    val movement: String? = null,
    val value: Long? = null,
    val count: Long? = null,
    val direction: String? = null,
    val from: String? = null,
    val by: String? = null
)

data class DiagnosticTokenRequest(
    val nodes: List<String>,
    val ttl_s: Long? = null,
    val label: String? = null
)

data class DiagnosticTokenCreated(
    val id: String,
    val token: String,
    val scope: String = "read_only",
    val nodes: List<String>,
    val label: String? = null,
    val created_at: String,
    val expires_at: String,
    val created_by: String
)

data class DiagnosticTokenInfo(
    val id: String,
    val scope: String = "read_only",
    val nodes: List<String>,
    val label: String? = null,
    val created_at: String,
    val expires_at: String,
    val created_by: String,
    val status: String,
    val revoked_at: String? = null,
    val revoked_by: String? = null,
    val uses: Long,
    val last_used_at: String? = null
)

data class AlarmZone(
    val id: String,
    val name: String? = null,
    val kind: String,
    val state: String,
    val bypassed: Boolean
)

data class AlarmEvent(
    val ago_s: Long,
    val kind: String,
    val zone: String? = null
)

data class Alarm(
    val kind: String = "alarm",
    val node_id: String,
    val timestamp_ms: Long,
    val phase: String,
    val mode: String,
    val siren: Boolean,
    val locked_out: Boolean,
    val commands_enabled: Boolean,
    val zones: List<AlarmZone>,
    val open_zones: List<String>,
    val events: List<AlarmEvent>,
    val arm_profiles: Boolean? = null,
    val profile: String? = null,
    val siren_loop: String? = null,
    val siren_fault: Boolean? = null,
    val seq: Long? = null,
    val sig: String? = null
)

data class ArmProfileZone(
    val id: String,
    val armed: Boolean? = null,
    val delay: String? = null
)

data class ArmProfile(
    val id: String,
    val name: String,
    val base: String,
    val exit_delay_s: Long? = null,
    val entry_delay_s: Long? = null,
    val siren: Boolean? = null,
    val notify: String? = null,
    val zones: List<ArmProfileZone>? = null
)

data class AlarmCommand(
    val kind: String = "alarm_command",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val action: String,
    val mode: String? = null,
    val force: Boolean? = null,
    val profile: ArmProfile? = null
)

data class AlarmResult(
    val kind: String = "alarm_result",
    val node_id: String,
    val timestamp_ms: Long,
    val command_id: String,
    val action: String,
    val accepted: Boolean,
    val refusal: String,
    val phase: String
)

data class ArmingModesModesAway(
    val entry: List<String>? = null,
    val exit_delay_s: Long? = null,
    val entry_delay_s: Long? = null
)

data class ArmingModesModesHome(
    val defends: List<String>? = null,
    val entry: List<String>? = null,
    val exit_delay_s: Long? = null,
    val entry_delay_s: Long? = null
)

data class ArmingModesModesNight(
    val defends: List<String>? = null,
    val entry: List<String>? = null,
    val exit_delay_s: Long? = null,
    val entry_delay_s: Long? = null
)

data class ArmingModesModes(
    val away: ArmingModesModesAway,
    val home: ArmingModesModesHome,
    val night: ArmingModesModesNight
)

data class ArmingModesSchedule(
    val mode: String,
    val days: List<Long>,
    val at: String
)

data class ArmingModesPanelMapProfiles(
    val away: String? = null,
    val home: String? = null,
    val night: String? = null
)

data class ArmingModesPanelMap(
    val profiles: ArmingModesPanelMapProfiles? = null,
    val only: List<String>? = null
)

data class ArmingModes(
    val modes: ArmingModesModes,
    val schedule: List<ArmingModesSchedule>? = null,
    val panel_map: ArmingModesPanelMap? = null
)

data class AlarmZoneFeed(
    val zone: String,
    val state: String,
    val battery_low: Boolean,
    val seq: Long? = null,
    val sig: String? = null
)

data class AlarmPolicy(
    val config_hash: Boolean,
    val zone_feed: Boolean,
    val zone_feed_signature: Boolean,
    val disarm_pin: String? = null,
    val nvs_encryption: String? = null
)

data class NodeHealthBoot(
    val cause: String,
    val reset_reason: String,
    val uptime_before_s: Long? = null,
    val heap_internal_free: Long? = null,
    val heap_internal_largest: Long? = null,
    val coredump: Boolean,
    val deliberate: Boolean,
    val guard: Boolean
)

data class NodeHealthMemoryGate(
    val closed: Boolean,
    val transitions: Long,
    val close_free: Long,
    val close_block: Long,
    val open_free: Long,
    val open_block: Long
)

data class NodeHealthCoredump(
    val present: Boolean,
    val size: Long? = null
)

data class NodeHealthConfigCheck(
    val snapshot: String? = null,
    val reverted: String? = null
)

data class NodeHealthSensors(
    val sensor_id: Long,
    val model: String,
    val state: String,
    val firmware_known: Boolean,
    val firmware: String? = null,
    val bluetooth: String,
    val mac: String? = null,
    val bluetooth_alert: Boolean? = null,
    val quirk: String? = null
)

data class NodeHealthRadar(
    val perimeter_enabled: Boolean,
    val masked: Boolean,
    val wifi_jam: Boolean,
    val bridge_open: Boolean,
    val events_buffered: Long,
    val sensor_bluetooth_off: Boolean
)

data class NodeHealth(
    val kind: String = "node_health",
    val node_id: String,
    val timestamp_ms: Long,
    val family: String,
    val firmware: String,
    val contract: String? = null,
    val board: String? = null,
    val uptime_s: Long,
    val reset_reason: String,
    val heap_free: Long,
    val heap_min: Long,
    val heap_internal_free: Long? = null,
    val heap_internal_min: Long? = null,
    val heap_internal_largest: Long? = null,
    val psram_free: Long? = null,
    val link: String,
    val link_up: Boolean,
    val rssi_dbm: Long? = null,
    val broker_reconnects: Long,
    val low_stack_tasks: Long? = null,
    val stack_min_free: Long? = null,
    val stack_min_task: String? = null,
    val last_error: String? = null,
    val control_state: String? = null,
    val control_since_ms: Long? = null,
    val control_by: String? = null,
    val control_until_s: Long? = null,
    val maintenance: Boolean? = null,
    val maintenance_until_s: Long? = null,
    val boot: NodeHealthBoot? = null,
    val memory_gate: NodeHealthMemoryGate? = null,
    val coredump: NodeHealthCoredump? = null,
    val config_check: NodeHealthConfigCheck? = null,
    val sensors: List<NodeHealthSensors>? = null,
    val radar: NodeHealthRadar? = null
)

data class VoiceTurnMeta(
    val language: String,
    val encoding: String,
    val sample_rate: Long,
    val channels: Long,
    val reply_audio: String? = null
)

data class VoiceTurnResult(
    val heard: String,
    val reply: String,
    val audio: String? = null,
    val audio_omitted: String? = null,
    val challenge: String? = null
)

data class ConnectionEvent(
    val id: Long,
    val at: String,
    val type: String = "connection",
    val action: String,
    val client_kind: String,
    val client_id: String,
    val user: String? = null,
    val origin: String? = null,
    val two_factor: Boolean? = null,
    val app_version: String? = null,
    val subject: String? = null,
    val ip: String? = null,
    val agent: String? = null
)

data class SystemEvent(
    val id: Long,
    val at: String,
    val type: String = "system",
    val category: String,
    val action: String,
    val subject: String? = null,
    val by: String? = null,
    val version: String? = null,
    val previous_version: String? = null,
    val profile: String? = null,
    val outcome: String? = null
)

data class ConnectionClient(
    val id: String,
    val kind: String,
    val user: String? = null,
    val label: String? = null,
    val app_version: String? = null,
    val origin: String? = null,
    val two_factor: Boolean? = null,
    val first_seen: String,
    val last_seen: String,
    val last_failure: String? = null,
    val active_sessions: Long,
    val logins_ok: Long,
    val logins_failed: Long,
    val ip: String? = null,
    val agent: String? = null
)

data class DailySummaryBodyTotals(
    val events: Long,
    val alarms: Long,
    val serious_alarms: Long,
    val false_alarms: Long
)

data class DailySummaryBodySeriousAlarms(
    val t_s: Double,
    val code: String? = null,
    val zone: String? = null,
    val node: String? = null,
    val sensor: String? = null,
    val severity: String? = null,
    val watts: Double? = null,
    val value: Double? = null,
    val duration_s: Double? = null,
    val mean_w: Double? = null,
    val limit_w: Double? = null
)

data class DailySummaryBodyNodesLinkLost(
    val node: String,
    val count: Long,
    val total_s: Double
)

data class DailySummaryBodyOutlierReadings(
    val t_s: Double,
    val node: String,
    val sensor: String,
    val value: Double,
    val median: Double,
    val score: Double
)

data class DailySummaryBodyConsumptionPeaks(
    val t_s: Double,
    val code: String? = null,
    val zone: String? = null,
    val node: String? = null,
    val sensor: String? = null,
    val severity: String? = null,
    val watts: Double? = null,
    val value: Double? = null,
    val duration_s: Double? = null,
    val mean_w: Double? = null,
    val limit_w: Double? = null
)

data class DailySummaryBodyConsumption(
    val samples: Long,
    val peaks: List<DailySummaryBodyConsumptionPeaks>
)

data class DailySummaryBody(
    val schema: String = "armor-daily-summary/1",
    val totals: DailySummaryBodyTotals,
    val by_type: Map<String, Long>,
    val by_zone: Map<String, Long>,
    val by_hour: List<Long>,
    val serious_alarms: List<DailySummaryBodySeriousAlarms>? = null,
    val nodes_link_lost: List<DailySummaryBodyNodesLinkLost>? = null,
    val outlier_readings: List<DailySummaryBodyOutlierReadings>? = null,
    val consumption: DailySummaryBodyConsumption? = null
)

data class DailySummaryFindingSubject(
    val code: String? = null,
    val zone: String? = null,
    val node: String? = null
)

data class DailySummaryFindingDetail(
    val hours: List<Long>? = null,
    val tolerance_min: Double? = null,
    val max_gap_s: Double? = null,
    val limit_s: Double? = null,
    val minimum: Long? = null,
    val window: Long? = null,
    val sigma: Double? = null,
    val min_ratio: Double? = null
)

data class DailySummaryFindingEvidence(
    val t_s: Double,
    val code: String? = null,
    val zone: String? = null,
    val node: String? = null,
    val sensor: String? = null,
    val severity: String? = null,
    val watts: Double? = null,
    val value: Double? = null,
    val duration_s: Double? = null,
    val mean_w: Double? = null,
    val limit_w: Double? = null
)

data class DailySummaryFinding(
    val kind: String,
    val subject: DailySummaryFindingSubject,
    val count: Long,
    val detail: DailySummaryFindingDetail,
    val evidence: List<DailySummaryFindingEvidence>
)

data class DailySummary(
    val date: String,
    val language: String,
    val summary: DailySummaryBody,
    val findings: List<DailySummaryFinding>,
    val text: String,
    val ai_note: String? = null
)

data class Heatmap(
    val schema: String = "armor.vision.heatmap/v1",
    val camera_id: String,
    val cols: Long,
    val rows: Long,
    val accepted_positions: Long,
    val rejected_positions: Long,
    val total: Double,
    val max: Double,
    val weights: List<List<Double>>,
    val normalized: List<List<Double>>,
    val contains_images: Boolean = false
)

data class NetworkInterface(
    val name: String,
    val ip: String,
    val cidr: String,
    val gateway: String? = null,
    val rx_bps: Long? = null,
    val tx_bps: Long? = null
)

data class NetworkProbe(
    val target: String,
    val kind: String,
    val ok: Boolean,
    val latency_ms: Double? = null
)

data class NetworkOutage(
    val started_ms: Long,
    val ended_ms: Long,
    val duration_s: Long
)

data class NetworkInternet(
    val state: String,
    val since_ms: Long? = null,
    val gateway_ok: Boolean? = null,
    val latency_ms: Double? = null,
    val loss_percent: Double? = null,
    val probes: List<NetworkProbe>? = null,
    val last_outage: NetworkOutage? = null,
    val outages_24h: Long? = null,
    val downtime_24h_s: Long? = null
)

data class NetworkPort(
    val port: Long,
    val proto: String,
    val service: String? = null,
    val banner: String? = null
)

data class NetworkDevice(
    val id: String,
    val ip: String,
    val mac: String? = null,
    val randomized_mac: Boolean? = null,
    val vendor: String? = null,
    val hostname: String? = null,
    val kind: String? = null,
    val os: String? = null,
    val online: Boolean,
    val first_seen_ms: Long,
    val last_seen_ms: Long,
    val latency_ms: Double? = null,
    val ports: List<NetworkPort>? = null,
    val services: List<String>? = null
)

data class NetworkEvent(
    val id: String,
    val kind: String,
    val at_ms: Long,
    val device_id: String? = null,
    val port: Long? = null,
    val outage_s: Long? = null,
    val server: String? = null,
    val recommendation: String? = null,
    val detail: String? = null
)

data class NetworkScan(
    val last_ms: Long,
    val hosts: Long,
    val duration_ms: Long? = null
)

data class NetworkPublicDns(
    val name: String,
    val addresses: List<String>,
    val matches: Boolean
)

data class NetworkPublic(
    val ip: String,
    val hostname: String? = null,
    val city: String? = null,
    val region: String? = null,
    val country: String? = null,
    val org: String? = null,
    val timezone: String? = null,
    val checked_ms: Long,
    val changed_ms: Long? = null,
    val dns: NetworkPublicDns? = null
)

data class NetworkResults(
    val id: String,
    val type: String,
    val ok: Boolean,
    val finished_ms: Long,
    val device_id: String? = null,
    val output: String? = null,
    val ports: List<NetworkPort>? = null,
    val latency_ms: Double? = null
)

data class Network(
    val kind: String = "network",
    val node_id: String,
    val contract: Long? = null,
    val timestamp_ms: Long,
    val `interface`: NetworkInterface,
    val internet: NetworkInternet,
    val devices: List<NetworkDevice>,
    val events: List<NetworkEvent>? = null,
    val scan: NetworkScan? = null,
    val public: NetworkPublic? = null,
    val results: List<NetworkResults>? = null
)

data class AiObservationRegions(
    val x: Double,
    val y: Double,
    val w: Double,
    val h: Double
)

data class AiObservation(
    val camera_id: String,
    val severity: String,
    val reasons: List<String>,
    val profile: String,
    val motion: Double,
    val motion_ratio: Double? = null,
    val regions: List<AiObservationRegions>? = null,
    val radar_tracks: Long
)

data class DeviceState(
    val on: Boolean
)

data class NetworkOrdersCommands(
    val id: String,
    val type: String,
    val device_id: String? = null,
    val ip: String? = null,
    val mac: String? = null,
    val port: Long? = null,
    val auth_sealed: String? = null
)

data class NetworkOrders(
    val accepted: Boolean = true,
    val commands: List<NetworkOrdersCommands>
)

data class ServerAlert(
    val service: String = "armor-server",
    val event: String,
    val at: String,
    val mode: String,
    val node_id: String? = null,
    val camera_id: String? = null,
    val targets: Long? = null,
    val minutes: Long? = null,
    val alarm_id: String? = null,
    val severity: String? = null,
    val code: String? = null,
    val device_id: String? = null,
    val solar_id: String? = null,
    val electrical_id: String? = null,
    val alarm_node_id: String? = null,
    val network_id: String? = null,
    val silent: Boolean? = null,
    val automation: String? = null,
    val login_user: String? = null,
    val login_from: String? = null,
    val login_country: String? = null,
    val login_country_new: Boolean? = null
)

data class VisionEventVectors(
    val track_id: Long,
    val dx: Double,
    val dy: Double,
    val speed: Double
)

data class VisionEvent(
    val schema: String,
    val type: String,
    val camera_id: String,
    val zone_id: String,
    val zone_name: String,
    val track_id: Long,
    val label: String,
    val confidence: Double,
    val box: List<Double>,
    val timestamp: Double,
    val timestamp_ms: Long,
    val authorizes_action: Boolean = false,
    val radar_tracks: Long? = null,
    val vectors: List<VisionEventVectors>? = null
)

object ContractLimits {
    const val MAX_TARGETS = 15
    const val MAX_LUX = 200000.0
    val COMMANDS = listOf("calibrate", "set_thresholds", "restart")
}
