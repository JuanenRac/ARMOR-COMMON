#!/usr/bin/env bash
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/armor-project.sh" build-test "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
