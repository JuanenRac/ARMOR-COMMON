// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_types.py. Do not edit.
package es.electrohobby3d.armor.contracts

data class RadarTrack(
    val sensorId: Long,
    val trackId: Long,
    val xMm: Double,
    val yMm: Double,
    val speedMmS: Double
)

data class Telemetry(
    val nodeId: String,
    val timestampMs: Long,
    val lux: Double,
    val targets: List<RadarTrack>
)

data class Health(
    val nodeId: String,
    val timestampMs: Long,
    val online: Boolean
)

data class Command(
    val nodeId: String,
    val timestampMs: Long,
    val command: String,
    val sensitivity: Long? = null
)

data class Info(
    val nodeId: String,
    val timestampMs: Long,
    val name: String,
    val firmware: String,
    val ip: String,
    val port: Long
)

data class SolarInverter(
    val kind: String,
    val nodeId: String,
    val device: String,
    val timestampMs: Long,
    val mode: String,
    val gridV: Double,
    val gridHz: Double,
    val outV: Double,
    val outHz: Double,
    val outVa: Double,
    val outW: Double,
    val loadPercent: Double,
    val batteryV: Double,
    val batteryA: Double,
    val batteryPercent: Double,
    val pvV: Double,
    val pvA: Double,
    val pvW: Double,
    val heatsinkC: Double,
    val acCharging: Boolean,
    val pvCharging: Boolean,
    val loadOn: Boolean,
    val warnings: List<String>,
    val pv2V: Double? = null,
    val pv2A: Double? = null,
    val pv2W: Double? = null,
    val totalOutW: Double? = null,
    val totalOutVa: Double? = null,
    val totalLoadPercent: Double? = null,
    val totalChargingA: Double? = null,
    val units: List<Any>? = null
)

data class SolarModule(
    val n: Long,
    val present: Boolean,
    val voltageV: Double? = null,
    val currentA: Double? = null,
    val temperatureC: Double? = null,
    val socPercent: Long? = null,
    val state: String? = null,
    val cellsV: List<Double>? = null,
    val temperaturesC: List<Double>? = null,
    val capacityAh: Double? = null,
    val fullCapacityAh: Double? = null,
    val cycles: Long? = null,
    val healthPercent: Long? = null
)

data class SolarBattery(
    val kind: String,
    val nodeId: String,
    val device: String,
    val timestampMs: Long,
    val modules: Long,
    val state: String? = null,
    val voltageV: Double? = null,
    val currentA: Double? = null,
    val temperatureMinC: Double? = null,
    val temperatureMaxC: Double? = null,
    val cellMinV: Double? = null,
    val cellMaxV: Double? = null,
    val socPercent: Long? = null,
    val alarm: Boolean? = null,
    val stack: List<SolarModule>,
    val model: String? = null,
    val capacityAh: Double? = null,
    val fullCapacityAh: Double? = null,
    val energyKwh: Double? = null,
    val cycles: Long? = null,
    val healthPercent: Long? = null
)

data class ElectricalChannel(
    val id: String,
    val domain: String,
    val label: String? = null,
    val voltageV: Double? = null,
    val currentA: Double? = null,
    val powerW: Double? = null,
    val energyKwh: Double? = null,
    val frequencyHz: Double? = null,
    val powerFactor: Double? = null,
    val state: String? = null,
    val alarm: Boolean? = null,
    val alarmCode: String? = null
)

data class ElectricalSwitch(
    val id: String,
    val kind: String,
    val label: String? = null,
    val sourceA: String? = null,
    val sourceB: String? = null,
    val aClosed: Boolean,
    val bClosed: Boolean,
    val selected: String,
    val wanted: String,
    val closing: Boolean,
    val armed: Boolean,
    val fault: String
)

data class Electrical(
    val kind: String,
    val nodeId: String,
    val timestampMs: Long,
    val switchingEnabled: Boolean? = null,
    val channels: List<ElectricalChannel>,
    val switches: List<ElectricalSwitch>? = null
)

data class ElectricalCommand(
    val kind: String,
    val nodeId: String,
    val timestampMs: Long,
    val commandId: String,
    val switch: String,
    val action: String,
    val token: String? = null
)

data class ElectricalResult(
    val kind: String,
    val nodeId: String,
    val timestampMs: Long,
    val commandId: String,
    val switch: String,
    val action: String,
    val accepted: Boolean,
    val refusal: String,
    val token: String? = null
)

data class NetworkInterface(
    val name: String,
    val ip: String,
    val cidr: String,
    val gateway: String? = null,
    val rxBps: Long? = null,
    val txBps: Long? = null
)

data class NetworkProbe(
    val target: String,
    val kind: String,
    val ok: Boolean,
    val latencyMs: Double? = null
)

data class NetworkOutage(
    val startedMs: Long,
    val endedMs: Long,
    val durationS: Long
)

data class NetworkInternet(
    val state: String,
    val sinceMs: Long? = null,
    val gatewayOk: Boolean? = null,
    val latencyMs: Double? = null,
    val lossPercent: Double? = null,
    val probes: List<NetworkProbe>? = null,
    val lastOutage: NetworkOutage? = null,
    val outages24h: Long? = null,
    val downtime24hS: Long? = null
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
    val randomizedMac: Boolean? = null,
    val vendor: String? = null,
    val hostname: String? = null,
    val kind: String? = null,
    val os: String? = null,
    val online: Boolean,
    val firstSeenMs: Long,
    val lastSeenMs: Long,
    val latencyMs: Double? = null,
    val ports: List<NetworkPort>? = null,
    val services: List<String>? = null
)

data class NetworkEvent(
    val id: String,
    val kind: String,
    val atMs: Long,
    val deviceId: String? = null,
    val port: Long? = null,
    val outageS: Long? = null,
    val detail: String? = null
)

data class NetworkScan(
    val lastMs: Long,
    val hosts: Long,
    val durationMs: Long? = null
)

data class Network(
    val kind: String,
    val nodeId: String,
    val timestampMs: Long,
    val interface: NetworkInterface,
    val internet: NetworkInternet,
    val devices: List<NetworkDevice>,
    val events: List<NetworkEvent>? = null,
    val scan: NetworkScan? = null,
    val public: Map<String, Any>? = null,
    val results: List<Any>? = null
)

object ContractLimits {
    const val MAX_TARGETS = 15
    const val MAX_LUX = 200000.0
    val COMMANDS = listOf("calibrate", "set_thresholds", "restart")
}
