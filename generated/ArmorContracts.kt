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

data class Electrical(
    val kind: String,
    val nodeId: String,
    val timestampMs: Long,
    val switchingEnabled: Boolean? = null,
    val channels: List<ElectricalChannel>
)

object ContractLimits {
    const val MAX_TARGETS = 15
    const val MAX_LUX = 200000.0
    val COMMANDS = listOf("calibrate", "set_thresholds", "restart")
}
