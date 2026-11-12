# Readers and writers of the messages

The JSON Schemas in `src/armor_common/schemas/` are the single source of truth for every message. Four generated files read and write the messages from them, and none is edited by hand.

| File | Made by | What it holds |
|---|---|---|
| `generated/armor-contracts.ts`, `generated/ArmorContracts.kt` | `tools/generate_types.py` | the types of every message |
| `generated/armor_wire.hpp` | `tools/generate_wire.py` | C++: a struct, `validate_<schema>`, `parse_<schema>` and `write_<schema>` for each schema, and `validate_message(name, value)` / `rewrite_message(name, value, out)` by name |
| `generated/armor-parsers.ts` | `tools/generate_parsers.py` | TypeScript: `parseMessage(name, value)` (typed or a `ContractError` with the path) and `checkMessage` |
| `generated/ArmorParsers.kt` | `tools/generate_kotlin_parsers.py` | Kotlin over `org.json`: `checkMessage(name, value)`, `read<Message>(JSONObject)` into the data class and `parse<Message>(JSONObject)` (null when not valid) |
| `generated/ArmorContract.swift` | `tools/generate_swift_parsers.py` | Swift over `JSONSerialization`, inside the namespace `Contract`: a struct for each message with `init(reading:)` and `toJSON()`, `check(name, document)`, `parse<Message>(document)` (nil when not valid), `parse(name, document)` and `rewrite(name, document)` |

`armor_wire.hpp` needs only `json.hpp` of the shared firmware. The schema is a table that a few lines of C++ interpret (type, enum, const, limits, lengths in code points, required members, unknown members, a map of one kind of value); the patterns are compiled by `tools/wire_regex.py` into a small automaton over code points, which runs without recursion and with one flag per state. A pattern outside the supported subset stops the generator, so a constraint is never ignored without notice.

## The topics

`src/armor_common/mqtt_topics.json` is the one list of the MQTT topics: the address, the schema of the messages, who publishes, who reads, the QoS and whether the broker keeps the message. `tools/generate_asyncapi.py` makes `asyncapi/armor-mqtt.asyncapi.json` from it and from the access lines of `node_roles.json`: AsyncAPI 3.0 with a channel per topic, an operation per role and channel (`send` or `receive`, with its `qos` and `retain`), and `x-acl` with the lines of every role. A topic whose commands exist only when an option is turned on (`alarm-commands`, `electrical-switching`, `battery-write`) says which in `x-opt-in`. `tests/test_mqtt_topics.py` keeps the list and the access lines saying the same thing.

## The oracle

`tools/make_wire_cases.py` writes `conformance/wire_cases.tsv`: the valid vectors of `conformance/` and seeded mutations of them, one case per line (`schema`, `1` or `0`, the document), with the verdict of the Python validator `armor_common.schema`. The same bytes are written on every run.

* `host_tests/test_wire_oracle.cpp` (`ctest`) runs every case through the C++ validator, reads each valid one into its struct, writes it back and checks that the text is valid, that writing twice gives the same text and, with `tools/check_wire_rewrites.py`, that it equals the document without the members the schema does not name.
* The Swift readers and writers of the iPhone app run both files of cases: the verdict of each, every valid case read, written back equal to the document without the members the schema does not name, and the same text when written twice.
* The TypeScript parsers and the hand-written readers of the server are run against the same file by the tests of the repositories that use them.
* A node project runs the cases through the parsers it has written by hand for the messages it receives: a parser must not accept what the contract refuses.

Run the host test:

```bash
cmake -S host_tests -B build && cmake --build build && ctest --test-dir build --output-on-failure
python tools/check_wire_rewrites.py build/wire_rewrites.tsv
```
