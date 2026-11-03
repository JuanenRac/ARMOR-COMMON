# Testing strategy: property-based tests and mutation checks of the validators

The validators of the contract are the gate between a device that can say anything and the program that acts on what it says. Besides the hand-written cases, the shared conformance vectors and the libFuzzer targets of the firmware parsers (see [FUZZING.md](FUZZING.md)), they are tested with property-based tests.

## Property-based tests

`tests/test_property_validators.py` states rules that must hold for every input and checks them on generated cases. The cases come from a small generator with a fixed seed (`random.Random`), so a run is the same on every machine, nothing is installed to run it, and the whole file takes about one second. The rules:

| Area | Rule checked on generated inputs |
| --- | --- |
| Topic and node id | `parse_topic` accepts exactly `armor/node/{node_id}/{kind}` with a known kind and a node id of lowercase letters, digits, `-` and `_`, not starting with `-` or `_`, at most 64 characters; the node id of the payload must be the one of the topic |
| Command | `sensitivity` is accepted only on `set_thresholds` and only as a whole number from 1 to 10 (a boolean never is); only `calibrate`, `set_thresholds` and `restart` exist |
| Control operations | the duration of `pause`, `identify` and `maintenance_on` stays inside its range, and only on an execute |
| Schemas | for every schema with a conformance vector: no number outside a stated `minimum` / `maximum` is accepted (and both limits are), a boolean, a text or `null` is never taken for a number, a value outside a stated `enum` is refused |
| Untrusted lines | `decode` answers a `ValueError` (a `ContractError` is one) to any text, damaged valid lines, truncated lines and documents nested thousands of levels deep, and whatever it accepts is a valid message; a repeated name is refused; a structured fuzz of a valid command is accepted or refused with a `ContractError`, never another error |

## Mutation checks (local only)

Mutation testing changes the code of a module in small ways (a `<` for a `<=`, a constant, a condition) and runs the tests: a change the tests do not notice is a behaviour nobody checks. It is a measure of the tests, not a part of the build: it is **not** run in the CI. To repeat it, in a throwaway virtual environment (mutmut 2 counts only the exit code 1 of the test command as a kill, so use a runner that maps every failing exit code to 1):

```
python -m pip install "mutmut<3" pytest
mutmut run --paths-to-mutate src/armor_common/contracts.py --runner "python runner.py tests/test_property_validators.py tests/test_contracts.py tests/test_fuzz_validator.py"
mutmut results
```

The file is large, so the run was limited to the topic and node id checks and `validate_topic_and_payload` (the other lines marked with `# pragma: no mutate` in a scratch copy).

| Target | Mutants | Killed by the first run | Killed after the added tests | Left |
| --- | --- | --- | --- | --- |
| `_check_node_id`, `parse_topic`, `validate_topic_and_payload` | 44 | 35 (79.5 %) | 43 (97.7 %) | 1, equivalent |

The mutants that survived the first run were the texts of the refusals (the readers show them, so the tests now compare them) and the character set used up to its last member. The one left is `node_id[0] in "-_"` written as `in "XX-_XX"`, which answers the same for a single character.
