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

object ContractLimits {
    const val MAX_TARGETS = 15
    const val MAX_LUX = 200000.0
    val COMMANDS = listOf("calibrate", "set_thresholds", "restart")
}
