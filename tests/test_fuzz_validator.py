"""The validators meet damaged messages: whatever is done to a valid message, the answer is "accepted" or a ContractError, never another kind of exception.

A message from the broker is written by a device (or by whoever reached it), so a validator that fails with a TypeError or a KeyError on an odd value is a way to crash the
program that reads it. The mutations are seeded, so a failure repeats.
"""
import copy
import json
import random
import unittest
from pathlib import Path

from armor_common import ContractError
from armor_common.contracts import validate_payload

import test_contracts as contracts

CONFORMANCE = Path(__file__).resolve().parent.parent / "conformance"
ODD = [None, True, False, 0, -1, 2 ** 70, 1.5, -0.0, "", " ", "x" * 5000, "\u0000", "😀", [], {}, [None], {"a": {"b": [1, 2, {"c": None}]}}, [[[[]]]], "armor/../x", "0" * 400]


def paths(value, prefix=()):
    yield prefix
    if isinstance(value, dict):
        for key, item in value.items():
            yield from paths(item, prefix + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value[:6]):
            yield from paths(item, prefix + (index,))


def mutate(payload, rng):
    result = copy.deepcopy(payload)
    options = [path for path in paths(result) if path]
    if not options:
        return rng.choice(ODD)
    path = rng.choice(options)
    parent = result
    for step in path[:-1]:
        parent = parent[step]
    action = rng.choice(["replace", "replace", "delete", "add"])
    if action == "delete" and isinstance(parent, dict):
        del parent[path[-1]]
    elif action == "delete" and isinstance(parent, list):
        parent.pop(path[-1])
    elif action == "add" and isinstance(parent, dict):
        parent[rng.choice(["extra", "id", "node_id", "state", ""])] = rng.choice(ODD)
    else:
        parent[path[-1]] = rng.choice(ODD)
    return result


class DamagedMessages(unittest.TestCase):
    def test_a_damaged_message_is_accepted_or_refused_with_a_contract_error(self):
        rng = random.Random(20260101)
        checked = 0
        for file in sorted(CONFORMANCE.glob("*.json")):
            document = json.loads(file.read_text(encoding="utf-8"))
            kind = document.get("kind")
            if not kind or "vectors" not in document:
                continue
            valid = [vector["payload"] for vector in document["vectors"] if vector["valid"]]
            rule = contracts.MESSAGE_RULES.get(kind)
            for payload in valid[:4]:
                for _ in range(60):
                    damaged = payload
                    for _ in range(rng.choice([1, 1, 2, 3])):
                        damaged = mutate(damaged, rng)
                    with self.subTest(kind=kind):
                        try:
                            validate_payload(kind, damaged)
                            if rule:
                                rule(damaged)
                        except ContractError:
                            pass
                        except RecursionError:
                            self.fail(f"{kind}: a deep message exhausted the stack: {json.dumps(damaged)[:200]}")
                        except Exception as error:   # noqa: BLE001 - this is what the test is for
                            self.fail(f"{kind}: {type(error).__name__}: {error} on {json.dumps(damaged, default=str)[:300]}")
                    checked += 1
        self.assertGreater(checked, 1500)


if __name__ == "__main__":
    unittest.main()
