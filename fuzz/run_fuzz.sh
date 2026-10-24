#!/usr/bin/env bash
# Builds the libFuzzer targets of the shared firmware code with clang (AddressSanitizer + UndefinedBehaviorSanitizer) and runs each one for a while.
#   bash fuzz/run_fuzz.sh [seconds per target, default 20]
# Needs clang with libFuzzer (Linux). The seed inputs are in fuzz/corpus/<target>/; new findings are written to fuzz/artifacts/ and are not kept in the repository.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
seconds="${1:-20}"
out="${FUZZ_BUILD_DIR:-$here/build}"
mkdir -p "$out" "$here/artifacts"
status=0
for target in fuzz_json fuzz_ble_frame fuzz_improv; do
  clang++ -std=c++17 -O1 -g -fno-omit-frame-pointer -fsanitize=fuzzer,address,undefined -fno-sanitize-recover=undefined \
    "$here/$target.cpp" -o "$out/$target"
  work="$out/work_$target"; mkdir -p "$work"
  cp -r "$here/corpus/$target/." "$work/" 2>/dev/null || true
  echo "== $target: ${seconds} s"
  "$out/$target" -max_total_time="$seconds" -max_len=8192 -artifact_prefix="$here/artifacts/${target}_" "$work" || status=1
done
exit "$status"
