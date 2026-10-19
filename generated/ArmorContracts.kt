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
    val node_id: String,
    val timestamp_ms: Long,
    val command: String,
    val sensitivity: Long? = null
)

data class Info(
    val node_id: String,
    val timestamp_ms: Long,
    val name: String,
    val firmware: String,
    val ip: String,
    val port: Long
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
    val requested_by: String
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
    val maintenance: Boolean
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
    val profile: String? = null
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

data class NodeHealth(
    val kind: String = "node_health",
    val node_id: String,
    val timestamp_ms: Long,
    val family: String,
    val firmware: String,
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
    val last_error: String? = null,
    val control_state: String? = null,
    val control_since_ms: Long? = null,
    val control_by: String? = null,
    val control_until_s: Long? = null,
    val maintenance: Boolean? = null,
    val maintenance_until_s: Long? = null
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
    val detail: String? = null
)

data class NetworkScan(
    val last_ms: Long,
    val hosts: Long,
    val duration_ms: Long? = null
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
    val changed_ms: Long? = null
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
    val timestamp_ms: Long,
    val `interface`: NetworkInterface,
    val internet: NetworkInternet,
    val devices: List<NetworkDevice>,
    val events: List<NetworkEvent>? = null,
    val scan: NetworkScan? = null,
    val public: NetworkPublic? = null,
    val results: List<NetworkResults>? = null
)

object ContractLimits {
    const val MAX_TARGETS = 15
    const val MAX_LUX = 200000.0
    val COMMANDS = listOf("calibrate", "set_thresholds", "restart")
}
