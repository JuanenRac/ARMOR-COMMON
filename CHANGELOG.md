# Changelog

All notable changes to this project are documented here.

## [0.5.0] - OpenAPI 0.5.0

- `armor-server-0.5.0.yaml`: `/api/v1/history/summary`, `DELETE /api/v1/history`, the new history filters, and the PTZ semantics (auto-stop, honest errors).

## [0.4.0] - OpenAPI 0.4.0

- `armor-server-0.4.0.yaml`: `/api/v1/camera-status`, `DELETE /api/v1/nodes/{id}`, the `camera` event type, and `/api/v1/status` now needing an operator.

## [0.3.0] - OpenAPI 0.3.0

- `openapi/armor-server-0.3.0.yaml` (replaces 0.2.0) adds `GET /api/v1/history` and `GET`/`PUT /api/v1/rules` with the `Rules` schema.

## [0.2.0] - Schemas as the single source of truth

- The JSON Schemas are now packaged with the library and interpreted directly by a small validator that refuses any schema keyword it does not implement, so a constraint can never be silently skipped.
- The Python validator used to be weaker than the published schemas (it did not check lux range, integer timestamps, sensor 1-3, the node-id pattern or unknown fields); it now enforces all of them.
- Added `command.schema.json` (allow-listed commands, optional sensitivity 1-10).
- Added 50 shared conformance vectors. ARMOR-SERVER runs them too, which found and fixed a real drift: the server used to ignore unknown fields.
- Added generated TypeScript and Kotlin types (`tools/generate_types.py`, `--check` for CI).
- Replaced the 0.1.0 OpenAPI file with `armor-server-0.2.0.yaml`, covering every route and access rule of ARMOR-SERVER.
- 16 tests (previously 3).

## [0.1.0]

- First functional baseline: topic parsing, telemetry/health validation and deterministic envelopes.
