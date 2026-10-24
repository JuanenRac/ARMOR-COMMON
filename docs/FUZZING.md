# Fuzzing the parsers of the node firmware

The code every node uses to read what arrives from outside is pure C++ (no ESP-IDF), so it can be fuzzed on a computer with clang and libFuzzer:

| Target | What it reads | What must always hold |
|---|---|---|
| `fuzz/fuzz_json.cpp` | the JSON parser (`core/json.hpp`) | any text is refused or gives a document that, written and read again, has the same shape; no crash, no undefined behaviour |
| `fuzz/fuzz_ble_frame.cpp` | the Bluetooth set-up channel (`core/ble_frame.hpp`): the message assembler fed in slices of any size, then the request parser | no crash; a request has an operation of 1 to 32 characters and an id of 0 or more; the buffer never holds more than one message plus one write |
| `fuzz/fuzz_improv.cpp` | the Improv serial parser and the RPC reader (`core/improv.hpp`) | only packets with a right checksum come out; a Wi-Fi command has an SSID of 1 to 32 and a password of up to 63 characters |

Run them (Linux or WSL, clang with libFuzzer, AddressSanitizer and UndefinedBehaviorSanitizer):

```bash
bash fuzz/run_fuzz.sh 20      # 20 seconds per target
```

The seeds are in `fuzz/corpus/<target>/`. A failing input is written to `fuzz/artifacts/` (not tracked): copy it into the corpus together with the fix. The workflow `.github/workflows/fuzz.yml` runs every target for 30 seconds when the shared code or the targets change.
