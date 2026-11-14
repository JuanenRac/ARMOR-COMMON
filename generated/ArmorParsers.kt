// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_kotlin_parsers.py. Do not edit.
package es.electrohobby3d.armor.contracts

import org.json.JSONArray
import org.json.JSONObject
import java.math.BigInteger

/** What a document gets wrong: where (`/zones/0/id`) and what. */
class ContractError(val path: String, val detail: String) : Exception("${path.ifEmpty { "$" }}: $detail")

private fun isWhole(number: Number): Boolean = when (number) {
    is Int, is Long, is Short, is Byte, is BigInteger -> true
    else -> number.toDouble().let { it.isFinite() && it == Math.floor(it) }
}

private val compiled = HashMap<String, Regex>()
private fun matcher(pattern: String): Regex = synchronized(compiled) { compiled.getOrPut(pattern) { Regex(pattern) } }

private fun typeMatches(value: Any?, type: String): Boolean = when (type) {
    "object" -> value is JSONObject
    "array" -> value is JSONArray
    "string" -> value is String
    "boolean" -> value is Boolean
    "integer" -> value is Number && value.toDouble().isFinite() && isWhole(value)
    "number" -> value is Number && value.toDouble().isFinite()
    else -> false
}

private fun same(a: Any?, b: Any?): Boolean = if (a is Number && b is Number) a.toDouble() == b.toDouble() else a == b

/** The first way in which `value` does not satisfy `schema`, in the order Python's validator finds it, or null. */
private fun firstError(value: Any?, schema: JSONObject, path: String): ContractError? {
    schema.optString("type", "").takeIf { it.isNotEmpty() }?.let { if (!typeMatches(value, it)) return ContractError(path, "must be of type $it") }
    if (schema.has("const") && !same(value, schema.get("const"))) return ContractError(path, "must equal ${schema.get("const")}")
    schema.optJSONArray("enum")?.let { options ->
        if ((0 until options.length()).none { same(value, options.get(it)) }) return ContractError(path, "must be one of $options")
    }
    if (value is String) {
        val length = value.codePointCount(0, value.length)
        if (schema.has("minLength") && length < schema.getInt("minLength")) return ContractError(path, "must have at least ${schema.getInt("minLength")} characters")
        if (schema.has("maxLength") && length > schema.getInt("maxLength")) return ContractError(path, "must have at most ${schema.getInt("maxLength")} characters")
        if (schema.has("pattern") && !matcher(schema.getString("pattern")).containsMatchIn(value)) return ContractError(path, "must match ${schema.getString("pattern")}")
    }
    if (value is Number) {
        val number = value.toDouble()
        if (schema.has("minimum") && number < schema.getDouble("minimum")) return ContractError(path, "must be at least ${schema.get("minimum")}")
        if (schema.has("maximum") && number > schema.getDouble("maximum")) return ContractError(path, "must be at most ${schema.get("maximum")}")
    }
    if (value is JSONArray) {
        if (schema.has("minItems") && value.length() < schema.getInt("minItems")) return ContractError(path, "must have at least ${schema.getInt("minItems")} items")
        if (schema.has("maxItems") && value.length() > schema.getInt("maxItems")) return ContractError(path, "must have at most ${schema.getInt("maxItems")} items")
        schema.optJSONObject("items")?.let { items ->
            for (index in 0 until value.length()) firstError(value.get(index), items, "$path/$index")?.let { return it }
        }
    }
    if (value is JSONObject) {
        val properties = schema.optJSONObject("properties") ?: JSONObject()
        schema.optJSONArray("required")?.let { required ->
            for (index in 0 until required.length()) if (!value.has(required.getString(index))) return ContractError("$path/${required.getString(index)}", "is required")
        }
        val names = value.keys().asSequence().toList()
        if (schema.has("maxProperties") && names.size > schema.getInt("maxProperties")) return ContractError(path, "must have at most ${schema.getInt("maxProperties")} properties")
        schema.optJSONObject("propertyNames")?.let { rule ->
            for (name in names) if (!matcher(rule.getString("pattern")).containsMatchIn(name)) return ContractError("$path/$name", "the name must match ${rule.getString("pattern")}")
        }
        val extra = schema.opt("additionalProperties")
        if (extra == false) {
            for (name in names) if (!properties.has(name)) return ContractError("$path/$name", "is not allowed")
        } else if (extra is JSONObject) {
            for (name in names) if (!properties.has(name)) firstError(value.get(name), extra, "$path/$name")?.let { return it }
        }
        for (name in properties.keys()) if (value.has(name)) firstError(value.get(name), properties.getJSONObject(name), "$path/$name")?.let { return it }
    }
    return null
}

private const val SCHEMA_AI_OBSERVATION = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"camera_id\",\"severity\",\"reasons\",\"profile\",\"motion\",\"radar_tracks\"],\"properties\":{\"camera_id\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._-]{3,80}(?![\\\\s\\\\S])\"},\"severity\":{\"type\":\"string\",\"enum\":[\"review\",\"high\"]},\"reasons\":{\"type\":\"array\",\"maxItems\":5,\"items\":{\"type\":\"string\",\"maxLength\":200}},\"profile\":{\"type\":\"string\",\"enum\":[\"daylight\",\"low-light\"]},\"motion\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1},\"motion_ratio\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1},\"regions\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"x\",\"y\",\"w\",\"h\"],\"properties\":{\"x\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1},\"y\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1},\"w\":{\"type\":\"number\",\"minimum\":0.0001,\"maximum\":1},\"h\":{\"type\":\"number\",\"minimum\":0.0001,\"maximum\":1}}}},\"radar_tracks\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000}}}"
private const val SCHEMA_ALARM = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"phase\",\"mode\",\"siren\",\"locked_out\",\"commands_enabled\",\"zones\",\"open_zones\",\"events\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"alarm\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"phase\":{\"type\":\"string\",\"enum\":[\"disarmed\",\"exit_delay\",\"armed\",\"entry_delay\",\"alarm\"]},\"mode\":{\"type\":\"string\",\"enum\":[\"disarmed\",\"away\",\"stay\"]},\"siren\":{\"type\":\"boolean\"},\"locked_out\":{\"type\":\"boolean\"},\"commands_enabled\":{\"type\":\"boolean\"},\"zones\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"kind\",\"state\",\"bypassed\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":160},\"kind\":{\"type\":\"string\",\"enum\":[\"instant\",\"entry\",\"interior\",\"always\"]},\"state\":{\"type\":\"string\",\"enum\":[\"normal\",\"triggered\",\"tamper\",\"trouble\"]},\"bypassed\":{\"type\":\"boolean\"}}}},\"open_zones\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"}},\"events\":{\"type\":\"array\",\"maxItems\":10,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"ago_s\",\"kind\"],\"properties\":{\"ago_s\":{\"type\":\"integer\",\"minimum\":0},\"kind\":{\"type\":\"string\",\"enum\":[\"armed\",\"exit_delay_started\",\"entry_delay_started\",\"alarm\",\"siren_timed_out\",\"disarmed\",\"bad_pin\",\"locked_out\",\"zone_bypassed\",\"siren_silenced\"]},\"zone\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"}}}},\"arm_profiles\":{\"type\":\"boolean\"},\"profile\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,15}(?![\\\\s\\\\S])\"},\"siren_loop\":{\"type\":\"string\",\"enum\":[\"unknown\",\"ok\",\"open\",\"short\",\"unreadable\"]},\"siren_fault\":{\"type\":\"boolean\"},\"seq\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":9007199254740991},\"sig\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{64}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_ALARM_COMMAND = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"action\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"alarm_command\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"disarm\",\"silence\"]},\"mode\":{\"type\":\"string\",\"enum\":[\"away\",\"stay\"]},\"force\":{\"type\":\"boolean\"},\"profile\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"name\",\"base\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,15}(?![\\\\s\\\\S])\"},\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"base\":{\"type\":\"string\",\"enum\":[\"away\",\"stay\"]},\"exit_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"entry_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"siren\":{\"type\":\"boolean\"},\"notify\":{\"type\":\"string\",\"enum\":[\"urgent\",\"normal\"]},\"zones\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"armed\":{\"type\":\"boolean\"},\"delay\":{\"type\":\"string\",\"enum\":[\"instant\",\"entry\"]}}}}}}}}"
private const val SCHEMA_ALARM_POLICY = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"config_hash\",\"zone_feed\",\"zone_feed_signature\"],\"properties\":{\"config_hash\":{\"type\":\"boolean\"},\"zone_feed\":{\"type\":\"boolean\"},\"zone_feed_signature\":{\"type\":\"boolean\"},\"disarm_pin\":{\"type\":\"string\",\"enum\":[\"never\",\"if_set\",\"always\"]},\"nvs_encryption\":{\"type\":\"string\",\"enum\":[\"secrets\"]}}}"
private const val SCHEMA_ALARM_RESULT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"action\",\"accepted\",\"refusal\",\"phase\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"alarm_result\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"disarm\",\"silence\"]},\"accepted\":{\"type\":\"boolean\"},\"refusal\":{\"type\":\"string\",\"enum\":[\"none\",\"not_disarmed\",\"zones_open\",\"not_armed\",\"bad_pin\",\"locked_out\"]},\"phase\":{\"type\":\"string\",\"enum\":[\"disarmed\",\"exit_delay\",\"armed\",\"entry_delay\",\"alarm\"]}}}"
private const val SCHEMA_ALARM_ZONE_FEED = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"zone\",\"state\",\"battery_low\"],\"properties\":{\"zone\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"state\":{\"type\":\"string\",\"enum\":[\"normal\",\"triggered\",\"tamper\"]},\"battery_low\":{\"type\":\"boolean\"},\"seq\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":9007199254740991},\"sig\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{64}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_ARM_PROFILE = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"name\",\"base\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,15}(?![\\\\s\\\\S])\"},\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"base\":{\"type\":\"string\",\"enum\":[\"away\",\"stay\"]},\"exit_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"entry_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"siren\":{\"type\":\"boolean\"},\"notify\":{\"type\":\"string\",\"enum\":[\"urgent\",\"normal\"]},\"zones\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"armed\":{\"type\":\"boolean\"},\"delay\":{\"type\":\"string\",\"enum\":[\"instant\",\"entry\"]}}}}}}"
private const val SCHEMA_ARMING_MODES = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"modes\"],\"properties\":{\"modes\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"away\",\"home\",\"night\"],\"properties\":{\"away\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"entry\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"string\",\"pattern\":\"^(zone|device|node|camera):[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b]([^\\\\n]{0,62}[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b])?(?![\\\\s\\\\S])\"}},\"exit_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"entry_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300}}},\"home\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"defends\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"string\",\"pattern\":\"^(zone|device|node|camera):[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b]([^\\\\n]{0,62}[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b])?(?![\\\\s\\\\S])\"}},\"entry\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"string\",\"pattern\":\"^(zone|device|node|camera):[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b]([^\\\\n]{0,62}[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b])?(?![\\\\s\\\\S])\"}},\"exit_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"entry_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300}}},\"night\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"defends\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"string\",\"pattern\":\"^(zone|device|node|camera):[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b]([^\\\\n]{0,62}[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b])?(?![\\\\s\\\\S])\"}},\"entry\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"string\",\"pattern\":\"^(zone|device|node|camera):[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b]([^\\\\n]{0,62}[^ \\\\t\\\\n\\\\r\\\\f\\\\x0b])?(?![\\\\s\\\\S])\"}},\"exit_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300},\"entry_delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":300}}}}},\"schedule\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"mode\",\"days\",\"at\"],\"properties\":{\"mode\":{\"type\":\"string\",\"enum\":[\"away\",\"home\",\"night\"]},\"days\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":7,\"items\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":7}},\"at\":{\"type\":\"string\",\"pattern\":\"^([01][0-9]|2[0-3]):[0-5][0-9](?![\\\\s\\\\S])\"}}}},\"panel_map\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"profiles\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"away\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,15}(?![\\\\s\\\\S])\"},\"home\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,15}(?![\\\\s\\\\S])\"},\"night\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,15}(?![\\\\s\\\\S])\"}}},\"only\":{\"type\":\"array\",\"maxItems\":32,\"items\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"}}}}}}"
private const val SCHEMA_COMMAND = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"node_id\",\"timestamp_ms\",\"command\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"command\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command\":{\"type\":\"string\",\"enum\":[\"calibrate\",\"set_thresholds\",\"restart\"]},\"sensitivity\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":10}}}"
private const val SCHEMA_CONNECTION_CLIENT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"kind\",\"first_seen\",\"last_seen\",\"active_sessions\",\"logins_ok\",\"logins_failed\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"kind\":{\"type\":\"string\",\"enum\":[\"studio\",\"android\",\"node\",\"voice\",\"other\"]},\"user\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":60},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"app_version\":{\"type\":\"string\",\"pattern\":\"^[0-9A-Za-z._-]{1,24}(?![\\\\s\\\\S])\"},\"origin\":{\"type\":\"string\",\"enum\":[\"local\",\"remote\"]},\"two_factor\":{\"type\":\"boolean\"},\"first_seen\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"last_seen\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"last_failure\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"active_sessions\":{\"type\":\"integer\",\"minimum\":0},\"logins_ok\":{\"type\":\"integer\",\"minimum\":0},\"logins_failed\":{\"type\":\"integer\",\"minimum\":0},\"ip\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"agent\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":120}}}"
private const val SCHEMA_CONNECTION_EVENT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"at\",\"type\",\"action\",\"client_kind\",\"client_id\"],\"properties\":{\"id\":{\"type\":\"integer\",\"minimum\":1},\"at\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"type\":{\"type\":\"string\",\"const\":\"connection\"},\"action\":{\"type\":\"string\",\"enum\":[\"first_seen\",\"login\",\"login_failed\",\"second_factor_failed\",\"logout\",\"session_ended\",\"session_expired\",\"panel_opened\"]},\"client_kind\":{\"type\":\"string\",\"enum\":[\"studio\",\"android\",\"node\",\"voice\",\"other\"]},\"client_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"user\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":60},\"origin\":{\"type\":\"string\",\"enum\":[\"local\",\"remote\"]},\"two_factor\":{\"type\":\"boolean\"},\"app_version\":{\"type\":\"string\",\"pattern\":\"^[0-9A-Za-z._-]{1,24}(?![\\\\s\\\\S])\"},\"subject\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"ip\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"agent\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":120}}}"
private const val SCHEMA_DAILY_SUMMARY = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"date\",\"language\",\"summary\",\"findings\",\"text\"],\"properties\":{\"date\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\\\\s\\\\S])\"},\"language\":{\"type\":\"string\",\"enum\":[\"en\",\"es\",\"de\",\"fr\",\"it\",\"ja\",\"zh\",\"pt\"]},\"summary\":{\"type\":\"object\",\"required\":[\"schema\",\"totals\",\"by_type\",\"by_zone\",\"by_hour\"],\"properties\":{\"schema\":{\"type\":\"string\",\"const\":\"armor-daily-summary/1\"},\"totals\":{\"type\":\"object\",\"required\":[\"events\",\"alarms\",\"serious_alarms\",\"false_alarms\"],\"properties\":{\"events\":{\"type\":\"integer\",\"minimum\":0},\"alarms\":{\"type\":\"integer\",\"minimum\":0},\"serious_alarms\":{\"type\":\"integer\",\"minimum\":0},\"false_alarms\":{\"type\":\"integer\",\"minimum\":0}}},\"by_type\":{\"type\":\"object\",\"additionalProperties\":{\"type\":\"integer\"}},\"by_zone\":{\"type\":\"object\",\"additionalProperties\":{\"type\":\"integer\"}},\"by_hour\":{\"type\":\"array\",\"minItems\":24,\"maxItems\":24,\"items\":{\"type\":\"integer\",\"minimum\":0}},\"serious_alarms\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"required\":[\"t_s\"],\"properties\":{\"t_s\":{\"type\":\"number\",\"minimum\":0,\"maximum\":86400},\"code\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"zone\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"node\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"sensor\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"severity\":{\"type\":\"string\",\"enum\":[\"info\",\"low\",\"medium\",\"high\",\"critical\"]},\"watts\":{\"type\":\"number\"},\"value\":{\"type\":\"number\"},\"duration_s\":{\"type\":\"number\",\"minimum\":0},\"mean_w\":{\"type\":\"number\"},\"limit_w\":{\"type\":\"number\"}}}},\"nodes_link_lost\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"required\":[\"node\",\"count\",\"total_s\"],\"properties\":{\"node\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"count\":{\"type\":\"integer\",\"minimum\":1},\"total_s\":{\"type\":\"number\",\"minimum\":0}}}},\"outlier_readings\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"required\":[\"t_s\",\"node\",\"sensor\",\"value\",\"median\",\"score\"],\"properties\":{\"t_s\":{\"type\":\"number\",\"minimum\":0,\"maximum\":86400},\"node\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"sensor\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"value\":{\"type\":\"number\"},\"median\":{\"type\":\"number\"},\"score\":{\"type\":\"number\"}}}},\"consumption\":{\"type\":\"object\",\"required\":[\"samples\",\"peaks\"],\"properties\":{\"samples\":{\"type\":\"integer\",\"minimum\":0},\"peaks\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"required\":[\"t_s\"],\"properties\":{\"t_s\":{\"type\":\"number\",\"minimum\":0,\"maximum\":86400},\"code\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"zone\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"node\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"sensor\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"severity\":{\"type\":\"string\",\"enum\":[\"info\",\"low\",\"medium\",\"high\",\"critical\"]},\"watts\":{\"type\":\"number\"},\"value\":{\"type\":\"number\"},\"duration_s\":{\"type\":\"number\",\"minimum\":0},\"mean_w\":{\"type\":\"number\"},\"limit_w\":{\"type\":\"number\"}}}}}}}},\"findings\":{\"type\":\"array\",\"maxItems\":200,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"subject\",\"count\",\"detail\",\"evidence\"],\"properties\":{\"kind\":{\"type\":\"string\",\"enum\":[\"hourly_repeat\",\"intermittent_sensor\",\"intermittent_link\",\"recurrent_false_alarm\",\"anomalous_consumption\"]},\"subject\":{\"type\":\"object\",\"properties\":{\"code\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"zone\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"node\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"}}},\"count\":{\"type\":\"integer\",\"minimum\":0},\"detail\":{\"type\":\"object\",\"properties\":{\"hours\":{\"type\":\"array\",\"items\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":23}},\"tolerance_min\":{\"type\":\"number\"},\"max_gap_s\":{\"type\":\"number\"},\"limit_s\":{\"type\":\"number\"},\"minimum\":{\"type\":\"integer\"},\"window\":{\"type\":\"integer\"},\"sigma\":{\"type\":\"number\"},\"min_ratio\":{\"type\":\"number\"}}},\"evidence\":{\"type\":\"array\",\"maxItems\":20,\"items\":{\"type\":\"object\",\"required\":[\"t_s\"],\"properties\":{\"t_s\":{\"type\":\"number\",\"minimum\":0,\"maximum\":86400},\"code\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"zone\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"node\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"sensor\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?![\\\\s\\\\S])\"},\"severity\":{\"type\":\"string\",\"enum\":[\"info\",\"low\",\"medium\",\"high\",\"critical\"]},\"watts\":{\"type\":\"number\"},\"value\":{\"type\":\"number\"},\"duration_s\":{\"type\":\"number\",\"minimum\":0},\"mean_w\":{\"type\":\"number\"},\"limit_w\":{\"type\":\"number\"}}}}}}},\"text\":{\"type\":\"string\",\"maxLength\":20000},\"ai_note\":{\"type\":\"string\",\"maxLength\":2000}}}"
private const val SCHEMA_DEVICE_STATE = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"on\"],\"properties\":{\"on\":{\"type\":\"boolean\"}}}"
private const val SCHEMA_DIAGNOSTIC_TOKEN_CREATED = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"token\",\"scope\",\"nodes\",\"created_at\",\"expires_at\",\"created_by\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-f0-9]{12}(?![\\\\s\\\\S])\"},\"token\":{\"type\":\"string\",\"pattern\":\"^armor-diag-[A-Za-z0-9_-]{43}(?![\\\\s\\\\S])\"},\"scope\":{\"type\":\"string\",\"const\":\"read_only\"},\"nodes\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":16,\"items\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"}},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":48},\"created_at\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]{8,12}Z(?![\\\\s\\\\S])\"},\"expires_at\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]{8,12}Z(?![\\\\s\\\\S])\"},\"created_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_DIAGNOSTIC_TOKEN_INFO = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"scope\",\"nodes\",\"created_at\",\"expires_at\",\"created_by\",\"status\",\"uses\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-f0-9]{12}(?![\\\\s\\\\S])\"},\"scope\":{\"type\":\"string\",\"const\":\"read_only\"},\"nodes\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":16,\"items\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"}},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":48},\"created_at\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]{8,12}Z(?![\\\\s\\\\S])\"},\"expires_at\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]{8,12}Z(?![\\\\s\\\\S])\"},\"created_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"},\"status\":{\"type\":\"string\",\"enum\":[\"active\",\"expired\",\"revoked\"]},\"revoked_at\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]{8,12}Z(?![\\\\s\\\\S])\"},\"revoked_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"},\"uses\":{\"type\":\"integer\",\"minimum\":0},\"last_used_at\":{\"type\":\"string\",\"pattern\":\"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]{8,12}Z(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_DIAGNOSTIC_TOKEN_REQUEST = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"nodes\"],\"properties\":{\"nodes\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":16,\"items\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"}},\"ttl_s\":{\"type\":\"integer\",\"minimum\":300,\"maximum\":86400},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":48}}}"
private const val SCHEMA_ELECTRICAL = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"channels\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"electrical\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"switching_enabled\":{\"type\":\"boolean\"},\"channels\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"domain\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"domain\":{\"type\":\"string\",\"enum\":[\"ac\",\"dc\"]},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"voltage_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"current_a\":{\"type\":\"number\",\"minimum\":-1000,\"maximum\":1000},\"power_w\":{\"type\":\"number\",\"minimum\":-1000000,\"maximum\":1000000},\"energy_kwh\":{\"type\":\"number\",\"minimum\":0,\"maximum\":10000000},\"reading_age_ms\":{\"type\":\"integer\",\"minimum\":0},\"errors\":{\"type\":\"integer\",\"minimum\":0},\"power_estimated\":{\"type\":\"boolean\"},\"frequency_hz\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"power_factor\":{\"type\":\"number\",\"minimum\":-1,\"maximum\":1},\"state\":{\"type\":\"string\",\"enum\":[\"closed\",\"open\",\"unknown\"]},\"alarm\":{\"type\":\"boolean\"},\"alarm_code\":{\"type\":\"string\",\"pattern\":\"^[a-z][a-z0-9_]{0,39}(?![\\\\s\\\\S])\"}}}},\"switches\":{\"type\":\"array\",\"maxItems\":4,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"kind\",\"a_closed\",\"b_closed\",\"selected\",\"wanted\",\"closing\",\"armed\",\"fault\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"kind\":{\"type\":\"string\",\"const\":\"transfer\"},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"source_a\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"source_b\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"a_closed\":{\"type\":\"boolean\"},\"b_closed\":{\"type\":\"boolean\"},\"selected\":{\"type\":\"string\",\"enum\":[\"none\",\"a\",\"b\"]},\"wanted\":{\"type\":\"string\",\"enum\":[\"none\",\"a\",\"b\"]},\"closing\":{\"type\":\"boolean\"},\"armed\":{\"type\":\"boolean\"},\"fault\":{\"type\":\"string\",\"enum\":[\"none\",\"did_not_close\",\"did_not_open\",\"both_closed\",\"disabled\"]}}}}}}"
private const val SCHEMA_ELECTRICAL_COMMAND = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"switch\",\"action\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"electrical_command\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"switch\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"close_a\",\"close_b\",\"open\",\"acknowledge\"]},\"token\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9]{8,32}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_ELECTRICAL_RESULT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"switch\",\"action\",\"accepted\",\"refusal\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"electrical_result\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"switch\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"close_a\",\"close_b\",\"open\",\"acknowledge\"]},\"accepted\":{\"type\":\"boolean\"},\"refusal\":{\"type\":\"string\",\"enum\":[\"none\",\"disabled\",\"fault\",\"not_armed\",\"not_confirmed_open\",\"unknown_switch\",\"bad_token\",\"not_supported\"]},\"token\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9]{8,32}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_HEALTH = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"node_id\",\"timestamp_ms\",\"online\"],\"properties\":{\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"online\":{\"type\":\"boolean\"},\"kind\":{\"type\":\"string\",\"enum\":[\"radar\",\"panel\"]}}}"
private const val SCHEMA_HEATMAP = "{\"type\":\"object\",\"required\":[\"schema\",\"camera_id\",\"cols\",\"rows\",\"accepted_positions\",\"rejected_positions\",\"total\",\"max\",\"weights\",\"normalized\",\"contains_images\"],\"properties\":{\"schema\":{\"type\":\"string\",\"const\":\"armor.vision.heatmap/v1\"},\"camera_id\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._-]{1,80}(?![\\\\s\\\\S])\"},\"cols\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65536},\"rows\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65536},\"accepted_positions\":{\"type\":\"integer\",\"minimum\":0},\"rejected_positions\":{\"type\":\"integer\",\"minimum\":0},\"total\":{\"type\":\"number\",\"minimum\":0},\"max\":{\"type\":\"number\",\"minimum\":0},\"weights\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":65536,\"items\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":65536,\"items\":{\"type\":\"number\",\"minimum\":0}}},\"normalized\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":65536,\"items\":{\"type\":\"array\",\"minItems\":1,\"maxItems\":65536,\"items\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1}}},\"contains_images\":{\"type\":\"boolean\",\"const\":false}}}"
private const val SCHEMA_INFO = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"node_id\",\"timestamp_ms\",\"name\",\"firmware\",\"ip\",\"port\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"info\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":48},\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"ip\":{\"type\":\"string\",\"pattern\":\"^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\\\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}(?![\\\\s\\\\S])\"},\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65535},\"contract\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_NETWORK = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"interface\",\"internet\",\"devices\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"network\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"contract\":{\"type\":\"integer\",\"minimum\":1},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"interface\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"name\",\"ip\",\"cidr\"],\"properties\":{\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"ip\":{\"type\":\"string\",\"pattern\":\"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?![\\\\s\\\\S])\"},\"cidr\":{\"type\":\"string\",\"pattern\":\"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])/(?:3[0-2]|[12]?[0-9])(?![\\\\s\\\\S])\"},\"gateway\":{\"type\":\"string\",\"pattern\":\"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?![\\\\s\\\\S])\"},\"rx_bps\":{\"type\":\"integer\",\"minimum\":0},\"tx_bps\":{\"type\":\"integer\",\"minimum\":0}}},\"internet\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"state\"],\"properties\":{\"state\":{\"type\":\"string\",\"enum\":[\"up\",\"degraded\",\"down\",\"lan_down\",\"unknown\"]},\"since_ms\":{\"type\":\"integer\",\"minimum\":0},\"gateway_ok\":{\"type\":\"boolean\"},\"latency_ms\":{\"type\":\"number\",\"minimum\":0,\"maximum\":60000},\"loss_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"probes\":{\"type\":\"array\",\"maxItems\":8,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"target\",\"kind\",\"ok\"],\"properties\":{\"target\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"kind\":{\"type\":\"string\",\"enum\":[\"icmp\",\"tcp\",\"dns\",\"http\"]},\"ok\":{\"type\":\"boolean\"},\"latency_ms\":{\"type\":\"number\",\"minimum\":0,\"maximum\":60000}}}},\"last_outage\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"started_ms\",\"ended_ms\",\"duration_s\"],\"properties\":{\"started_ms\":{\"type\":\"integer\",\"minimum\":0},\"ended_ms\":{\"type\":\"integer\",\"minimum\":0},\"duration_s\":{\"type\":\"integer\",\"minimum\":0}}},\"outages_24h\":{\"type\":\"integer\",\"minimum\":0},\"downtime_24h_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":86400}}},\"devices\":{\"type\":\"array\",\"maxItems\":512,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"ip\",\"online\",\"first_seen_ms\",\"last_seen_ms\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9:._-]{0,63}(?![\\\\s\\\\S])\"},\"ip\":{\"type\":\"string\",\"pattern\":\"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?![\\\\s\\\\S])\"},\"mac\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{2}(:[0-9a-f]{2}){5}(?![\\\\s\\\\S])\"},\"randomized_mac\":{\"type\":\"boolean\"},\"vendor\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"hostname\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"kind\":{\"type\":\"string\",\"enum\":[\"router\",\"computer\",\"phone\",\"tv\",\"printer\",\"camera\",\"iot\",\"server\",\"nas\",\"network\",\"unknown\"]},\"os\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"online\":{\"type\":\"boolean\"},\"first_seen_ms\":{\"type\":\"integer\",\"minimum\":0},\"last_seen_ms\":{\"type\":\"integer\",\"minimum\":0},\"latency_ms\":{\"type\":\"number\",\"minimum\":0,\"maximum\":60000},\"ports\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"port\",\"proto\"],\"properties\":{\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65535},\"proto\":{\"type\":\"string\",\"enum\":[\"tcp\",\"udp\"]},\"service\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"banner\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80}}}},\"services\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":48}}}}},\"events\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"kind\",\"at_ms\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"kind\":{\"type\":\"string\",\"enum\":[\"new_device\",\"device_online\",\"device_offline\",\"ip_changed\",\"arp_conflict\",\"port_opened\",\"port_closed\",\"internet_down\",\"internet_up\",\"gateway_down\",\"gateway_up\",\"risky_port\",\"rogue_dhcp\"]},\"at_ms\":{\"type\":\"integer\",\"minimum\":0},\"device_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9:._-]{0,63}(?![\\\\s\\\\S])\"},\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65535},\"outage_s\":{\"type\":\"integer\",\"minimum\":0},\"server\":{\"type\":\"string\",\"pattern\":\"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?![\\\\s\\\\S])\"},\"recommendation\":{\"type\":\"string\",\"pattern\":\"^[a-z][a-z0-9_]{0,31}(?![\\\\s\\\\S])\"},\"detail\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":120}}}},\"scan\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"last_ms\",\"hosts\"],\"properties\":{\"last_ms\":{\"type\":\"integer\",\"minimum\":0},\"hosts\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1024},\"duration_ms\":{\"type\":\"integer\",\"minimum\":0}}},\"public\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"ip\",\"checked_ms\"],\"properties\":{\"ip\":{\"type\":\"string\",\"maxLength\":45},\"hostname\":{\"type\":\"string\",\"maxLength\":128},\"city\":{\"type\":\"string\",\"maxLength\":64},\"region\":{\"type\":\"string\",\"maxLength\":64},\"country\":{\"type\":\"string\",\"maxLength\":64},\"org\":{\"type\":\"string\",\"maxLength\":128},\"timezone\":{\"type\":\"string\",\"maxLength\":64},\"checked_ms\":{\"type\":\"integer\",\"minimum\":0},\"changed_ms\":{\"type\":\"integer\",\"minimum\":0},\"dns\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"name\",\"addresses\",\"matches\"],\"properties\":{\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":253},\"addresses\":{\"type\":\"array\",\"maxItems\":8,\"items\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":45}},\"matches\":{\"type\":\"boolean\"}}}}},\"results\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"type\",\"ok\",\"finished_ms\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"type\":{\"type\":\"string\",\"enum\":[\"scan_now\",\"ping\",\"traceroute\",\"wake\",\"ports\",\"http\",\"inspect\"]},\"ok\":{\"type\":\"boolean\"},\"finished_ms\":{\"type\":\"integer\",\"minimum\":0},\"device_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9:._-]{0,63}(?![\\\\s\\\\S])\"},\"output\":{\"type\":\"string\",\"maxLength\":2000},\"ports\":{\"type\":\"array\",\"maxItems\":64,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"port\",\"proto\"],\"properties\":{\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65535},\"proto\":{\"type\":\"string\",\"enum\":[\"tcp\",\"udp\"]},\"service\":{\"type\":\"string\",\"maxLength\":32},\"banner\":{\"type\":\"string\",\"maxLength\":80}}}},\"latency_ms\":{\"type\":\"number\",\"minimum\":0}}}}}}"
private const val SCHEMA_NETWORK_ORDERS = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"accepted\",\"commands\"],\"properties\":{\"accepted\":{\"type\":\"boolean\",\"const\":true},\"commands\":{\"type\":\"array\",\"maxItems\":4,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"type\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"type\":{\"type\":\"string\",\"enum\":[\"scan_now\",\"ping\",\"traceroute\",\"wake\",\"ports\",\"http\",\"inspect\"]},\"device_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"ip\":{\"type\":\"string\",\"pattern\":\"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?![\\\\s\\\\S])\"},\"mac\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{2}(:[0-9a-f]{2}){5}(?![\\\\s\\\\S])\"},\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":65535},\"auth_sealed\":{\"type\":\"string\",\"minLength\":64,\"maxLength\":2048,\"pattern\":\"^[A-Za-z0-9+/]+={0,2}(?![\\\\s\\\\S])\"}}}}}}"
private const val SCHEMA_NODE_CONTROL_COMMAND = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"action\",\"operation\",\"mode\",\"requested_by\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"node_control_command\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"execute\"]},\"operation\":{\"type\":\"string\",\"enum\":[\"restart\",\"pause\",\"resume\",\"standby\",\"identify\",\"diagnostics\",\"maintenance_on\",\"maintenance_off\"]},\"mode\":{\"type\":\"string\",\"enum\":[\"now\",\"rolling\"]},\"delay_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":600},\"slot\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":63},\"duration_s\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":86400},\"token\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9]{16,32}(?![\\\\s\\\\S])\"},\"requested_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"},\"detail\":{\"type\":\"string\",\"enum\":[\"package\",\"log\"]}}}"
private const val SCHEMA_NODE_CONTROL_RESULT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"action\",\"operation\",\"stage\",\"accepted\",\"refusal\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"node_control_result\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"execute\"]},\"operation\":{\"type\":\"string\",\"enum\":[\"restart\",\"pause\",\"resume\",\"standby\",\"identify\",\"diagnostics\",\"maintenance_on\",\"maintenance_off\"]},\"stage\":{\"type\":\"string\",\"enum\":[\"armed\",\"restarting\",\"applied\",\"diagnostics\",\"rejected\"]},\"accepted\":{\"type\":\"boolean\"},\"refusal\":{\"type\":\"string\",\"enum\":[\"none\",\"not_armed\",\"invalid_token\",\"token_expired\",\"rate_limited\",\"already_restarting\",\"already_in_state\",\"busy_update\",\"busy_upload\",\"busy_slot_copy\",\"busy_battery\",\"unavailable\"]},\"token\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9]{16,32}(?![\\\\s\\\\S])\"},\"token_ttl_s\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":120},\"reason\":{\"type\":\"string\",\"enum\":[\"requested_by_server\"]},\"mode\":{\"type\":\"string\",\"enum\":[\"now\",\"rolling\"]},\"restart_in_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":3600},\"uptime_s\":{\"type\":\"integer\",\"minimum\":0},\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"requested_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"},\"state\":{\"type\":\"string\",\"enum\":[\"running\",\"paused\",\"standby\"]},\"maintenance\":{\"type\":\"boolean\"},\"until_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":86400},\"since_ms\":{\"type\":\"integer\",\"minimum\":0},\"diagnostics\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"firmware\",\"uptime_s\",\"reset_reason\",\"heap_free\",\"heap_min\",\"mqtt_connected\",\"state\",\"maintenance\"],\"properties\":{\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"uptime_s\":{\"type\":\"integer\",\"minimum\":0},\"reset_reason\":{\"type\":\"string\",\"enum\":[\"power_on\",\"external\",\"software\",\"panic\",\"int_wdt\",\"task_wdt\",\"other_wdt\",\"deep_sleep\",\"brownout\",\"sdio\",\"usb\",\"jtag\",\"efuse\",\"power_glitch\",\"cpu_lockup\",\"unknown\"]},\"heap_free\":{\"type\":\"integer\",\"minimum\":0},\"heap_min\":{\"type\":\"integer\",\"minimum\":0},\"psram_free\":{\"type\":\"integer\",\"minimum\":0},\"stack_min_free\":{\"type\":\"integer\",\"minimum\":0},\"rssi\":{\"type\":\"integer\",\"minimum\":-120,\"maximum\":0},\"mqtt_connected\":{\"type\":\"boolean\"},\"state\":{\"type\":\"string\",\"enum\":[\"running\",\"paused\",\"standby\"]},\"maintenance\":{\"type\":\"boolean\"},\"package\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"detail\",\"log\",\"truncated\"],\"properties\":{\"detail\":{\"type\":\"string\",\"enum\":[\"package\",\"log\"]},\"heap\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"internal_free\",\"internal_min\",\"internal_largest\",\"total_free\",\"total_min\"],\"properties\":{\"internal_free\":{\"type\":\"integer\",\"minimum\":0},\"internal_min\":{\"type\":\"integer\",\"minimum\":0},\"internal_largest\":{\"type\":\"integer\",\"minimum\":0},\"total_free\":{\"type\":\"integer\",\"minimum\":0},\"total_min\":{\"type\":\"integer\",\"minimum\":0},\"psram_free\":{\"type\":\"integer\",\"minimum\":0}}},\"tasks\":{\"type\":\"array\",\"maxItems\":40,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"name\",\"stack_free\",\"priority\",\"state\"],\"properties\":{\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":15},\"stack_free\":{\"type\":\"integer\",\"minimum\":0},\"priority\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":63},\"state\":{\"type\":\"string\",\"enum\":[\"R\",\"r\",\"B\",\"S\",\"D\",\"?\"]}}}},\"resets\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"reason\",\"uptime_s\",\"guard_restarts_in_hour\"],\"properties\":{\"reason\":{\"type\":\"string\",\"enum\":[\"power_on\",\"external\",\"software\",\"panic\",\"int_wdt\",\"task_wdt\",\"other_wdt\",\"deep_sleep\",\"brownout\",\"sdio\",\"usb\",\"jtag\",\"efuse\",\"power_glitch\",\"cpu_lockup\",\"unknown\"]},\"uptime_s\":{\"type\":\"integer\",\"minimum\":0},\"guard_restarts_in_hour\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":3}}},\"boot\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"cause\",\"reset_reason\",\"coredump\",\"deliberate\",\"guard\"],\"properties\":{\"cause\":{\"type\":\"string\",\"enum\":[\"panic\",\"task_watchdog\",\"interrupt_watchdog\",\"other_watchdog\",\"brownout\",\"power_glitch\",\"cpu_lockup\",\"out_of_memory\",\"guard_missing_task\",\"guard_low_memory\",\"guard_dead_man\",\"guard\"]},\"reset_reason\":{\"type\":\"string\",\"enum\":[\"power_on\",\"external\",\"software\",\"panic\",\"int_wdt\",\"task_wdt\",\"other_wdt\",\"deep_sleep\",\"brownout\",\"sdio\",\"usb\",\"jtag\",\"efuse\",\"power_glitch\",\"cpu_lockup\",\"unknown\"]},\"uptime_before_s\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_free\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_largest\":{\"type\":\"integer\",\"minimum\":0},\"coredump\":{\"type\":\"boolean\"},\"deliberate\":{\"type\":\"boolean\"},\"guard\":{\"type\":\"boolean\"}}},\"memory_gate\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"closed\",\"transitions\",\"close_free\",\"close_block\",\"open_free\",\"open_block\"],\"properties\":{\"closed\":{\"type\":\"boolean\"},\"transitions\":{\"type\":\"integer\",\"minimum\":0},\"close_free\":{\"type\":\"integer\",\"minimum\":0},\"close_block\":{\"type\":\"integer\",\"minimum\":0},\"open_free\":{\"type\":\"integer\",\"minimum\":0},\"open_block\":{\"type\":\"integer\",\"minimum\":0}}},\"versions\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"firmware\",\"idf\",\"sensors\"],\"properties\":{\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"idf\":{\"type\":\"string\",\"maxLength\":32},\"board\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"sensors\":{\"type\":\"array\",\"maxItems\":8,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"name\",\"version\"],\"properties\":{\"name\":{\"type\":\"string\",\"maxLength\":32},\"version\":{\"type\":\"string\",\"maxLength\":32}}}}}},\"config\":{\"type\":\"object\",\"maxProperties\":64,\"additionalProperties\":{\"type\":\"string\",\"maxLength\":96}},\"coredump\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"present\"],\"properties\":{\"present\":{\"type\":\"boolean\"},\"size\":{\"type\":\"integer\",\"minimum\":1},\"summary\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"task\"],\"properties\":{\"task\":{\"type\":\"string\",\"maxLength\":16},\"reason\":{\"type\":\"string\",\"maxLength\":96},\"pc\":{\"type\":\"string\",\"pattern\":\"^0x[0-9a-fA-F]{1,16}(?![\\\\s\\\\S])\"},\"backtrace\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"string\",\"pattern\":\"^0x[0-9a-fA-F]{1,16}(?![\\\\s\\\\S])\"}},\"app_sha256\":{\"type\":\"string\",\"maxLength\":16}}}}},\"log\":{\"type\":\"string\",\"maxLength\":6000},\"truncated\":{\"type\":\"boolean\"}}}}}}}"
private const val SCHEMA_NODE_HEALTH = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"family\",\"firmware\",\"uptime_s\",\"reset_reason\",\"heap_free\",\"heap_min\",\"link\",\"link_up\",\"broker_reconnects\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"node_health\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"family\":{\"type\":\"string\",\"enum\":[\"radar\",\"solar\",\"electrical\",\"alarm\",\"hmi\"]},\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"contract\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"board\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"uptime_s\":{\"type\":\"integer\",\"minimum\":0},\"reset_reason\":{\"type\":\"string\",\"enum\":[\"power_on\",\"external\",\"software\",\"panic\",\"int_wdt\",\"task_wdt\",\"other_wdt\",\"deep_sleep\",\"brownout\",\"sdio\",\"usb\",\"jtag\",\"efuse\",\"power_glitch\",\"cpu_lockup\",\"unknown\"]},\"heap_free\":{\"type\":\"integer\",\"minimum\":0},\"heap_min\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_free\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_min\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_largest\":{\"type\":\"integer\",\"minimum\":0},\"psram_free\":{\"type\":\"integer\",\"minimum\":0},\"link\":{\"type\":\"string\",\"enum\":[\"wifi\",\"ethernet\",\"none\"]},\"link_up\":{\"type\":\"boolean\"},\"rssi_dbm\":{\"type\":\"integer\",\"minimum\":-120,\"maximum\":0},\"broker_reconnects\":{\"type\":\"integer\",\"minimum\":0},\"low_stack_tasks\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":64},\"stack_min_free\":{\"type\":\"integer\",\"minimum\":0},\"stack_min_task\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":32},\"last_error\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":96},\"control_state\":{\"type\":\"string\",\"enum\":[\"running\",\"paused\",\"standby\"]},\"control_since_ms\":{\"type\":\"integer\",\"minimum\":0},\"control_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"},\"control_until_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":86400},\"maintenance\":{\"type\":\"boolean\"},\"maintenance_until_s\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":86400},\"boot\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"cause\",\"reset_reason\",\"coredump\",\"deliberate\",\"guard\"],\"properties\":{\"cause\":{\"type\":\"string\",\"enum\":[\"panic\",\"task_watchdog\",\"interrupt_watchdog\",\"other_watchdog\",\"brownout\",\"power_glitch\",\"cpu_lockup\",\"out_of_memory\",\"guard_missing_task\",\"guard_low_memory\",\"guard_dead_man\",\"guard\"]},\"reset_reason\":{\"type\":\"string\",\"enum\":[\"power_on\",\"external\",\"software\",\"panic\",\"int_wdt\",\"task_wdt\",\"other_wdt\",\"deep_sleep\",\"brownout\",\"sdio\",\"usb\",\"jtag\",\"efuse\",\"power_glitch\",\"cpu_lockup\",\"unknown\"]},\"uptime_before_s\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_free\":{\"type\":\"integer\",\"minimum\":0},\"heap_internal_largest\":{\"type\":\"integer\",\"minimum\":0},\"coredump\":{\"type\":\"boolean\"},\"deliberate\":{\"type\":\"boolean\"},\"guard\":{\"type\":\"boolean\"}}},\"memory_gate\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"closed\",\"transitions\",\"close_free\",\"close_block\",\"open_free\",\"open_block\"],\"properties\":{\"closed\":{\"type\":\"boolean\"},\"transitions\":{\"type\":\"integer\",\"minimum\":0},\"close_free\":{\"type\":\"integer\",\"minimum\":0},\"close_block\":{\"type\":\"integer\",\"minimum\":0},\"open_free\":{\"type\":\"integer\",\"minimum\":0},\"open_block\":{\"type\":\"integer\",\"minimum\":0}}},\"coredump\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"present\"],\"properties\":{\"present\":{\"type\":\"boolean\"},\"size\":{\"type\":\"integer\",\"minimum\":1}}},\"config_check\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"snapshot\":{\"type\":\"string\",\"enum\":[\"restored\",\"failed\"]},\"reverted\":{\"type\":\"string\",\"enum\":[\"reapplied\",\"failed\"]}}},\"sensors\":{\"type\":\"array\",\"maxItems\":3,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"sensor_id\",\"model\",\"state\",\"firmware_known\",\"bluetooth\"],\"properties\":{\"sensor_id\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":3},\"model\":{\"type\":\"string\",\"enum\":[\"ld2450\",\"ld2461\",\"ld2410\",\"ld2412\",\"ld2410s\",\"mr24hpc1\"]},\"state\":{\"type\":\"string\",\"enum\":[\"reporting\",\"no_data\",\"garbled\",\"silent\",\"bridge\"]},\"firmware_known\":{\"type\":\"boolean\"},\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9A-Za-z._:-]{1,24}(?![\\\\s\\\\S])\"},\"bluetooth\":{\"type\":\"string\",\"enum\":[\"unknown\",\"open\",\"closed\",\"none\"]},\"mac\":{\"type\":\"string\",\"pattern\":\"^[0-9A-Za-z:._-]{1,17}(?![\\\\s\\\\S])\"},\"bluetooth_alert\":{\"type\":\"boolean\"},\"quirk\":{\"type\":\"string\",\"enum\":[\"ld2412_bad_firmware\",\"ld2412_unknown_firmware\"]}}}},\"radar\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"perimeter_enabled\",\"masked\",\"wifi_jam\",\"bridge_open\",\"events_buffered\",\"sensor_bluetooth_off\"],\"properties\":{\"perimeter_enabled\":{\"type\":\"boolean\"},\"masked\":{\"type\":\"boolean\"},\"wifi_jam\":{\"type\":\"boolean\"},\"bridge_open\":{\"type\":\"boolean\"},\"events_buffered\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000},\"sensor_bluetooth_off\":{\"type\":\"boolean\"}}}}}"
private const val SCHEMA_NODE_MAINTENANCE = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"active\",\"reason\",\"firmware\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"node_maintenance\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"active\":{\"type\":\"boolean\"},\"reason\":{\"type\":\"string\",\"enum\":[\"restart\",\"pause\",\"standby\",\"update\",\"upload\",\"operator\"]},\"expected_s\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":3600},\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9]+[.][0-9]+[.][0-9]+([.][0-9]+)?(?![\\\\s\\\\S])\"},\"requested_by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._@ -]{1,64}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_RADAR_EVENT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"boot\",\"seq\",\"event\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"radar_event\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"boot\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":4294967295},\"seq\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":4294967295},\"event\":{\"type\":\"string\",\"enum\":[\"zone_occupied\",\"zone_clear\",\"loiter\",\"tripwire\",\"path_violation\",\"masking\",\"masking_end\",\"sensor_bluetooth_open\",\"sensor_bluetooth_closed\",\"wifi_jam\",\"wifi_jam_end\",\"bridge_opened\",\"bridge_closed\"]},\"name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24},\"sensor_id\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":3},\"track_id\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":255},\"movement\":{\"type\":\"string\",\"enum\":[\"still\",\"walking\",\"running\"]},\"value\":{\"type\":\"integer\",\"minimum\":0},\"count\":{\"type\":\"integer\",\"minimum\":0},\"direction\":{\"type\":\"string\",\"enum\":[\"in\",\"out\"]},\"from\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24},\"by\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._-]{1,32}(?![\\\\s\\\\S])\"}}}"
private const val SCHEMA_SERVER_ALERT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"service\",\"event\",\"at\",\"mode\"],\"properties\":{\"service\":{\"type\":\"string\",\"const\":\"armor-server\"},\"event\":{\"type\":\"string\",\"enum\":[\"alert.raised\",\"alert.cleared\",\"node.offline\",\"node.stale\",\"camera.offline\",\"alarm.raised\",\"alarm.escalated\",\"automation.notify\",\"login.remote\",\"alert.test\"]},\"at\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"mode\":{\"type\":\"string\",\"enum\":[\"armed\",\"disarmed\"]},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"camera_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"targets\":{\"type\":\"integer\",\"minimum\":0},\"minutes\":{\"type\":\"integer\",\"minimum\":0},\"alarm_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"severity\":{\"type\":\"string\",\"enum\":[\"critical\",\"high\",\"warning\"]},\"code\":{\"type\":\"string\",\"pattern\":\"^[a-z][a-z0-9_]{0,63}(?![\\\\s\\\\S])\"},\"device_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"solar_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"electrical_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"alarm_node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"network_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"silent\":{\"type\":\"boolean\",\"const\":true},\"automation\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"login_user\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"login_from\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":64},\"login_country\":{\"type\":\"string\",\"pattern\":\"^[A-Z]{2}(?![\\\\s\\\\S])\"},\"login_country_new\":{\"type\":\"boolean\",\"const\":true}}}"
private const val SCHEMA_SOLAR_BATTERY = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"device\",\"timestamp_ms\",\"modules\",\"stack\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"battery\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"device\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"modules\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":16},\"state\":{\"type\":\"string\",\"enum\":[\"charging\",\"discharging\",\"idle\"]},\"voltage_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"current_a\":{\"type\":\"number\",\"minimum\":-1000,\"maximum\":1000},\"temperature_min_c\":{\"type\":\"number\",\"minimum\":-50,\"maximum\":200},\"temperature_max_c\":{\"type\":\"number\",\"minimum\":-50,\"maximum\":200},\"cell_min_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":10},\"cell_max_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":10},\"soc_percent\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":100},\"alarm\":{\"type\":\"boolean\"},\"stack\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"n\",\"present\"],\"properties\":{\"n\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":16},\"present\":{\"type\":\"boolean\"},\"voltage_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"current_a\":{\"type\":\"number\",\"minimum\":-1000,\"maximum\":1000},\"temperature_c\":{\"type\":\"number\",\"minimum\":-50,\"maximum\":200},\"soc_percent\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":100},\"state\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":16},\"cells_v\":{\"type\":\"array\",\"maxItems\":32,\"items\":{\"type\":\"number\",\"minimum\":0,\"maximum\":10}},\"counters\":{\"type\":\"object\",\"maxProperties\":48,\"propertyNames\":{\"pattern\":\"^[a-z][a-z0-9_]{0,31}(?![\\\\s\\\\S])\"},\"additionalProperties\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":9999999999}},\"temperatures_c\":{\"type\":\"array\",\"maxItems\":8,\"items\":{\"type\":\"number\",\"minimum\":-50,\"maximum\":200}},\"capacity_ah\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"full_capacity_ah\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"cycles\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000000},\"health_percent\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":100},\"model\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24},\"cell_count\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":32},\"max_charge_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"max_discharge_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"console_baud\":{\"type\":\"integer\",\"minimum\":300,\"maximum\":1000000},\"soh_counts\":{\"type\":\"array\",\"maxItems\":32,\"items\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000000}},\"soh_abnormal\":{\"type\":\"array\",\"maxItems\":32,\"items\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":31}},\"last_event\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"index\",\"time\"],\"properties\":{\"index\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000000},\"time\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"voltage_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"current_a\":{\"type\":\"number\",\"minimum\":-1000,\"maximum\":1000},\"temperature_c\":{\"type\":\"number\",\"minimum\":-50,\"maximum\":200},\"percent\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":100},\"base_state\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"voltage_state\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"current_state\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"temperature_state\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"coulomb_state\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"power_events\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"battery_events\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"system_fault\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40}}},\"board_version\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24},\"main_soft_version\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24},\"soft_version\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24}}}},\"model\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":24},\"capacity_ah\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"full_capacity_ah\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"energy_kwh\":{\"type\":\"number\",\"minimum\":0,\"maximum\":10000},\"cycles\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000000},\"health_percent\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":100},\"power_w\":{\"type\":\"number\",\"minimum\":-1000000,\"maximum\":1000000},\"balancing\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":64},\"protecting\":{\"type\":\"boolean\"},\"charge_mos\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":255},\"discharge_mos\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":255}}}"
private const val SCHEMA_SOLAR_BATTERY_COMMAND = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"port\",\"action\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"solar_battery_command\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":10},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"execute\",\"cancel\",\"stage\"]},\"op\":{\"type\":\"string\",\"enum\":[\"set_clock\",\"clear_stats\",\"clear_log\",\"clear_data\",\"restart\",\"shutdown\",\"soc_capacity\",\"mosfail_test\",\"soc_reset\",\"pcb_setup\",\"limits_set\",\"limits_default\",\"protections_set\",\"protections_default\",\"output_set\",\"fault_clear\",\"write_barcode\",\"eeprom_erase\",\"firmware_update\",\"expert_command\"]},\"params\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"which\":{\"type\":\"string\",\"enum\":[\"event\",\"history\"]},\"group\":{\"type\":\"string\",\"enum\":[\"module_voltage\",\"cell_voltage\",\"temperature\"]},\"values\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"pov\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"povr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"phv\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"phvr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"plv\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"plvr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"puv\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"puvr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"pslp\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"bov\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"bovr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"bhv\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"bhvr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"blv\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"blvr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"buv\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"buvr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"bslp\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"cot\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"cotr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"cht\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"chtr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"clt\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"cltr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"cut\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000},\"cutr\":{\"type\":\"integer\",\"minimum\":-40000,\"maximum\":100000}}},\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"bov\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"bhv\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"blv\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"buv\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"bslp\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"pov\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"phv\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"plv\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"puv\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"pslp\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"coc\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"coc2\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"doc\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]},\"doc2\":{\"type\":\"string\",\"enum\":[\"en\",\"dis\"]}}},\"accept_risk\":{\"type\":\"boolean\"},\"output\":{\"type\":\"string\",\"enum\":[\"cfet\",\"dfet\",\"buzz\",\"heat\"]},\"state\":{\"type\":\"string\",\"enum\":[\"on\",\"off\"]},\"serial\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_-]{10,24}(?![\\\\s\\\\S])\"},\"restore_barcode\":{\"type\":\"boolean\"},\"image_size\":{\"type\":\"integer\",\"minimum\":65536,\"maximum\":524288},\"image_crc32\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":4294967295},\"image_version\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":12},\"clear_eeprom\":{\"type\":\"boolean\"},\"line\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":48}}},\"serial\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9_-]{8,24}(?![\\\\s\\\\S])\"},\"token\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{32}(?![\\\\s\\\\S])\"},\"stage\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"index\",\"total\",\"size\",\"crc32\",\"data\"],\"properties\":{\"id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9]{8,32}(?![\\\\s\\\\S])\"},\"index\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":2047},\"total\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":2048},\"size\":{\"type\":\"integer\",\"minimum\":65536,\"maximum\":524288},\"crc32\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":4294967295},\"data\":{\"type\":\"string\",\"minLength\":4,\"maxLength\":344,\"pattern\":\"^[A-Za-z0-9+/]+={0,2}(?![\\\\s\\\\S])\"}}}}}"
private const val SCHEMA_SOLAR_BATTERY_RESULT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"command_id\",\"port\",\"action\",\"stage\",\"accepted\",\"refusal\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"solar_battery_result\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"command_id\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{16}(?![\\\\s\\\\S])\"},\"port\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":10},\"action\":{\"type\":\"string\",\"enum\":[\"arm\",\"execute\",\"cancel\",\"stage\"]},\"op\":{\"type\":\"string\",\"maxLength\":32},\"stage\":{\"type\":\"string\",\"enum\":[\"armed\",\"started\",\"progress\",\"cancel_requested\",\"final\",\"rejected\",\"staged\"]},\"accepted\":{\"type\":\"boolean\"},\"refusal\":{\"type\":\"string\",\"enum\":[\"none\",\"disabled\",\"invalid_params\",\"unknown_op\",\"not_pylontech\",\"no_battery\",\"unknown_model\",\"unknown_firmware\",\"serial_mismatch\",\"serial_unreadable\",\"not_idle\",\"critical_alarm\",\"busy\",\"cooldown\",\"locked\",\"not_armed\",\"bad_token\",\"expired\",\"chip_unknown\",\"image_missing\",\"image_mismatch\",\"unsupported_model\",\"no_official_value\",\"risk_not_accepted\",\"expert_blocked\",\"no_password\",\"battery_changed\",\"clock_not_set\",\"not_cancellable\",\"no_memory\",\"no_answer\",\"login_failed\",\"preflight_failed\",\"stage_invalid\",\"stage_order\",\"stage_data\",\"stage_size\",\"stage_crc\"]},\"token\":{\"type\":\"string\",\"pattern\":\"^[0-9a-f]{32}(?![\\\\s\\\\S])\"},\"canonical\":{\"type\":\"string\",\"maxLength\":600},\"summary\":{\"type\":\"string\",\"maxLength\":300},\"risk\":{\"type\":\"string\",\"enum\":[\"low\",\"medium\",\"high\",\"irreversible\"]},\"atomic\":{\"type\":\"boolean\"},\"battery\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"model\",\"serial\",\"soft_version\",\"board\"],\"properties\":{\"model\":{\"type\":\"string\",\"maxLength\":24},\"serial\":{\"type\":\"string\",\"maxLength\":32},\"soft_version\":{\"type\":\"string\",\"maxLength\":24},\"board\":{\"type\":\"string\",\"maxLength\":24},\"capacity_ah\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000}}},\"snapshot_before\":{\"type\":\"string\",\"maxLength\":4000},\"outcome\":{\"type\":\"string\",\"enum\":[\"running\",\"ok\",\"failed\",\"partial\",\"retry\",\"rejected\"]},\"code\":{\"type\":\"string\",\"maxLength\":96},\"steps_done\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":200},\"steps_total\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":200},\"writes_done\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":200},\"packets_sent\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":2048},\"packets_total\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":2048},\"truncated\":{\"type\":\"boolean\"},\"before\":{\"type\":\"string\",\"maxLength\":4000},\"after\":{\"type\":\"string\",\"maxLength\":4000},\"transcript\":{\"type\":\"string\",\"maxLength\":8000},\"received\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":524288}}}"
private const val SCHEMA_SOLAR_INVERTER = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"device\",\"timestamp_ms\",\"mode\",\"grid_v\",\"grid_hz\",\"out_v\",\"out_hz\",\"out_va\",\"out_w\",\"load_percent\",\"battery_v\",\"battery_a\",\"battery_percent\",\"pv_v\",\"pv_a\",\"pv_w\",\"heatsink_c\",\"ac_charging\",\"pv_charging\",\"load_on\",\"warnings\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"inverter\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"device\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"mode\":{\"type\":\"string\",\"enum\":[\"power_on\",\"standby\",\"line\",\"battery\",\"fault\",\"power_saving\",\"shutdown\",\"unknown\"]},\"grid_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"grid_hz\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"out_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"out_hz\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"out_va\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"out_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"load_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":200},\"battery_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"battery_a\":{\"type\":\"number\",\"minimum\":-1000,\"maximum\":1000},\"battery_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"pv_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1500},\"pv_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":500},\"pv_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"heatsink_c\":{\"type\":\"number\",\"minimum\":-50,\"maximum\":200},\"ac_charging\":{\"type\":\"boolean\"},\"pv_charging\":{\"type\":\"boolean\"},\"load_on\":{\"type\":\"boolean\"},\"warnings\":{\"type\":\"array\",\"maxItems\":32,\"items\":{\"type\":\"string\",\"pattern\":\"^[a-z][a-z0-9_]{0,39}(?![\\\\s\\\\S])\"}},\"warnings_known\":{\"type\":\"boolean\"},\"clamped\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"string\",\"maxLength\":32}},\"pv2_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1500},\"pv2_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":500},\"pv2_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"total_out_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000},\"total_out_va\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000},\"total_load_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":200},\"total_charging_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":10000},\"units\":{\"type\":\"array\",\"maxItems\":10,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"unit\",\"mode\"],\"properties\":{\"unit\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":9},\"serial\":{\"type\":\"string\",\"maxLength\":24},\"mode\":{\"type\":\"string\",\"enum\":[\"power_on\",\"standby\",\"line\",\"battery\",\"fault\",\"power_saving\",\"shutdown\",\"unknown\"]},\"fault_code\":{\"type\":\"string\",\"pattern\":\"^[0-9]{2}(?![\\\\s\\\\S])\"},\"grid_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"out_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"out_va\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"out_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100000},\"load_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":200},\"battery_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000},\"battery_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"pv_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1500},\"charging_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000}}}},\"bus_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1500},\"serial\":{\"type\":\"string\",\"pattern\":\"^[0-9A-Za-z]{8,20}(?![\\\\s\\\\S])\"},\"firmware\":{\"type\":\"string\",\"pattern\":\"^[0-9A-Za-z._-]{1,24}(?![\\\\s\\\\S])\"},\"pv_energy_total_wh\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000000000.0},\"ratings\":{\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"grid_rating_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"out_rating_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"out_rating_hz\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"out_rating_va\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000},\"out_rating_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000},\"battery_rating_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"battery_recharge_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"battery_under_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"battery_bulk_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"battery_float_v\":{\"type\":\"number\",\"minimum\":0,\"maximum\":600},\"max_charge_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":2000},\"max_ac_charge_a\":{\"type\":\"number\",\"minimum\":0,\"maximum\":2000},\"battery_type\":{\"type\":\"string\",\"enum\":[\"agm\",\"flooded\",\"user\"]},\"input_range\":{\"type\":\"string\",\"enum\":[\"appliance\",\"ups\"]},\"output_priority\":{\"type\":\"string\",\"enum\":[\"utility_first\",\"solar_first\",\"sbu\"]},\"charger_priority\":{\"type\":\"string\",\"enum\":[\"utility_first\",\"solar_first\",\"solar_and_utility\",\"solar_only\"]}}}}}"
private const val SCHEMA_SOLAR_SYSTEM = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"kind\",\"node_id\",\"timestamp_ms\",\"inverters\",\"batteries\",\"alerts\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"system\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"inverters\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":16},\"batteries\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":16},\"pv_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000},\"load_w\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1000000},\"soc_percent\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100},\"balance_w\":{\"type\":\"number\",\"minimum\":-1000000,\"maximum\":1000000},\"alerts\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"code\",\"device\"],\"properties\":{\"code\":{\"type\":\"string\",\"enum\":[\"soc_low\",\"cell_over_voltage\",\"temperature_high\",\"temperature_low\"]},\"device\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"}}}}}}"
private const val SCHEMA_SYSTEM_EVENT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"id\",\"at\",\"type\",\"category\",\"action\"],\"properties\":{\"id\":{\"type\":\"integer\",\"minimum\":1},\"at\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":40},\"type\":{\"type\":\"string\",\"const\":\"system\"},\"category\":{\"type\":\"string\",\"enum\":[\"node\",\"broker\",\"settings\",\"service\",\"update\",\"alarm\",\"backup\",\"batteries\"]},\"action\":{\"type\":\"string\",\"enum\":[\"appeared\",\"returned\",\"disappeared\",\"firmware_changed\",\"connected\",\"disconnected\",\"created\",\"changed\",\"removed\",\"started\",\"stopped\",\"restarted\",\"checked\",\"installed\",\"rolled_back\",\"armed\",\"disarmed\",\"silenced\",\"acknowledged\",\"arm_requested\",\"disarm_requested\",\"silence_requested\",\"backup_made\",\"backup_restored\",\"battery_requested\",\"battery_operation\",\"control_requested\",\"control_acknowledged\",\"control_refused\",\"control_applied\",\"control_back\",\"control_lost\",\"maintenance_started\",\"maintenance_ended\",\"maintenance_expired\",\"dirty_boot\",\"sensor_bluetooth_open\",\"sensor_bluetooth_closed\",\"radar_event\",\"diagnostic_token_issued\",\"diagnostic_token_revoked\",\"diagnostic_token_used\",\"diagnostic_token_denied\"]},\"subject\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"by\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":60},\"version\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"previous_version\":{\"type\":\"string\",\"pattern\":\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?(?![\\\\s\\\\S])\"},\"profile\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,31}(?![\\\\s\\\\S])\"},\"outcome\":{\"type\":\"string\",\"enum\":[\"allowed\",\"denied\",\"failed\"]}}}"
private const val SCHEMA_TELEMETRY = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"node_id\",\"timestamp_ms\",\"lux\",\"targets\"],\"properties\":{\"kind\":{\"type\":\"string\",\"const\":\"telemetry\"},\"node_id\":{\"type\":\"string\",\"pattern\":\"^[a-z0-9][a-z0-9_-]{0,63}(?![\\\\s\\\\S])\"},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"lux\":{\"type\":\"number\",\"minimum\":0,\"maximum\":200000},\"targets\":{\"type\":\"array\",\"maxItems\":15,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"sensor_id\",\"track_id\",\"x_mm\",\"y_mm\",\"speed_mm_s\"],\"properties\":{\"sensor_id\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":3},\"track_id\":{\"type\":\"integer\",\"minimum\":1},\"x_mm\":{\"type\":\"number\"},\"y_mm\":{\"type\":\"number\"},\"speed_mm_s\":{\"type\":\"number\"}}}}}}"
private const val SCHEMA_VISION_EVENT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"schema\",\"type\",\"camera_id\",\"zone_id\",\"zone_name\",\"track_id\",\"label\",\"confidence\",\"box\",\"timestamp\",\"timestamp_ms\",\"authorizes_action\"],\"properties\":{\"schema\":{\"type\":\"string\",\"enum\":[\"armor.vision.event/v1\",\"armor.vision.event/v2\"]},\"type\":{\"type\":\"string\",\"enum\":[\"alert\",\"detection\"]},\"camera_id\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9._-]{3,80}(?![\\\\s\\\\S])\"},\"zone_id\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":80},\"zone_name\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":120},\"track_id\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":9007199254740991},\"label\":{\"type\":\"string\",\"minLength\":1,\"maxLength\":60},\"confidence\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1},\"box\":{\"type\":\"array\",\"minItems\":4,\"maxItems\":4,\"items\":{\"type\":\"number\",\"minimum\":0,\"maximum\":1}},\"timestamp\":{\"type\":\"number\",\"minimum\":0},\"timestamp_ms\":{\"type\":\"integer\",\"minimum\":0},\"authorizes_action\":{\"type\":\"boolean\",\"const\":false},\"radar_tracks\":{\"type\":\"integer\",\"minimum\":0,\"maximum\":1000},\"vectors\":{\"type\":\"array\",\"maxItems\":16,\"items\":{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"track_id\",\"dx\",\"dy\",\"speed\"],\"properties\":{\"track_id\":{\"type\":\"integer\",\"minimum\":1,\"maximum\":9007199254740991},\"dx\":{\"type\":\"number\",\"minimum\":-1,\"maximum\":1},\"dy\":{\"type\":\"number\",\"minimum\":-1,\"maximum\":1},\"speed\":{\"type\":\"number\",\"minimum\":0,\"maximum\":100}}}}}}"
private const val SCHEMA_VOICE_TURN_META = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"language\",\"encoding\",\"sample_rate\",\"channels\"],\"properties\":{\"language\":{\"type\":\"string\",\"enum\":[\"en\",\"es\",\"de\",\"fr\",\"it\",\"ja\",\"zh\",\"pt\"]},\"encoding\":{\"type\":\"string\",\"enum\":[\"pcm_s16le\"]},\"sample_rate\":{\"type\":\"integer\",\"enum\":[16000]},\"channels\":{\"type\":\"integer\",\"enum\":[1]},\"reply_audio\":{\"type\":\"string\",\"enum\":[\"base64\",\"binary\",\"none\"]}}}"
private const val SCHEMA_VOICE_TURN_RESULT = "{\"type\":\"object\",\"additionalProperties\":false,\"required\":[\"heard\",\"reply\"],\"properties\":{\"heard\":{\"type\":\"string\",\"maxLength\":2000},\"reply\":{\"type\":\"string\",\"maxLength\":2000},\"audio\":{\"type\":\"string\",\"pattern\":\"^[A-Za-z0-9+/]*={0,2}(?![\\\\s\\\\S])\",\"maxLength\":1400000},\"audio_omitted\":{\"type\":\"string\",\"enum\":[\"too_large\"]},\"challenge\":{\"type\":\"string\",\"pattern\":\"^[0-9]{2,6}(?![\\\\s\\\\S])\"}}}"

private val SCHEMAS: Map<String, JSONObject> by lazy {
    mapOf(
        "ai_observation" to JSONObject(SCHEMA_AI_OBSERVATION),
        "alarm" to JSONObject(SCHEMA_ALARM),
        "alarm_command" to JSONObject(SCHEMA_ALARM_COMMAND),
        "alarm_policy" to JSONObject(SCHEMA_ALARM_POLICY),
        "alarm_result" to JSONObject(SCHEMA_ALARM_RESULT),
        "alarm_zone_feed" to JSONObject(SCHEMA_ALARM_ZONE_FEED),
        "arm_profile" to JSONObject(SCHEMA_ARM_PROFILE),
        "arming_modes" to JSONObject(SCHEMA_ARMING_MODES),
        "command" to JSONObject(SCHEMA_COMMAND),
        "connection_client" to JSONObject(SCHEMA_CONNECTION_CLIENT),
        "connection_event" to JSONObject(SCHEMA_CONNECTION_EVENT),
        "daily_summary" to JSONObject(SCHEMA_DAILY_SUMMARY),
        "device_state" to JSONObject(SCHEMA_DEVICE_STATE),
        "diagnostic_token_created" to JSONObject(SCHEMA_DIAGNOSTIC_TOKEN_CREATED),
        "diagnostic_token_info" to JSONObject(SCHEMA_DIAGNOSTIC_TOKEN_INFO),
        "diagnostic_token_request" to JSONObject(SCHEMA_DIAGNOSTIC_TOKEN_REQUEST),
        "electrical" to JSONObject(SCHEMA_ELECTRICAL),
        "electrical_command" to JSONObject(SCHEMA_ELECTRICAL_COMMAND),
        "electrical_result" to JSONObject(SCHEMA_ELECTRICAL_RESULT),
        "health" to JSONObject(SCHEMA_HEALTH),
        "heatmap" to JSONObject(SCHEMA_HEATMAP),
        "info" to JSONObject(SCHEMA_INFO),
        "network" to JSONObject(SCHEMA_NETWORK),
        "network_orders" to JSONObject(SCHEMA_NETWORK_ORDERS),
        "node_control_command" to JSONObject(SCHEMA_NODE_CONTROL_COMMAND),
        "node_control_result" to JSONObject(SCHEMA_NODE_CONTROL_RESULT),
        "node_health" to JSONObject(SCHEMA_NODE_HEALTH),
        "node_maintenance" to JSONObject(SCHEMA_NODE_MAINTENANCE),
        "radar_event" to JSONObject(SCHEMA_RADAR_EVENT),
        "server_alert" to JSONObject(SCHEMA_SERVER_ALERT),
        "solar_battery" to JSONObject(SCHEMA_SOLAR_BATTERY),
        "solar_battery_command" to JSONObject(SCHEMA_SOLAR_BATTERY_COMMAND),
        "solar_battery_result" to JSONObject(SCHEMA_SOLAR_BATTERY_RESULT),
        "solar_inverter" to JSONObject(SCHEMA_SOLAR_INVERTER),
        "solar_system" to JSONObject(SCHEMA_SOLAR_SYSTEM),
        "system_event" to JSONObject(SCHEMA_SYSTEM_EVENT),
        "telemetry" to JSONObject(SCHEMA_TELEMETRY),
        "vision_event" to JSONObject(SCHEMA_VISION_EVENT),
        "voice_turn_meta" to JSONObject(SCHEMA_VOICE_TURN_META),
        "voice_turn_result" to JSONObject(SCHEMA_VOICE_TURN_RESULT),
    )
}

val MESSAGE_NAMES: List<String> get() = SCHEMAS.keys.sorted()

/** The JSON Schema of the message called `name`, or null: what a reader needs to leave out the members a closed object does not name. */
fun messageSchema(name: String): JSONObject? = SCHEMAS[name]

/** The first thing wrong with the document as the message called `name` (a JSONObject, a JSONArray, a String, a Number or a Boolean), or null when it is valid. */
fun checkMessage(name: String, value: Any?): ContractError? = firstError(value, SCHEMAS.getValue(name), "")

fun readRadarTrack(o: JSONObject): RadarTrack = RadarTrack(
    sensor_id = o.getLong("sensor_id"),
    track_id = o.getLong("track_id"),
    x_mm = o.getDouble("x_mm"),
    y_mm = o.getDouble("y_mm"),
    speed_mm_s = o.getDouble("speed_mm_s"),
)

fun readTelemetry(o: JSONObject): Telemetry = Telemetry(
    kind = if (o.has("kind")) o.getString("kind") else null,
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    lux = o.getDouble("lux"),
    targets = o.getJSONArray("targets").let { a -> (0 until a.length()).map { readRadarTrack(a.getJSONObject(it)) } },
)

fun readHealth(o: JSONObject): Health = Health(
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    online = o.getBoolean("online"),
    kind = if (o.has("kind")) o.getString("kind") else null,
)

fun readCommand(o: JSONObject): Command = Command(
    kind = if (o.has("kind")) o.getString("kind") else null,
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command = o.getString("command"),
    sensitivity = if (o.has("sensitivity")) o.getLong("sensitivity") else null,
)

fun readInfo(o: JSONObject): Info = Info(
    kind = if (o.has("kind")) o.getString("kind") else null,
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    name = o.getString("name"),
    firmware = o.getString("firmware"),
    ip = o.getString("ip"),
    port = o.getLong("port"),
    contract = if (o.has("contract")) o.getString("contract") else null,
)

fun readSolarInverterUnits(o: JSONObject): SolarInverterUnits = SolarInverterUnits(
    unit = o.getLong("unit"),
    serial = if (o.has("serial")) o.getString("serial") else null,
    mode = o.getString("mode"),
    fault_code = if (o.has("fault_code")) o.getString("fault_code") else null,
    grid_v = if (o.has("grid_v")) o.getDouble("grid_v") else null,
    out_v = if (o.has("out_v")) o.getDouble("out_v") else null,
    out_va = if (o.has("out_va")) o.getDouble("out_va") else null,
    out_w = if (o.has("out_w")) o.getDouble("out_w") else null,
    load_percent = if (o.has("load_percent")) o.getDouble("load_percent") else null,
    battery_v = if (o.has("battery_v")) o.getDouble("battery_v") else null,
    battery_percent = if (o.has("battery_percent")) o.getDouble("battery_percent") else null,
    pv_v = if (o.has("pv_v")) o.getDouble("pv_v") else null,
    charging_a = if (o.has("charging_a")) o.getDouble("charging_a") else null,
)

fun readSolarInverterRatings(o: JSONObject): SolarInverterRatings = SolarInverterRatings(
    grid_rating_v = if (o.has("grid_rating_v")) o.getDouble("grid_rating_v") else null,
    out_rating_v = if (o.has("out_rating_v")) o.getDouble("out_rating_v") else null,
    out_rating_hz = if (o.has("out_rating_hz")) o.getDouble("out_rating_hz") else null,
    out_rating_va = if (o.has("out_rating_va")) o.getDouble("out_rating_va") else null,
    out_rating_w = if (o.has("out_rating_w")) o.getDouble("out_rating_w") else null,
    battery_rating_v = if (o.has("battery_rating_v")) o.getDouble("battery_rating_v") else null,
    battery_recharge_v = if (o.has("battery_recharge_v")) o.getDouble("battery_recharge_v") else null,
    battery_under_v = if (o.has("battery_under_v")) o.getDouble("battery_under_v") else null,
    battery_bulk_v = if (o.has("battery_bulk_v")) o.getDouble("battery_bulk_v") else null,
    battery_float_v = if (o.has("battery_float_v")) o.getDouble("battery_float_v") else null,
    max_charge_a = if (o.has("max_charge_a")) o.getDouble("max_charge_a") else null,
    max_ac_charge_a = if (o.has("max_ac_charge_a")) o.getDouble("max_ac_charge_a") else null,
    battery_type = if (o.has("battery_type")) o.getString("battery_type") else null,
    input_range = if (o.has("input_range")) o.getString("input_range") else null,
    output_priority = if (o.has("output_priority")) o.getString("output_priority") else null,
    charger_priority = if (o.has("charger_priority")) o.getString("charger_priority") else null,
)

fun readSolarInverter(o: JSONObject): SolarInverter = SolarInverter(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    device = o.getString("device"),
    timestamp_ms = o.getLong("timestamp_ms"),
    mode = o.getString("mode"),
    grid_v = o.getDouble("grid_v"),
    grid_hz = o.getDouble("grid_hz"),
    out_v = o.getDouble("out_v"),
    out_hz = o.getDouble("out_hz"),
    out_va = o.getDouble("out_va"),
    out_w = o.getDouble("out_w"),
    load_percent = o.getDouble("load_percent"),
    battery_v = o.getDouble("battery_v"),
    battery_a = o.getDouble("battery_a"),
    battery_percent = o.getDouble("battery_percent"),
    pv_v = o.getDouble("pv_v"),
    pv_a = o.getDouble("pv_a"),
    pv_w = o.getDouble("pv_w"),
    heatsink_c = o.getDouble("heatsink_c"),
    ac_charging = o.getBoolean("ac_charging"),
    pv_charging = o.getBoolean("pv_charging"),
    load_on = o.getBoolean("load_on"),
    warnings = o.getJSONArray("warnings").let { a -> (0 until a.length()).map { a.getString(it) } },
    warnings_known = if (o.has("warnings_known")) o.getBoolean("warnings_known") else null,
    clamped = if (o.has("clamped")) o.getJSONArray("clamped").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    pv2_v = if (o.has("pv2_v")) o.getDouble("pv2_v") else null,
    pv2_a = if (o.has("pv2_a")) o.getDouble("pv2_a") else null,
    pv2_w = if (o.has("pv2_w")) o.getDouble("pv2_w") else null,
    total_out_w = if (o.has("total_out_w")) o.getDouble("total_out_w") else null,
    total_out_va = if (o.has("total_out_va")) o.getDouble("total_out_va") else null,
    total_load_percent = if (o.has("total_load_percent")) o.getDouble("total_load_percent") else null,
    total_charging_a = if (o.has("total_charging_a")) o.getDouble("total_charging_a") else null,
    units = if (o.has("units")) o.getJSONArray("units").let { a -> (0 until a.length()).map { readSolarInverterUnits(a.getJSONObject(it)) } } else null,
    bus_v = if (o.has("bus_v")) o.getDouble("bus_v") else null,
    serial = if (o.has("serial")) o.getString("serial") else null,
    firmware = if (o.has("firmware")) o.getString("firmware") else null,
    pv_energy_total_wh = if (o.has("pv_energy_total_wh")) o.getDouble("pv_energy_total_wh") else null,
    ratings = if (o.has("ratings")) readSolarInverterRatings(o.getJSONObject("ratings")) else null,
)

fun readSolarModuleLastEvent(o: JSONObject): SolarModuleLastEvent = SolarModuleLastEvent(
    index = o.getLong("index"),
    time = o.getString("time"),
    voltage_v = if (o.has("voltage_v")) o.getDouble("voltage_v") else null,
    current_a = if (o.has("current_a")) o.getDouble("current_a") else null,
    temperature_c = if (o.has("temperature_c")) o.getDouble("temperature_c") else null,
    percent = if (o.has("percent")) o.getLong("percent") else null,
    base_state = if (o.has("base_state")) o.getString("base_state") else null,
    voltage_state = if (o.has("voltage_state")) o.getString("voltage_state") else null,
    current_state = if (o.has("current_state")) o.getString("current_state") else null,
    temperature_state = if (o.has("temperature_state")) o.getString("temperature_state") else null,
    coulomb_state = if (o.has("coulomb_state")) o.getString("coulomb_state") else null,
    power_events = if (o.has("power_events")) o.getString("power_events") else null,
    battery_events = if (o.has("battery_events")) o.getString("battery_events") else null,
    system_fault = if (o.has("system_fault")) o.getString("system_fault") else null,
)

fun readSolarModule(o: JSONObject): SolarModule = SolarModule(
    n = o.getLong("n"),
    present = o.getBoolean("present"),
    voltage_v = if (o.has("voltage_v")) o.getDouble("voltage_v") else null,
    current_a = if (o.has("current_a")) o.getDouble("current_a") else null,
    temperature_c = if (o.has("temperature_c")) o.getDouble("temperature_c") else null,
    soc_percent = if (o.has("soc_percent")) o.getLong("soc_percent") else null,
    state = if (o.has("state")) o.getString("state") else null,
    cells_v = if (o.has("cells_v")) o.getJSONArray("cells_v").let { a -> (0 until a.length()).map { a.getDouble(it) } } else null,
    counters = if (o.has("counters")) o.getJSONObject("counters").let { m -> m.keys().asSequence().associateWith { m.getLong(it) } } else null,
    temperatures_c = if (o.has("temperatures_c")) o.getJSONArray("temperatures_c").let { a -> (0 until a.length()).map { a.getDouble(it) } } else null,
    capacity_ah = if (o.has("capacity_ah")) o.getDouble("capacity_ah") else null,
    full_capacity_ah = if (o.has("full_capacity_ah")) o.getDouble("full_capacity_ah") else null,
    cycles = if (o.has("cycles")) o.getLong("cycles") else null,
    health_percent = if (o.has("health_percent")) o.getLong("health_percent") else null,
    model = if (o.has("model")) o.getString("model") else null,
    cell_count = if (o.has("cell_count")) o.getLong("cell_count") else null,
    max_charge_a = if (o.has("max_charge_a")) o.getDouble("max_charge_a") else null,
    max_discharge_a = if (o.has("max_discharge_a")) o.getDouble("max_discharge_a") else null,
    console_baud = if (o.has("console_baud")) o.getLong("console_baud") else null,
    soh_counts = if (o.has("soh_counts")) o.getJSONArray("soh_counts").let { a -> (0 until a.length()).map { a.getLong(it) } } else null,
    soh_abnormal = if (o.has("soh_abnormal")) o.getJSONArray("soh_abnormal").let { a -> (0 until a.length()).map { a.getLong(it) } } else null,
    last_event = if (o.has("last_event")) readSolarModuleLastEvent(o.getJSONObject("last_event")) else null,
    board_version = if (o.has("board_version")) o.getString("board_version") else null,
    main_soft_version = if (o.has("main_soft_version")) o.getString("main_soft_version") else null,
    soft_version = if (o.has("soft_version")) o.getString("soft_version") else null,
)

fun readSolarBattery(o: JSONObject): SolarBattery = SolarBattery(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    device = o.getString("device"),
    timestamp_ms = o.getLong("timestamp_ms"),
    modules = o.getLong("modules"),
    state = if (o.has("state")) o.getString("state") else null,
    voltage_v = if (o.has("voltage_v")) o.getDouble("voltage_v") else null,
    current_a = if (o.has("current_a")) o.getDouble("current_a") else null,
    temperature_min_c = if (o.has("temperature_min_c")) o.getDouble("temperature_min_c") else null,
    temperature_max_c = if (o.has("temperature_max_c")) o.getDouble("temperature_max_c") else null,
    cell_min_v = if (o.has("cell_min_v")) o.getDouble("cell_min_v") else null,
    cell_max_v = if (o.has("cell_max_v")) o.getDouble("cell_max_v") else null,
    soc_percent = if (o.has("soc_percent")) o.getLong("soc_percent") else null,
    alarm = if (o.has("alarm")) o.getBoolean("alarm") else null,
    stack = o.getJSONArray("stack").let { a -> (0 until a.length()).map { readSolarModule(a.getJSONObject(it)) } },
    model = if (o.has("model")) o.getString("model") else null,
    capacity_ah = if (o.has("capacity_ah")) o.getDouble("capacity_ah") else null,
    full_capacity_ah = if (o.has("full_capacity_ah")) o.getDouble("full_capacity_ah") else null,
    energy_kwh = if (o.has("energy_kwh")) o.getDouble("energy_kwh") else null,
    cycles = if (o.has("cycles")) o.getLong("cycles") else null,
    health_percent = if (o.has("health_percent")) o.getLong("health_percent") else null,
    power_w = if (o.has("power_w")) o.getDouble("power_w") else null,
    balancing = if (o.has("balancing")) o.getLong("balancing") else null,
    protecting = if (o.has("protecting")) o.getBoolean("protecting") else null,
    charge_mos = if (o.has("charge_mos")) o.getLong("charge_mos") else null,
    discharge_mos = if (o.has("discharge_mos")) o.getLong("discharge_mos") else null,
)

fun readElectricalChannel(o: JSONObject): ElectricalChannel = ElectricalChannel(
    id = o.getString("id"),
    domain = o.getString("domain"),
    label = if (o.has("label")) o.getString("label") else null,
    voltage_v = if (o.has("voltage_v")) o.getDouble("voltage_v") else null,
    current_a = if (o.has("current_a")) o.getDouble("current_a") else null,
    power_w = if (o.has("power_w")) o.getDouble("power_w") else null,
    energy_kwh = if (o.has("energy_kwh")) o.getDouble("energy_kwh") else null,
    reading_age_ms = if (o.has("reading_age_ms")) o.getLong("reading_age_ms") else null,
    errors = if (o.has("errors")) o.getLong("errors") else null,
    power_estimated = if (o.has("power_estimated")) o.getBoolean("power_estimated") else null,
    frequency_hz = if (o.has("frequency_hz")) o.getDouble("frequency_hz") else null,
    power_factor = if (o.has("power_factor")) o.getDouble("power_factor") else null,
    state = if (o.has("state")) o.getString("state") else null,
    alarm = if (o.has("alarm")) o.getBoolean("alarm") else null,
    alarm_code = if (o.has("alarm_code")) o.getString("alarm_code") else null,
)

fun readElectricalSwitch(o: JSONObject): ElectricalSwitch = ElectricalSwitch(
    id = o.getString("id"),
    kind = o.getString("kind"),
    label = if (o.has("label")) o.getString("label") else null,
    source_a = if (o.has("source_a")) o.getString("source_a") else null,
    source_b = if (o.has("source_b")) o.getString("source_b") else null,
    a_closed = o.getBoolean("a_closed"),
    b_closed = o.getBoolean("b_closed"),
    selected = o.getString("selected"),
    wanted = o.getString("wanted"),
    closing = o.getBoolean("closing"),
    armed = o.getBoolean("armed"),
    fault = o.getString("fault"),
)

fun readElectrical(o: JSONObject): Electrical = Electrical(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    switching_enabled = if (o.has("switching_enabled")) o.getBoolean("switching_enabled") else null,
    channels = o.getJSONArray("channels").let { a -> (0 until a.length()).map { readElectricalChannel(a.getJSONObject(it)) } },
    switches = if (o.has("switches")) o.getJSONArray("switches").let { a -> (0 until a.length()).map { readElectricalSwitch(a.getJSONObject(it)) } } else null,
)

fun readElectricalCommand(o: JSONObject): ElectricalCommand = ElectricalCommand(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    switch = o.getString("switch"),
    action = o.getString("action"),
    token = if (o.has("token")) o.getString("token") else null,
)

fun readElectricalResult(o: JSONObject): ElectricalResult = ElectricalResult(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    switch = o.getString("switch"),
    action = o.getString("action"),
    accepted = o.getBoolean("accepted"),
    refusal = o.getString("refusal"),
    token = if (o.has("token")) o.getString("token") else null,
)

fun readSolarAlert(o: JSONObject): SolarAlert = SolarAlert(
    code = o.getString("code"),
    device = o.getString("device"),
)

fun readSolarSystem(o: JSONObject): SolarSystem = SolarSystem(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    inverters = o.getLong("inverters"),
    batteries = o.getLong("batteries"),
    pv_w = if (o.has("pv_w")) o.getDouble("pv_w") else null,
    load_w = if (o.has("load_w")) o.getDouble("load_w") else null,
    soc_percent = if (o.has("soc_percent")) o.getDouble("soc_percent") else null,
    balance_w = if (o.has("balance_w")) o.getDouble("balance_w") else null,
    alerts = o.getJSONArray("alerts").let { a -> (0 until a.length()).map { readSolarAlert(a.getJSONObject(it)) } },
)

fun readSolarBatteryStage(o: JSONObject): SolarBatteryStage = SolarBatteryStage(
    id = o.getString("id"),
    index = o.getLong("index"),
    total = o.getLong("total"),
    size = o.getLong("size"),
    crc32 = o.getLong("crc32"),
    data = o.getString("data"),
)

fun readSolarBatteryCommandParamsValues(o: JSONObject): SolarBatteryCommandParamsValues = SolarBatteryCommandParamsValues(
    pov = if (o.has("pov")) o.getLong("pov") else null,
    povr = if (o.has("povr")) o.getLong("povr") else null,
    phv = if (o.has("phv")) o.getLong("phv") else null,
    phvr = if (o.has("phvr")) o.getLong("phvr") else null,
    plv = if (o.has("plv")) o.getLong("plv") else null,
    plvr = if (o.has("plvr")) o.getLong("plvr") else null,
    puv = if (o.has("puv")) o.getLong("puv") else null,
    puvr = if (o.has("puvr")) o.getLong("puvr") else null,
    pslp = if (o.has("pslp")) o.getLong("pslp") else null,
    bov = if (o.has("bov")) o.getLong("bov") else null,
    bovr = if (o.has("bovr")) o.getLong("bovr") else null,
    bhv = if (o.has("bhv")) o.getLong("bhv") else null,
    bhvr = if (o.has("bhvr")) o.getLong("bhvr") else null,
    blv = if (o.has("blv")) o.getLong("blv") else null,
    blvr = if (o.has("blvr")) o.getLong("blvr") else null,
    buv = if (o.has("buv")) o.getLong("buv") else null,
    buvr = if (o.has("buvr")) o.getLong("buvr") else null,
    bslp = if (o.has("bslp")) o.getLong("bslp") else null,
    cot = if (o.has("cot")) o.getLong("cot") else null,
    cotr = if (o.has("cotr")) o.getLong("cotr") else null,
    cht = if (o.has("cht")) o.getLong("cht") else null,
    chtr = if (o.has("chtr")) o.getLong("chtr") else null,
    clt = if (o.has("clt")) o.getLong("clt") else null,
    cltr = if (o.has("cltr")) o.getLong("cltr") else null,
    cut = if (o.has("cut")) o.getLong("cut") else null,
    cutr = if (o.has("cutr")) o.getLong("cutr") else null,
)

fun readSolarBatteryCommandParamsItems(o: JSONObject): SolarBatteryCommandParamsItems = SolarBatteryCommandParamsItems(
    bov = if (o.has("bov")) o.getString("bov") else null,
    bhv = if (o.has("bhv")) o.getString("bhv") else null,
    blv = if (o.has("blv")) o.getString("blv") else null,
    buv = if (o.has("buv")) o.getString("buv") else null,
    bslp = if (o.has("bslp")) o.getString("bslp") else null,
    pov = if (o.has("pov")) o.getString("pov") else null,
    phv = if (o.has("phv")) o.getString("phv") else null,
    plv = if (o.has("plv")) o.getString("plv") else null,
    puv = if (o.has("puv")) o.getString("puv") else null,
    pslp = if (o.has("pslp")) o.getString("pslp") else null,
    coc = if (o.has("coc")) o.getString("coc") else null,
    coc2 = if (o.has("coc2")) o.getString("coc2") else null,
    doc = if (o.has("doc")) o.getString("doc") else null,
    doc2 = if (o.has("doc2")) o.getString("doc2") else null,
)

fun readSolarBatteryCommandParams(o: JSONObject): SolarBatteryCommandParams = SolarBatteryCommandParams(
    which = if (o.has("which")) o.getString("which") else null,
    group = if (o.has("group")) o.getString("group") else null,
    values = if (o.has("values")) readSolarBatteryCommandParamsValues(o.getJSONObject("values")) else null,
    items = if (o.has("items")) readSolarBatteryCommandParamsItems(o.getJSONObject("items")) else null,
    accept_risk = if (o.has("accept_risk")) o.getBoolean("accept_risk") else null,
    output = if (o.has("output")) o.getString("output") else null,
    state = if (o.has("state")) o.getString("state") else null,
    serial = if (o.has("serial")) o.getString("serial") else null,
    restore_barcode = if (o.has("restore_barcode")) o.getBoolean("restore_barcode") else null,
    image_size = if (o.has("image_size")) o.getLong("image_size") else null,
    image_crc32 = if (o.has("image_crc32")) o.getLong("image_crc32") else null,
    image_version = if (o.has("image_version")) o.getString("image_version") else null,
    clear_eeprom = if (o.has("clear_eeprom")) o.getBoolean("clear_eeprom") else null,
    line = if (o.has("line")) o.getString("line") else null,
)

fun readSolarBatteryCommand(o: JSONObject): SolarBatteryCommand = SolarBatteryCommand(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    port = o.getLong("port"),
    action = o.getString("action"),
    op = if (o.has("op")) o.getString("op") else null,
    params = if (o.has("params")) readSolarBatteryCommandParams(o.getJSONObject("params")) else null,
    serial = if (o.has("serial")) o.getString("serial") else null,
    token = if (o.has("token")) o.getString("token") else null,
    stage = if (o.has("stage")) readSolarBatteryStage(o.getJSONObject("stage")) else null,
)

fun readSolarBatteryIdentity(o: JSONObject): SolarBatteryIdentity = SolarBatteryIdentity(
    model = o.getString("model"),
    serial = o.getString("serial"),
    soft_version = o.getString("soft_version"),
    board = o.getString("board"),
    capacity_ah = if (o.has("capacity_ah")) o.getLong("capacity_ah") else null,
)

fun readSolarBatteryResult(o: JSONObject): SolarBatteryResult = SolarBatteryResult(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    port = o.getLong("port"),
    action = o.getString("action"),
    op = if (o.has("op")) o.getString("op") else null,
    stage = o.getString("stage"),
    accepted = o.getBoolean("accepted"),
    refusal = o.getString("refusal"),
    token = if (o.has("token")) o.getString("token") else null,
    canonical = if (o.has("canonical")) o.getString("canonical") else null,
    summary = if (o.has("summary")) o.getString("summary") else null,
    risk = if (o.has("risk")) o.getString("risk") else null,
    atomic = if (o.has("atomic")) o.getBoolean("atomic") else null,
    battery = if (o.has("battery")) readSolarBatteryIdentity(o.getJSONObject("battery")) else null,
    snapshot_before = if (o.has("snapshot_before")) o.getString("snapshot_before") else null,
    outcome = if (o.has("outcome")) o.getString("outcome") else null,
    code = if (o.has("code")) o.getString("code") else null,
    steps_done = if (o.has("steps_done")) o.getLong("steps_done") else null,
    steps_total = if (o.has("steps_total")) o.getLong("steps_total") else null,
    writes_done = if (o.has("writes_done")) o.getLong("writes_done") else null,
    packets_sent = if (o.has("packets_sent")) o.getLong("packets_sent") else null,
    packets_total = if (o.has("packets_total")) o.getLong("packets_total") else null,
    truncated = if (o.has("truncated")) o.getBoolean("truncated") else null,
    before = if (o.has("before")) o.getString("before") else null,
    after = if (o.has("after")) o.getString("after") else null,
    transcript = if (o.has("transcript")) o.getString("transcript") else null,
    received = if (o.has("received")) o.getLong("received") else null,
)

fun readNodeControlCommand(o: JSONObject): NodeControlCommand = NodeControlCommand(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    action = o.getString("action"),
    operation = o.getString("operation"),
    mode = o.getString("mode"),
    delay_s = if (o.has("delay_s")) o.getLong("delay_s") else null,
    slot = if (o.has("slot")) o.getLong("slot") else null,
    duration_s = if (o.has("duration_s")) o.getLong("duration_s") else null,
    token = if (o.has("token")) o.getString("token") else null,
    requested_by = o.getString("requested_by"),
    detail = if (o.has("detail")) o.getString("detail") else null,
)

fun readNodeControlResultDiagnosticsPackageHeap(o: JSONObject): NodeControlResultDiagnosticsPackageHeap = NodeControlResultDiagnosticsPackageHeap(
    internal_free = o.getLong("internal_free"),
    internal_min = o.getLong("internal_min"),
    internal_largest = o.getLong("internal_largest"),
    total_free = o.getLong("total_free"),
    total_min = o.getLong("total_min"),
    psram_free = if (o.has("psram_free")) o.getLong("psram_free") else null,
)

fun readNodeControlResultDiagnosticsPackageTasks(o: JSONObject): NodeControlResultDiagnosticsPackageTasks = NodeControlResultDiagnosticsPackageTasks(
    name = o.getString("name"),
    stack_free = o.getLong("stack_free"),
    priority = o.getLong("priority"),
    state = o.getString("state"),
)

fun readNodeControlResultDiagnosticsPackageResets(o: JSONObject): NodeControlResultDiagnosticsPackageResets = NodeControlResultDiagnosticsPackageResets(
    reason = o.getString("reason"),
    uptime_s = o.getLong("uptime_s"),
    guard_restarts_in_hour = o.getLong("guard_restarts_in_hour"),
)

fun readNodeControlResultDiagnosticsPackageBoot(o: JSONObject): NodeControlResultDiagnosticsPackageBoot = NodeControlResultDiagnosticsPackageBoot(
    cause = o.getString("cause"),
    reset_reason = o.getString("reset_reason"),
    uptime_before_s = if (o.has("uptime_before_s")) o.getLong("uptime_before_s") else null,
    heap_internal_free = if (o.has("heap_internal_free")) o.getLong("heap_internal_free") else null,
    heap_internal_largest = if (o.has("heap_internal_largest")) o.getLong("heap_internal_largest") else null,
    coredump = o.getBoolean("coredump"),
    deliberate = o.getBoolean("deliberate"),
    guard = o.getBoolean("guard"),
)

fun readNodeControlResultDiagnosticsPackageMemoryGate(o: JSONObject): NodeControlResultDiagnosticsPackageMemoryGate = NodeControlResultDiagnosticsPackageMemoryGate(
    closed = o.getBoolean("closed"),
    transitions = o.getLong("transitions"),
    close_free = o.getLong("close_free"),
    close_block = o.getLong("close_block"),
    open_free = o.getLong("open_free"),
    open_block = o.getLong("open_block"),
)

fun readNodeControlResultDiagnosticsPackageVersionsSensors(o: JSONObject): NodeControlResultDiagnosticsPackageVersionsSensors = NodeControlResultDiagnosticsPackageVersionsSensors(
    name = o.getString("name"),
    version = o.getString("version"),
)

fun readNodeControlResultDiagnosticsPackageVersions(o: JSONObject): NodeControlResultDiagnosticsPackageVersions = NodeControlResultDiagnosticsPackageVersions(
    firmware = o.getString("firmware"),
    idf = o.getString("idf"),
    board = if (o.has("board")) o.getString("board") else null,
    sensors = o.getJSONArray("sensors").let { a -> (0 until a.length()).map { readNodeControlResultDiagnosticsPackageVersionsSensors(a.getJSONObject(it)) } },
)

fun readNodeControlResultDiagnosticsPackageCoredumpSummary(o: JSONObject): NodeControlResultDiagnosticsPackageCoredumpSummary = NodeControlResultDiagnosticsPackageCoredumpSummary(
    task = o.getString("task"),
    reason = if (o.has("reason")) o.getString("reason") else null,
    pc = if (o.has("pc")) o.getString("pc") else null,
    backtrace = if (o.has("backtrace")) o.getJSONArray("backtrace").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    app_sha256 = if (o.has("app_sha256")) o.getString("app_sha256") else null,
)

fun readNodeControlResultDiagnosticsPackageCoredump(o: JSONObject): NodeControlResultDiagnosticsPackageCoredump = NodeControlResultDiagnosticsPackageCoredump(
    present = o.getBoolean("present"),
    size = if (o.has("size")) o.getLong("size") else null,
    summary = if (o.has("summary")) readNodeControlResultDiagnosticsPackageCoredumpSummary(o.getJSONObject("summary")) else null,
)

fun readNodeControlResultDiagnosticsPackage(o: JSONObject): NodeControlResultDiagnosticsPackage = NodeControlResultDiagnosticsPackage(
    detail = o.getString("detail"),
    heap = if (o.has("heap")) readNodeControlResultDiagnosticsPackageHeap(o.getJSONObject("heap")) else null,
    tasks = if (o.has("tasks")) o.getJSONArray("tasks").let { a -> (0 until a.length()).map { readNodeControlResultDiagnosticsPackageTasks(a.getJSONObject(it)) } } else null,
    resets = if (o.has("resets")) readNodeControlResultDiagnosticsPackageResets(o.getJSONObject("resets")) else null,
    boot = if (o.has("boot")) readNodeControlResultDiagnosticsPackageBoot(o.getJSONObject("boot")) else null,
    memory_gate = if (o.has("memory_gate")) readNodeControlResultDiagnosticsPackageMemoryGate(o.getJSONObject("memory_gate")) else null,
    versions = if (o.has("versions")) readNodeControlResultDiagnosticsPackageVersions(o.getJSONObject("versions")) else null,
    config = if (o.has("config")) o.getJSONObject("config").let { m -> m.keys().asSequence().associateWith { m.getString(it) } } else null,
    coredump = if (o.has("coredump")) readNodeControlResultDiagnosticsPackageCoredump(o.getJSONObject("coredump")) else null,
    log = o.getString("log"),
    truncated = o.getBoolean("truncated"),
)

fun readNodeControlResultDiagnostics(o: JSONObject): NodeControlResultDiagnostics = NodeControlResultDiagnostics(
    firmware = o.getString("firmware"),
    uptime_s = o.getLong("uptime_s"),
    reset_reason = o.getString("reset_reason"),
    heap_free = o.getLong("heap_free"),
    heap_min = o.getLong("heap_min"),
    psram_free = if (o.has("psram_free")) o.getLong("psram_free") else null,
    stack_min_free = if (o.has("stack_min_free")) o.getLong("stack_min_free") else null,
    rssi = if (o.has("rssi")) o.getLong("rssi") else null,
    mqtt_connected = o.getBoolean("mqtt_connected"),
    state = o.getString("state"),
    maintenance = o.getBoolean("maintenance"),
    `package` = if (o.has("package")) readNodeControlResultDiagnosticsPackage(o.getJSONObject("package")) else null,
)

fun readNodeControlResult(o: JSONObject): NodeControlResult = NodeControlResult(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    action = o.getString("action"),
    operation = o.getString("operation"),
    stage = o.getString("stage"),
    accepted = o.getBoolean("accepted"),
    refusal = o.getString("refusal"),
    token = if (o.has("token")) o.getString("token") else null,
    token_ttl_s = if (o.has("token_ttl_s")) o.getLong("token_ttl_s") else null,
    reason = if (o.has("reason")) o.getString("reason") else null,
    mode = if (o.has("mode")) o.getString("mode") else null,
    restart_in_s = if (o.has("restart_in_s")) o.getLong("restart_in_s") else null,
    uptime_s = if (o.has("uptime_s")) o.getLong("uptime_s") else null,
    firmware = if (o.has("firmware")) o.getString("firmware") else null,
    requested_by = if (o.has("requested_by")) o.getString("requested_by") else null,
    state = if (o.has("state")) o.getString("state") else null,
    maintenance = if (o.has("maintenance")) o.getBoolean("maintenance") else null,
    until_s = if (o.has("until_s")) o.getLong("until_s") else null,
    since_ms = if (o.has("since_ms")) o.getLong("since_ms") else null,
    diagnostics = if (o.has("diagnostics")) readNodeControlResultDiagnostics(o.getJSONObject("diagnostics")) else null,
)

fun readNodeMaintenance(o: JSONObject): NodeMaintenance = NodeMaintenance(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    active = o.getBoolean("active"),
    reason = o.getString("reason"),
    expected_s = if (o.has("expected_s")) o.getLong("expected_s") else null,
    firmware = o.getString("firmware"),
    requested_by = if (o.has("requested_by")) o.getString("requested_by") else null,
)

fun readRadarEvent(o: JSONObject): RadarEvent = RadarEvent(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    boot = o.getLong("boot"),
    seq = o.getLong("seq"),
    event = o.getString("event"),
    name = if (o.has("name")) o.getString("name") else null,
    sensor_id = if (o.has("sensor_id")) o.getLong("sensor_id") else null,
    track_id = if (o.has("track_id")) o.getLong("track_id") else null,
    movement = if (o.has("movement")) o.getString("movement") else null,
    value = if (o.has("value")) o.getLong("value") else null,
    count = if (o.has("count")) o.getLong("count") else null,
    direction = if (o.has("direction")) o.getString("direction") else null,
    from = if (o.has("from")) o.getString("from") else null,
    by = if (o.has("by")) o.getString("by") else null,
)

fun readDiagnosticTokenRequest(o: JSONObject): DiagnosticTokenRequest = DiagnosticTokenRequest(
    nodes = o.getJSONArray("nodes").let { a -> (0 until a.length()).map { a.getString(it) } },
    ttl_s = if (o.has("ttl_s")) o.getLong("ttl_s") else null,
    label = if (o.has("label")) o.getString("label") else null,
)

fun readDiagnosticTokenCreated(o: JSONObject): DiagnosticTokenCreated = DiagnosticTokenCreated(
    id = o.getString("id"),
    token = o.getString("token"),
    scope = o.getString("scope"),
    nodes = o.getJSONArray("nodes").let { a -> (0 until a.length()).map { a.getString(it) } },
    label = if (o.has("label")) o.getString("label") else null,
    created_at = o.getString("created_at"),
    expires_at = o.getString("expires_at"),
    created_by = o.getString("created_by"),
)

fun readDiagnosticTokenInfo(o: JSONObject): DiagnosticTokenInfo = DiagnosticTokenInfo(
    id = o.getString("id"),
    scope = o.getString("scope"),
    nodes = o.getJSONArray("nodes").let { a -> (0 until a.length()).map { a.getString(it) } },
    label = if (o.has("label")) o.getString("label") else null,
    created_at = o.getString("created_at"),
    expires_at = o.getString("expires_at"),
    created_by = o.getString("created_by"),
    status = o.getString("status"),
    revoked_at = if (o.has("revoked_at")) o.getString("revoked_at") else null,
    revoked_by = if (o.has("revoked_by")) o.getString("revoked_by") else null,
    uses = o.getLong("uses"),
    last_used_at = if (o.has("last_used_at")) o.getString("last_used_at") else null,
)

fun readAlarmZone(o: JSONObject): AlarmZone = AlarmZone(
    id = o.getString("id"),
    name = if (o.has("name")) o.getString("name") else null,
    kind = o.getString("kind"),
    state = o.getString("state"),
    bypassed = o.getBoolean("bypassed"),
)

fun readAlarmEvent(o: JSONObject): AlarmEvent = AlarmEvent(
    ago_s = o.getLong("ago_s"),
    kind = o.getString("kind"),
    zone = if (o.has("zone")) o.getString("zone") else null,
)

fun readAlarm(o: JSONObject): Alarm = Alarm(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    phase = o.getString("phase"),
    mode = o.getString("mode"),
    siren = o.getBoolean("siren"),
    locked_out = o.getBoolean("locked_out"),
    commands_enabled = o.getBoolean("commands_enabled"),
    zones = o.getJSONArray("zones").let { a -> (0 until a.length()).map { readAlarmZone(a.getJSONObject(it)) } },
    open_zones = o.getJSONArray("open_zones").let { a -> (0 until a.length()).map { a.getString(it) } },
    events = o.getJSONArray("events").let { a -> (0 until a.length()).map { readAlarmEvent(a.getJSONObject(it)) } },
    arm_profiles = if (o.has("arm_profiles")) o.getBoolean("arm_profiles") else null,
    profile = if (o.has("profile")) o.getString("profile") else null,
    siren_loop = if (o.has("siren_loop")) o.getString("siren_loop") else null,
    siren_fault = if (o.has("siren_fault")) o.getBoolean("siren_fault") else null,
    seq = if (o.has("seq")) o.getLong("seq") else null,
    sig = if (o.has("sig")) o.getString("sig") else null,
)

fun readArmProfileZone(o: JSONObject): ArmProfileZone = ArmProfileZone(
    id = o.getString("id"),
    armed = if (o.has("armed")) o.getBoolean("armed") else null,
    delay = if (o.has("delay")) o.getString("delay") else null,
)

fun readArmProfile(o: JSONObject): ArmProfile = ArmProfile(
    id = o.getString("id"),
    name = o.getString("name"),
    base = o.getString("base"),
    exit_delay_s = if (o.has("exit_delay_s")) o.getLong("exit_delay_s") else null,
    entry_delay_s = if (o.has("entry_delay_s")) o.getLong("entry_delay_s") else null,
    siren = if (o.has("siren")) o.getBoolean("siren") else null,
    notify = if (o.has("notify")) o.getString("notify") else null,
    zones = if (o.has("zones")) o.getJSONArray("zones").let { a -> (0 until a.length()).map { readArmProfileZone(a.getJSONObject(it)) } } else null,
)

fun readAlarmCommand(o: JSONObject): AlarmCommand = AlarmCommand(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    action = o.getString("action"),
    mode = if (o.has("mode")) o.getString("mode") else null,
    force = if (o.has("force")) o.getBoolean("force") else null,
    profile = if (o.has("profile")) readArmProfile(o.getJSONObject("profile")) else null,
)

fun readAlarmResult(o: JSONObject): AlarmResult = AlarmResult(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    command_id = o.getString("command_id"),
    action = o.getString("action"),
    accepted = o.getBoolean("accepted"),
    refusal = o.getString("refusal"),
    phase = o.getString("phase"),
)

fun readArmingModesModesAway(o: JSONObject): ArmingModesModesAway = ArmingModesModesAway(
    entry = if (o.has("entry")) o.getJSONArray("entry").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    exit_delay_s = if (o.has("exit_delay_s")) o.getLong("exit_delay_s") else null,
    entry_delay_s = if (o.has("entry_delay_s")) o.getLong("entry_delay_s") else null,
)

fun readArmingModesModesHome(o: JSONObject): ArmingModesModesHome = ArmingModesModesHome(
    defends = if (o.has("defends")) o.getJSONArray("defends").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    entry = if (o.has("entry")) o.getJSONArray("entry").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    exit_delay_s = if (o.has("exit_delay_s")) o.getLong("exit_delay_s") else null,
    entry_delay_s = if (o.has("entry_delay_s")) o.getLong("entry_delay_s") else null,
)

fun readArmingModesModesNight(o: JSONObject): ArmingModesModesNight = ArmingModesModesNight(
    defends = if (o.has("defends")) o.getJSONArray("defends").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    entry = if (o.has("entry")) o.getJSONArray("entry").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
    exit_delay_s = if (o.has("exit_delay_s")) o.getLong("exit_delay_s") else null,
    entry_delay_s = if (o.has("entry_delay_s")) o.getLong("entry_delay_s") else null,
)

fun readArmingModesModes(o: JSONObject): ArmingModesModes = ArmingModesModes(
    away = readArmingModesModesAway(o.getJSONObject("away")),
    home = readArmingModesModesHome(o.getJSONObject("home")),
    night = readArmingModesModesNight(o.getJSONObject("night")),
)

fun readArmingModesSchedule(o: JSONObject): ArmingModesSchedule = ArmingModesSchedule(
    mode = o.getString("mode"),
    days = o.getJSONArray("days").let { a -> (0 until a.length()).map { a.getLong(it) } },
    at = o.getString("at"),
)

fun readArmingModesPanelMapProfiles(o: JSONObject): ArmingModesPanelMapProfiles = ArmingModesPanelMapProfiles(
    away = if (o.has("away")) o.getString("away") else null,
    home = if (o.has("home")) o.getString("home") else null,
    night = if (o.has("night")) o.getString("night") else null,
)

fun readArmingModesPanelMap(o: JSONObject): ArmingModesPanelMap = ArmingModesPanelMap(
    profiles = if (o.has("profiles")) readArmingModesPanelMapProfiles(o.getJSONObject("profiles")) else null,
    only = if (o.has("only")) o.getJSONArray("only").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
)

fun readArmingModes(o: JSONObject): ArmingModes = ArmingModes(
    modes = readArmingModesModes(o.getJSONObject("modes")),
    schedule = if (o.has("schedule")) o.getJSONArray("schedule").let { a -> (0 until a.length()).map { readArmingModesSchedule(a.getJSONObject(it)) } } else null,
    panel_map = if (o.has("panel_map")) readArmingModesPanelMap(o.getJSONObject("panel_map")) else null,
)

fun readAlarmZoneFeed(o: JSONObject): AlarmZoneFeed = AlarmZoneFeed(
    zone = o.getString("zone"),
    state = o.getString("state"),
    battery_low = o.getBoolean("battery_low"),
    seq = if (o.has("seq")) o.getLong("seq") else null,
    sig = if (o.has("sig")) o.getString("sig") else null,
)

fun readAlarmPolicy(o: JSONObject): AlarmPolicy = AlarmPolicy(
    config_hash = o.getBoolean("config_hash"),
    zone_feed = o.getBoolean("zone_feed"),
    zone_feed_signature = o.getBoolean("zone_feed_signature"),
    disarm_pin = if (o.has("disarm_pin")) o.getString("disarm_pin") else null,
    nvs_encryption = if (o.has("nvs_encryption")) o.getString("nvs_encryption") else null,
)

fun readNodeHealthBoot(o: JSONObject): NodeHealthBoot = NodeHealthBoot(
    cause = o.getString("cause"),
    reset_reason = o.getString("reset_reason"),
    uptime_before_s = if (o.has("uptime_before_s")) o.getLong("uptime_before_s") else null,
    heap_internal_free = if (o.has("heap_internal_free")) o.getLong("heap_internal_free") else null,
    heap_internal_largest = if (o.has("heap_internal_largest")) o.getLong("heap_internal_largest") else null,
    coredump = o.getBoolean("coredump"),
    deliberate = o.getBoolean("deliberate"),
    guard = o.getBoolean("guard"),
)

fun readNodeHealthMemoryGate(o: JSONObject): NodeHealthMemoryGate = NodeHealthMemoryGate(
    closed = o.getBoolean("closed"),
    transitions = o.getLong("transitions"),
    close_free = o.getLong("close_free"),
    close_block = o.getLong("close_block"),
    open_free = o.getLong("open_free"),
    open_block = o.getLong("open_block"),
)

fun readNodeHealthCoredump(o: JSONObject): NodeHealthCoredump = NodeHealthCoredump(
    present = o.getBoolean("present"),
    size = if (o.has("size")) o.getLong("size") else null,
)

fun readNodeHealthConfigCheck(o: JSONObject): NodeHealthConfigCheck = NodeHealthConfigCheck(
    snapshot = if (o.has("snapshot")) o.getString("snapshot") else null,
    reverted = if (o.has("reverted")) o.getString("reverted") else null,
)

fun readNodeHealthSensors(o: JSONObject): NodeHealthSensors = NodeHealthSensors(
    sensor_id = o.getLong("sensor_id"),
    model = o.getString("model"),
    state = o.getString("state"),
    firmware_known = o.getBoolean("firmware_known"),
    firmware = if (o.has("firmware")) o.getString("firmware") else null,
    bluetooth = o.getString("bluetooth"),
    mac = if (o.has("mac")) o.getString("mac") else null,
    bluetooth_alert = if (o.has("bluetooth_alert")) o.getBoolean("bluetooth_alert") else null,
    quirk = if (o.has("quirk")) o.getString("quirk") else null,
)

fun readNodeHealthRadar(o: JSONObject): NodeHealthRadar = NodeHealthRadar(
    perimeter_enabled = o.getBoolean("perimeter_enabled"),
    masked = o.getBoolean("masked"),
    wifi_jam = o.getBoolean("wifi_jam"),
    bridge_open = o.getBoolean("bridge_open"),
    events_buffered = o.getLong("events_buffered"),
    sensor_bluetooth_off = o.getBoolean("sensor_bluetooth_off"),
)

fun readNodeHealth(o: JSONObject): NodeHealth = NodeHealth(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    timestamp_ms = o.getLong("timestamp_ms"),
    family = o.getString("family"),
    firmware = o.getString("firmware"),
    contract = if (o.has("contract")) o.getString("contract") else null,
    board = if (o.has("board")) o.getString("board") else null,
    uptime_s = o.getLong("uptime_s"),
    reset_reason = o.getString("reset_reason"),
    heap_free = o.getLong("heap_free"),
    heap_min = o.getLong("heap_min"),
    heap_internal_free = if (o.has("heap_internal_free")) o.getLong("heap_internal_free") else null,
    heap_internal_min = if (o.has("heap_internal_min")) o.getLong("heap_internal_min") else null,
    heap_internal_largest = if (o.has("heap_internal_largest")) o.getLong("heap_internal_largest") else null,
    psram_free = if (o.has("psram_free")) o.getLong("psram_free") else null,
    link = o.getString("link"),
    link_up = o.getBoolean("link_up"),
    rssi_dbm = if (o.has("rssi_dbm")) o.getLong("rssi_dbm") else null,
    broker_reconnects = o.getLong("broker_reconnects"),
    low_stack_tasks = if (o.has("low_stack_tasks")) o.getLong("low_stack_tasks") else null,
    stack_min_free = if (o.has("stack_min_free")) o.getLong("stack_min_free") else null,
    stack_min_task = if (o.has("stack_min_task")) o.getString("stack_min_task") else null,
    last_error = if (o.has("last_error")) o.getString("last_error") else null,
    control_state = if (o.has("control_state")) o.getString("control_state") else null,
    control_since_ms = if (o.has("control_since_ms")) o.getLong("control_since_ms") else null,
    control_by = if (o.has("control_by")) o.getString("control_by") else null,
    control_until_s = if (o.has("control_until_s")) o.getLong("control_until_s") else null,
    maintenance = if (o.has("maintenance")) o.getBoolean("maintenance") else null,
    maintenance_until_s = if (o.has("maintenance_until_s")) o.getLong("maintenance_until_s") else null,
    boot = if (o.has("boot")) readNodeHealthBoot(o.getJSONObject("boot")) else null,
    memory_gate = if (o.has("memory_gate")) readNodeHealthMemoryGate(o.getJSONObject("memory_gate")) else null,
    coredump = if (o.has("coredump")) readNodeHealthCoredump(o.getJSONObject("coredump")) else null,
    config_check = if (o.has("config_check")) readNodeHealthConfigCheck(o.getJSONObject("config_check")) else null,
    sensors = if (o.has("sensors")) o.getJSONArray("sensors").let { a -> (0 until a.length()).map { readNodeHealthSensors(a.getJSONObject(it)) } } else null,
    radar = if (o.has("radar")) readNodeHealthRadar(o.getJSONObject("radar")) else null,
)

fun readVoiceTurnMeta(o: JSONObject): VoiceTurnMeta = VoiceTurnMeta(
    language = o.getString("language"),
    encoding = o.getString("encoding"),
    sample_rate = o.getLong("sample_rate"),
    channels = o.getLong("channels"),
    reply_audio = if (o.has("reply_audio")) o.getString("reply_audio") else null,
)

fun readVoiceTurnResult(o: JSONObject): VoiceTurnResult = VoiceTurnResult(
    heard = o.getString("heard"),
    reply = o.getString("reply"),
    audio = if (o.has("audio")) o.getString("audio") else null,
    audio_omitted = if (o.has("audio_omitted")) o.getString("audio_omitted") else null,
    challenge = if (o.has("challenge")) o.getString("challenge") else null,
)

fun readConnectionEvent(o: JSONObject): ConnectionEvent = ConnectionEvent(
    id = o.getLong("id"),
    at = o.getString("at"),
    type = o.getString("type"),
    action = o.getString("action"),
    client_kind = o.getString("client_kind"),
    client_id = o.getString("client_id"),
    user = if (o.has("user")) o.getString("user") else null,
    origin = if (o.has("origin")) o.getString("origin") else null,
    two_factor = if (o.has("two_factor")) o.getBoolean("two_factor") else null,
    app_version = if (o.has("app_version")) o.getString("app_version") else null,
    subject = if (o.has("subject")) o.getString("subject") else null,
    ip = if (o.has("ip")) o.getString("ip") else null,
    agent = if (o.has("agent")) o.getString("agent") else null,
)

fun readSystemEvent(o: JSONObject): SystemEvent = SystemEvent(
    id = o.getLong("id"),
    at = o.getString("at"),
    type = o.getString("type"),
    category = o.getString("category"),
    action = o.getString("action"),
    subject = if (o.has("subject")) o.getString("subject") else null,
    by = if (o.has("by")) o.getString("by") else null,
    version = if (o.has("version")) o.getString("version") else null,
    previous_version = if (o.has("previous_version")) o.getString("previous_version") else null,
    profile = if (o.has("profile")) o.getString("profile") else null,
    outcome = if (o.has("outcome")) o.getString("outcome") else null,
)

fun readConnectionClient(o: JSONObject): ConnectionClient = ConnectionClient(
    id = o.getString("id"),
    kind = o.getString("kind"),
    user = if (o.has("user")) o.getString("user") else null,
    label = if (o.has("label")) o.getString("label") else null,
    app_version = if (o.has("app_version")) o.getString("app_version") else null,
    origin = if (o.has("origin")) o.getString("origin") else null,
    two_factor = if (o.has("two_factor")) o.getBoolean("two_factor") else null,
    first_seen = o.getString("first_seen"),
    last_seen = o.getString("last_seen"),
    last_failure = if (o.has("last_failure")) o.getString("last_failure") else null,
    active_sessions = o.getLong("active_sessions"),
    logins_ok = o.getLong("logins_ok"),
    logins_failed = o.getLong("logins_failed"),
    ip = if (o.has("ip")) o.getString("ip") else null,
    agent = if (o.has("agent")) o.getString("agent") else null,
)

fun readDailySummaryBodyTotals(o: JSONObject): DailySummaryBodyTotals = DailySummaryBodyTotals(
    events = o.getLong("events"),
    alarms = o.getLong("alarms"),
    serious_alarms = o.getLong("serious_alarms"),
    false_alarms = o.getLong("false_alarms"),
)

fun readDailySummaryBodySeriousAlarms(o: JSONObject): DailySummaryBodySeriousAlarms = DailySummaryBodySeriousAlarms(
    t_s = o.getDouble("t_s"),
    code = if (o.has("code")) o.getString("code") else null,
    zone = if (o.has("zone")) o.getString("zone") else null,
    node = if (o.has("node")) o.getString("node") else null,
    sensor = if (o.has("sensor")) o.getString("sensor") else null,
    severity = if (o.has("severity")) o.getString("severity") else null,
    watts = if (o.has("watts")) o.getDouble("watts") else null,
    value = if (o.has("value")) o.getDouble("value") else null,
    duration_s = if (o.has("duration_s")) o.getDouble("duration_s") else null,
    mean_w = if (o.has("mean_w")) o.getDouble("mean_w") else null,
    limit_w = if (o.has("limit_w")) o.getDouble("limit_w") else null,
)

fun readDailySummaryBodyNodesLinkLost(o: JSONObject): DailySummaryBodyNodesLinkLost = DailySummaryBodyNodesLinkLost(
    node = o.getString("node"),
    count = o.getLong("count"),
    total_s = o.getDouble("total_s"),
)

fun readDailySummaryBodyOutlierReadings(o: JSONObject): DailySummaryBodyOutlierReadings = DailySummaryBodyOutlierReadings(
    t_s = o.getDouble("t_s"),
    node = o.getString("node"),
    sensor = o.getString("sensor"),
    value = o.getDouble("value"),
    median = o.getDouble("median"),
    score = o.getDouble("score"),
)

fun readDailySummaryBodyConsumptionPeaks(o: JSONObject): DailySummaryBodyConsumptionPeaks = DailySummaryBodyConsumptionPeaks(
    t_s = o.getDouble("t_s"),
    code = if (o.has("code")) o.getString("code") else null,
    zone = if (o.has("zone")) o.getString("zone") else null,
    node = if (o.has("node")) o.getString("node") else null,
    sensor = if (o.has("sensor")) o.getString("sensor") else null,
    severity = if (o.has("severity")) o.getString("severity") else null,
    watts = if (o.has("watts")) o.getDouble("watts") else null,
    value = if (o.has("value")) o.getDouble("value") else null,
    duration_s = if (o.has("duration_s")) o.getDouble("duration_s") else null,
    mean_w = if (o.has("mean_w")) o.getDouble("mean_w") else null,
    limit_w = if (o.has("limit_w")) o.getDouble("limit_w") else null,
)

fun readDailySummaryBodyConsumption(o: JSONObject): DailySummaryBodyConsumption = DailySummaryBodyConsumption(
    samples = o.getLong("samples"),
    peaks = o.getJSONArray("peaks").let { a -> (0 until a.length()).map { readDailySummaryBodyConsumptionPeaks(a.getJSONObject(it)) } },
)

fun readDailySummaryBody(o: JSONObject): DailySummaryBody = DailySummaryBody(
    schema = o.getString("schema"),
    totals = readDailySummaryBodyTotals(o.getJSONObject("totals")),
    by_type = o.getJSONObject("by_type").let { m -> m.keys().asSequence().associateWith { m.getLong(it) } },
    by_zone = o.getJSONObject("by_zone").let { m -> m.keys().asSequence().associateWith { m.getLong(it) } },
    by_hour = o.getJSONArray("by_hour").let { a -> (0 until a.length()).map { a.getLong(it) } },
    serious_alarms = if (o.has("serious_alarms")) o.getJSONArray("serious_alarms").let { a -> (0 until a.length()).map { readDailySummaryBodySeriousAlarms(a.getJSONObject(it)) } } else null,
    nodes_link_lost = if (o.has("nodes_link_lost")) o.getJSONArray("nodes_link_lost").let { a -> (0 until a.length()).map { readDailySummaryBodyNodesLinkLost(a.getJSONObject(it)) } } else null,
    outlier_readings = if (o.has("outlier_readings")) o.getJSONArray("outlier_readings").let { a -> (0 until a.length()).map { readDailySummaryBodyOutlierReadings(a.getJSONObject(it)) } } else null,
    consumption = if (o.has("consumption")) readDailySummaryBodyConsumption(o.getJSONObject("consumption")) else null,
)

fun readDailySummaryFindingSubject(o: JSONObject): DailySummaryFindingSubject = DailySummaryFindingSubject(
    code = if (o.has("code")) o.getString("code") else null,
    zone = if (o.has("zone")) o.getString("zone") else null,
    node = if (o.has("node")) o.getString("node") else null,
)

fun readDailySummaryFindingDetail(o: JSONObject): DailySummaryFindingDetail = DailySummaryFindingDetail(
    hours = if (o.has("hours")) o.getJSONArray("hours").let { a -> (0 until a.length()).map { a.getLong(it) } } else null,
    tolerance_min = if (o.has("tolerance_min")) o.getDouble("tolerance_min") else null,
    max_gap_s = if (o.has("max_gap_s")) o.getDouble("max_gap_s") else null,
    limit_s = if (o.has("limit_s")) o.getDouble("limit_s") else null,
    minimum = if (o.has("minimum")) o.getLong("minimum") else null,
    window = if (o.has("window")) o.getLong("window") else null,
    sigma = if (o.has("sigma")) o.getDouble("sigma") else null,
    min_ratio = if (o.has("min_ratio")) o.getDouble("min_ratio") else null,
)

fun readDailySummaryFindingEvidence(o: JSONObject): DailySummaryFindingEvidence = DailySummaryFindingEvidence(
    t_s = o.getDouble("t_s"),
    code = if (o.has("code")) o.getString("code") else null,
    zone = if (o.has("zone")) o.getString("zone") else null,
    node = if (o.has("node")) o.getString("node") else null,
    sensor = if (o.has("sensor")) o.getString("sensor") else null,
    severity = if (o.has("severity")) o.getString("severity") else null,
    watts = if (o.has("watts")) o.getDouble("watts") else null,
    value = if (o.has("value")) o.getDouble("value") else null,
    duration_s = if (o.has("duration_s")) o.getDouble("duration_s") else null,
    mean_w = if (o.has("mean_w")) o.getDouble("mean_w") else null,
    limit_w = if (o.has("limit_w")) o.getDouble("limit_w") else null,
)

fun readDailySummaryFinding(o: JSONObject): DailySummaryFinding = DailySummaryFinding(
    kind = o.getString("kind"),
    subject = readDailySummaryFindingSubject(o.getJSONObject("subject")),
    count = o.getLong("count"),
    detail = readDailySummaryFindingDetail(o.getJSONObject("detail")),
    evidence = o.getJSONArray("evidence").let { a -> (0 until a.length()).map { readDailySummaryFindingEvidence(a.getJSONObject(it)) } },
)

fun readDailySummary(o: JSONObject): DailySummary = DailySummary(
    date = o.getString("date"),
    language = o.getString("language"),
    summary = readDailySummaryBody(o.getJSONObject("summary")),
    findings = o.getJSONArray("findings").let { a -> (0 until a.length()).map { readDailySummaryFinding(a.getJSONObject(it)) } },
    text = o.getString("text"),
    ai_note = if (o.has("ai_note")) o.getString("ai_note") else null,
)

fun readHeatmap(o: JSONObject): Heatmap = Heatmap(
    schema = o.getString("schema"),
    camera_id = o.getString("camera_id"),
    cols = o.getLong("cols"),
    rows = o.getLong("rows"),
    accepted_positions = o.getLong("accepted_positions"),
    rejected_positions = o.getLong("rejected_positions"),
    total = o.getDouble("total"),
    max = o.getDouble("max"),
    weights = o.getJSONArray("weights").let { rows -> (0 until rows.length()).map { r -> rows.getJSONArray(r).let { row -> (0 until row.length()).map { row.getDouble(it) } } } },
    normalized = o.getJSONArray("normalized").let { rows -> (0 until rows.length()).map { r -> rows.getJSONArray(r).let { row -> (0 until row.length()).map { row.getDouble(it) } } } },
    contains_images = o.getBoolean("contains_images"),
)

fun readNetworkInterface(o: JSONObject): NetworkInterface = NetworkInterface(
    name = o.getString("name"),
    ip = o.getString("ip"),
    cidr = o.getString("cidr"),
    gateway = if (o.has("gateway")) o.getString("gateway") else null,
    rx_bps = if (o.has("rx_bps")) o.getLong("rx_bps") else null,
    tx_bps = if (o.has("tx_bps")) o.getLong("tx_bps") else null,
)

fun readNetworkProbe(o: JSONObject): NetworkProbe = NetworkProbe(
    target = o.getString("target"),
    kind = o.getString("kind"),
    ok = o.getBoolean("ok"),
    latency_ms = if (o.has("latency_ms")) o.getDouble("latency_ms") else null,
)

fun readNetworkOutage(o: JSONObject): NetworkOutage = NetworkOutage(
    started_ms = o.getLong("started_ms"),
    ended_ms = o.getLong("ended_ms"),
    duration_s = o.getLong("duration_s"),
)

fun readNetworkInternet(o: JSONObject): NetworkInternet = NetworkInternet(
    state = o.getString("state"),
    since_ms = if (o.has("since_ms")) o.getLong("since_ms") else null,
    gateway_ok = if (o.has("gateway_ok")) o.getBoolean("gateway_ok") else null,
    latency_ms = if (o.has("latency_ms")) o.getDouble("latency_ms") else null,
    loss_percent = if (o.has("loss_percent")) o.getDouble("loss_percent") else null,
    probes = if (o.has("probes")) o.getJSONArray("probes").let { a -> (0 until a.length()).map { readNetworkProbe(a.getJSONObject(it)) } } else null,
    last_outage = if (o.has("last_outage")) readNetworkOutage(o.getJSONObject("last_outage")) else null,
    outages_24h = if (o.has("outages_24h")) o.getLong("outages_24h") else null,
    downtime_24h_s = if (o.has("downtime_24h_s")) o.getLong("downtime_24h_s") else null,
)

fun readNetworkPort(o: JSONObject): NetworkPort = NetworkPort(
    port = o.getLong("port"),
    proto = o.getString("proto"),
    service = if (o.has("service")) o.getString("service") else null,
    banner = if (o.has("banner")) o.getString("banner") else null,
)

fun readNetworkDevice(o: JSONObject): NetworkDevice = NetworkDevice(
    id = o.getString("id"),
    ip = o.getString("ip"),
    mac = if (o.has("mac")) o.getString("mac") else null,
    randomized_mac = if (o.has("randomized_mac")) o.getBoolean("randomized_mac") else null,
    vendor = if (o.has("vendor")) o.getString("vendor") else null,
    hostname = if (o.has("hostname")) o.getString("hostname") else null,
    kind = if (o.has("kind")) o.getString("kind") else null,
    os = if (o.has("os")) o.getString("os") else null,
    online = o.getBoolean("online"),
    first_seen_ms = o.getLong("first_seen_ms"),
    last_seen_ms = o.getLong("last_seen_ms"),
    latency_ms = if (o.has("latency_ms")) o.getDouble("latency_ms") else null,
    ports = if (o.has("ports")) o.getJSONArray("ports").let { a -> (0 until a.length()).map { readNetworkPort(a.getJSONObject(it)) } } else null,
    services = if (o.has("services")) o.getJSONArray("services").let { a -> (0 until a.length()).map { a.getString(it) } } else null,
)

fun readNetworkEvent(o: JSONObject): NetworkEvent = NetworkEvent(
    id = o.getString("id"),
    kind = o.getString("kind"),
    at_ms = o.getLong("at_ms"),
    device_id = if (o.has("device_id")) o.getString("device_id") else null,
    port = if (o.has("port")) o.getLong("port") else null,
    outage_s = if (o.has("outage_s")) o.getLong("outage_s") else null,
    server = if (o.has("server")) o.getString("server") else null,
    recommendation = if (o.has("recommendation")) o.getString("recommendation") else null,
    detail = if (o.has("detail")) o.getString("detail") else null,
)

fun readNetworkScan(o: JSONObject): NetworkScan = NetworkScan(
    last_ms = o.getLong("last_ms"),
    hosts = o.getLong("hosts"),
    duration_ms = if (o.has("duration_ms")) o.getLong("duration_ms") else null,
)

fun readNetworkPublicDns(o: JSONObject): NetworkPublicDns = NetworkPublicDns(
    name = o.getString("name"),
    addresses = o.getJSONArray("addresses").let { a -> (0 until a.length()).map { a.getString(it) } },
    matches = o.getBoolean("matches"),
)

fun readNetworkPublic(o: JSONObject): NetworkPublic = NetworkPublic(
    ip = o.getString("ip"),
    hostname = if (o.has("hostname")) o.getString("hostname") else null,
    city = if (o.has("city")) o.getString("city") else null,
    region = if (o.has("region")) o.getString("region") else null,
    country = if (o.has("country")) o.getString("country") else null,
    org = if (o.has("org")) o.getString("org") else null,
    timezone = if (o.has("timezone")) o.getString("timezone") else null,
    checked_ms = o.getLong("checked_ms"),
    changed_ms = if (o.has("changed_ms")) o.getLong("changed_ms") else null,
    dns = if (o.has("dns")) readNetworkPublicDns(o.getJSONObject("dns")) else null,
)

fun readNetworkResults(o: JSONObject): NetworkResults = NetworkResults(
    id = o.getString("id"),
    type = o.getString("type"),
    ok = o.getBoolean("ok"),
    finished_ms = o.getLong("finished_ms"),
    device_id = if (o.has("device_id")) o.getString("device_id") else null,
    output = if (o.has("output")) o.getString("output") else null,
    ports = if (o.has("ports")) o.getJSONArray("ports").let { a -> (0 until a.length()).map { readNetworkPort(a.getJSONObject(it)) } } else null,
    latency_ms = if (o.has("latency_ms")) o.getDouble("latency_ms") else null,
)

fun readNetwork(o: JSONObject): Network = Network(
    kind = o.getString("kind"),
    node_id = o.getString("node_id"),
    contract = if (o.has("contract")) o.getLong("contract") else null,
    timestamp_ms = o.getLong("timestamp_ms"),
    `interface` = readNetworkInterface(o.getJSONObject("interface")),
    internet = readNetworkInternet(o.getJSONObject("internet")),
    devices = o.getJSONArray("devices").let { a -> (0 until a.length()).map { readNetworkDevice(a.getJSONObject(it)) } },
    events = if (o.has("events")) o.getJSONArray("events").let { a -> (0 until a.length()).map { readNetworkEvent(a.getJSONObject(it)) } } else null,
    scan = if (o.has("scan")) readNetworkScan(o.getJSONObject("scan")) else null,
    public = if (o.has("public")) readNetworkPublic(o.getJSONObject("public")) else null,
    results = if (o.has("results")) o.getJSONArray("results").let { a -> (0 until a.length()).map { readNetworkResults(a.getJSONObject(it)) } } else null,
)

fun readAiObservationRegions(o: JSONObject): AiObservationRegions = AiObservationRegions(
    x = o.getDouble("x"),
    y = o.getDouble("y"),
    w = o.getDouble("w"),
    h = o.getDouble("h"),
)

fun readAiObservation(o: JSONObject): AiObservation = AiObservation(
    camera_id = o.getString("camera_id"),
    severity = o.getString("severity"),
    reasons = o.getJSONArray("reasons").let { a -> (0 until a.length()).map { a.getString(it) } },
    profile = o.getString("profile"),
    motion = o.getDouble("motion"),
    motion_ratio = if (o.has("motion_ratio")) o.getDouble("motion_ratio") else null,
    regions = if (o.has("regions")) o.getJSONArray("regions").let { a -> (0 until a.length()).map { readAiObservationRegions(a.getJSONObject(it)) } } else null,
    radar_tracks = o.getLong("radar_tracks"),
)

fun readDeviceState(o: JSONObject): DeviceState = DeviceState(
    on = o.getBoolean("on"),
)

fun readNetworkOrdersCommands(o: JSONObject): NetworkOrdersCommands = NetworkOrdersCommands(
    id = o.getString("id"),
    type = o.getString("type"),
    device_id = if (o.has("device_id")) o.getString("device_id") else null,
    ip = if (o.has("ip")) o.getString("ip") else null,
    mac = if (o.has("mac")) o.getString("mac") else null,
    port = if (o.has("port")) o.getLong("port") else null,
    auth_sealed = if (o.has("auth_sealed")) o.getString("auth_sealed") else null,
)

fun readNetworkOrders(o: JSONObject): NetworkOrders = NetworkOrders(
    accepted = o.getBoolean("accepted"),
    commands = o.getJSONArray("commands").let { a -> (0 until a.length()).map { readNetworkOrdersCommands(a.getJSONObject(it)) } },
)

fun readServerAlert(o: JSONObject): ServerAlert = ServerAlert(
    service = o.getString("service"),
    event = o.getString("event"),
    at = o.getString("at"),
    mode = o.getString("mode"),
    node_id = if (o.has("node_id")) o.getString("node_id") else null,
    camera_id = if (o.has("camera_id")) o.getString("camera_id") else null,
    targets = if (o.has("targets")) o.getLong("targets") else null,
    minutes = if (o.has("minutes")) o.getLong("minutes") else null,
    alarm_id = if (o.has("alarm_id")) o.getString("alarm_id") else null,
    severity = if (o.has("severity")) o.getString("severity") else null,
    code = if (o.has("code")) o.getString("code") else null,
    device_id = if (o.has("device_id")) o.getString("device_id") else null,
    solar_id = if (o.has("solar_id")) o.getString("solar_id") else null,
    electrical_id = if (o.has("electrical_id")) o.getString("electrical_id") else null,
    alarm_node_id = if (o.has("alarm_node_id")) o.getString("alarm_node_id") else null,
    network_id = if (o.has("network_id")) o.getString("network_id") else null,
    silent = if (o.has("silent")) o.getBoolean("silent") else null,
    automation = if (o.has("automation")) o.getString("automation") else null,
    login_user = if (o.has("login_user")) o.getString("login_user") else null,
    login_from = if (o.has("login_from")) o.getString("login_from") else null,
    login_country = if (o.has("login_country")) o.getString("login_country") else null,
    login_country_new = if (o.has("login_country_new")) o.getBoolean("login_country_new") else null,
)

fun readVisionEventVectors(o: JSONObject): VisionEventVectors = VisionEventVectors(
    track_id = o.getLong("track_id"),
    dx = o.getDouble("dx"),
    dy = o.getDouble("dy"),
    speed = o.getDouble("speed"),
)

fun readVisionEvent(o: JSONObject): VisionEvent = VisionEvent(
    schema = o.getString("schema"),
    type = o.getString("type"),
    camera_id = o.getString("camera_id"),
    zone_id = o.getString("zone_id"),
    zone_name = o.getString("zone_name"),
    track_id = o.getLong("track_id"),
    label = o.getString("label"),
    confidence = o.getDouble("confidence"),
    box = o.getJSONArray("box").let { a -> (0 until a.length()).map { a.getDouble(it) } },
    timestamp = o.getDouble("timestamp"),
    timestamp_ms = o.getLong("timestamp_ms"),
    authorizes_action = o.getBoolean("authorizes_action"),
    radar_tracks = if (o.has("radar_tracks")) o.getLong("radar_tracks") else null,
    vectors = if (o.has("vectors")) o.getJSONArray("vectors").let { a -> (0 until a.length()).map { readVisionEventVectors(a.getJSONObject(it)) } } else null,
)

/** Every message, by the name of its schema: the document read as its data class, or null when it does not satisfy the schema. */
fun parseAiObservation(o: JSONObject): AiObservation? = if (checkMessage("ai_observation", o) == null) readAiObservation(o) else null
fun parseAlarm(o: JSONObject): Alarm? = if (checkMessage("alarm", o) == null) readAlarm(o) else null
fun parseAlarmCommand(o: JSONObject): AlarmCommand? = if (checkMessage("alarm_command", o) == null) readAlarmCommand(o) else null
fun parseAlarmPolicy(o: JSONObject): AlarmPolicy? = if (checkMessage("alarm_policy", o) == null) readAlarmPolicy(o) else null
fun parseAlarmResult(o: JSONObject): AlarmResult? = if (checkMessage("alarm_result", o) == null) readAlarmResult(o) else null
fun parseAlarmZoneFeed(o: JSONObject): AlarmZoneFeed? = if (checkMessage("alarm_zone_feed", o) == null) readAlarmZoneFeed(o) else null
fun parseArmProfile(o: JSONObject): ArmProfile? = if (checkMessage("arm_profile", o) == null) readArmProfile(o) else null
fun parseArmingModes(o: JSONObject): ArmingModes? = if (checkMessage("arming_modes", o) == null) readArmingModes(o) else null
fun parseCommand(o: JSONObject): Command? = if (checkMessage("command", o) == null) readCommand(o) else null
fun parseConnectionClient(o: JSONObject): ConnectionClient? = if (checkMessage("connection_client", o) == null) readConnectionClient(o) else null
fun parseConnectionEvent(o: JSONObject): ConnectionEvent? = if (checkMessage("connection_event", o) == null) readConnectionEvent(o) else null
fun parseDailySummary(o: JSONObject): DailySummary? = if (checkMessage("daily_summary", o) == null) readDailySummary(o) else null
fun parseDeviceState(o: JSONObject): DeviceState? = if (checkMessage("device_state", o) == null) readDeviceState(o) else null
fun parseDiagnosticTokenCreated(o: JSONObject): DiagnosticTokenCreated? = if (checkMessage("diagnostic_token_created", o) == null) readDiagnosticTokenCreated(o) else null
fun parseDiagnosticTokenInfo(o: JSONObject): DiagnosticTokenInfo? = if (checkMessage("diagnostic_token_info", o) == null) readDiagnosticTokenInfo(o) else null
fun parseDiagnosticTokenRequest(o: JSONObject): DiagnosticTokenRequest? = if (checkMessage("diagnostic_token_request", o) == null) readDiagnosticTokenRequest(o) else null
fun parseElectrical(o: JSONObject): Electrical? = if (checkMessage("electrical", o) == null) readElectrical(o) else null
fun parseElectricalCommand(o: JSONObject): ElectricalCommand? = if (checkMessage("electrical_command", o) == null) readElectricalCommand(o) else null
fun parseElectricalResult(o: JSONObject): ElectricalResult? = if (checkMessage("electrical_result", o) == null) readElectricalResult(o) else null
fun parseHealth(o: JSONObject): Health? = if (checkMessage("health", o) == null) readHealth(o) else null
fun parseHeatmap(o: JSONObject): Heatmap? = if (checkMessage("heatmap", o) == null) readHeatmap(o) else null
fun parseInfo(o: JSONObject): Info? = if (checkMessage("info", o) == null) readInfo(o) else null
fun parseNetwork(o: JSONObject): Network? = if (checkMessage("network", o) == null) readNetwork(o) else null
fun parseNetworkOrders(o: JSONObject): NetworkOrders? = if (checkMessage("network_orders", o) == null) readNetworkOrders(o) else null
fun parseNodeControlCommand(o: JSONObject): NodeControlCommand? = if (checkMessage("node_control_command", o) == null) readNodeControlCommand(o) else null
fun parseNodeControlResult(o: JSONObject): NodeControlResult? = if (checkMessage("node_control_result", o) == null) readNodeControlResult(o) else null
fun parseNodeHealth(o: JSONObject): NodeHealth? = if (checkMessage("node_health", o) == null) readNodeHealth(o) else null
fun parseNodeMaintenance(o: JSONObject): NodeMaintenance? = if (checkMessage("node_maintenance", o) == null) readNodeMaintenance(o) else null
fun parseRadarEvent(o: JSONObject): RadarEvent? = if (checkMessage("radar_event", o) == null) readRadarEvent(o) else null
fun parseServerAlert(o: JSONObject): ServerAlert? = if (checkMessage("server_alert", o) == null) readServerAlert(o) else null
fun parseSolarBattery(o: JSONObject): SolarBattery? = if (checkMessage("solar_battery", o) == null) readSolarBattery(o) else null
fun parseSolarBatteryCommand(o: JSONObject): SolarBatteryCommand? = if (checkMessage("solar_battery_command", o) == null) readSolarBatteryCommand(o) else null
fun parseSolarBatteryResult(o: JSONObject): SolarBatteryResult? = if (checkMessage("solar_battery_result", o) == null) readSolarBatteryResult(o) else null
fun parseSolarInverter(o: JSONObject): SolarInverter? = if (checkMessage("solar_inverter", o) == null) readSolarInverter(o) else null
fun parseSolarSystem(o: JSONObject): SolarSystem? = if (checkMessage("solar_system", o) == null) readSolarSystem(o) else null
fun parseSystemEvent(o: JSONObject): SystemEvent? = if (checkMessage("system_event", o) == null) readSystemEvent(o) else null
fun parseTelemetry(o: JSONObject): Telemetry? = if (checkMessage("telemetry", o) == null) readTelemetry(o) else null
fun parseVisionEvent(o: JSONObject): VisionEvent? = if (checkMessage("vision_event", o) == null) readVisionEvent(o) else null
fun parseVoiceTurnMeta(o: JSONObject): VoiceTurnMeta? = if (checkMessage("voice_turn_meta", o) == null) readVoiceTurnMeta(o) else null
fun parseVoiceTurnResult(o: JSONObject): VoiceTurnResult? = if (checkMessage("voice_turn_result", o) == null) readVoiceTurnResult(o) else null

/** The document as the message called `name` (the name of its schema file): its data class, or null when it does not satisfy the schema or the name is not known. */
fun parseMessage(name: String, o: JSONObject): Any? = when (name) {
    "ai_observation" -> parseAiObservation(o)
    "alarm" -> parseAlarm(o)
    "alarm_command" -> parseAlarmCommand(o)
    "alarm_policy" -> parseAlarmPolicy(o)
    "alarm_result" -> parseAlarmResult(o)
    "alarm_zone_feed" -> parseAlarmZoneFeed(o)
    "arm_profile" -> parseArmProfile(o)
    "arming_modes" -> parseArmingModes(o)
    "command" -> parseCommand(o)
    "connection_client" -> parseConnectionClient(o)
    "connection_event" -> parseConnectionEvent(o)
    "daily_summary" -> parseDailySummary(o)
    "device_state" -> parseDeviceState(o)
    "diagnostic_token_created" -> parseDiagnosticTokenCreated(o)
    "diagnostic_token_info" -> parseDiagnosticTokenInfo(o)
    "diagnostic_token_request" -> parseDiagnosticTokenRequest(o)
    "electrical" -> parseElectrical(o)
    "electrical_command" -> parseElectricalCommand(o)
    "electrical_result" -> parseElectricalResult(o)
    "health" -> parseHealth(o)
    "heatmap" -> parseHeatmap(o)
    "info" -> parseInfo(o)
    "network" -> parseNetwork(o)
    "network_orders" -> parseNetworkOrders(o)
    "node_control_command" -> parseNodeControlCommand(o)
    "node_control_result" -> parseNodeControlResult(o)
    "node_health" -> parseNodeHealth(o)
    "node_maintenance" -> parseNodeMaintenance(o)
    "radar_event" -> parseRadarEvent(o)
    "server_alert" -> parseServerAlert(o)
    "solar_battery" -> parseSolarBattery(o)
    "solar_battery_command" -> parseSolarBatteryCommand(o)
    "solar_battery_result" -> parseSolarBatteryResult(o)
    "solar_inverter" -> parseSolarInverter(o)
    "solar_system" -> parseSolarSystem(o)
    "system_event" -> parseSystemEvent(o)
    "telemetry" -> parseTelemetry(o)
    "vision_event" -> parseVisionEvent(o)
    "voice_turn_meta" -> parseVoiceTurnMeta(o)
    "voice_turn_result" -> parseVoiceTurnResult(o)
    else -> null
}
