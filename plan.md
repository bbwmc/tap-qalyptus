# tap-qalyptus plan

## Goal

Build a small custom Singer/Meltano tap for Qalyptus to replace the dead Airbyte load that currently populates `frigg.ab_source__qalyptus`.

This should be treated as a production connector project, not just a one-off script.

## Why build a tap instead of using `tap-rest-api-msdk`

- Qalyptus is not just a set of flat list endpoints; several required datasets are parent-child fan-outs.
- We need stable stream naming and key behavior to preserve the existing warehouse/dbt contract.
- The Qalyptus docs are beta and sparse on exact response bodies, auth header details, and pagination/incremental behavior.
- The total data volume is small enough that a full-refresh custom tap is practical and lower risk.

`tap-rest-api-msdk` is still fine as a quick live API probe, but not recommended as the final production connector.

## Current warehouse contract

The current raw schema is `ab_source__qalyptus` in Frigg.

Live tables seen there:

- `filters` (~97 rows)
- `groups` (~5 rows)
- `projects` (~11 rows)
- `report_filters` (~983 rows)
- `report_objects` (~320 rows)
- `reports` (~80 rows)
- `task_recipients` (~340 rows)
- `task_report` (~85 rows)
- `task_reports` (~75 rows)
- `task_triggers` (~55 rows)
- `tasks` (~71 rows)
- `users` (~165 rows)

The last Airbyte extract timestamp across these tables is on `2025-07-23`, so the source is stale.

## Important downstream references in `bifrost`

Existing dbt source declaration:

- `/home/t4/work/bbg/bifrost/models/stg/qalyptus/_src.yml`

Important staging models:

- `/home/t4/work/bbg/bifrost/models/stg/qalyptus/stg_qalyptus__report_filters.sql`
- `/home/t4/work/bbg/bifrost/models/stg/qalyptus/stg_qalyptus__task_reports.sql`

Notable quirks:

- `stg_qalyptus__report_filters.sql` currently derives report-filter links from `source('qalyptus', 'task_report')`, specifically from the `filters` JSON array on `task_report`, not from the raw `report_filters` table.
- `stg_qalyptus__task_reports.sql` currently uses `task_reports.task_id` as the modeled `id`, not `task_reports.id`.
- Raw `task_report` appears to contain duplicate `id` values with different `_airbyte_extracted_at` values, so key semantics need to be checked carefully.

Do not assume the existing Airbyte shape is perfectly correct. Preserve behavior intentionally, not accidentally.

## Where this work lives

Create the tap in this local repo path:

- `/home/t4/work/bbg/tap-qalyptus`

The deployment/integration target is a different repo on the SSH ETL host:

- `ssh etl:~/bbgmeltano-new`

That repo is not local here. Do not assume it can be edited from this repo without SSHing in.

## Remote Meltano context

Observed on `ssh etl:~/bbgmeltano-new`:

- custom extractors are defined directly in `meltano.yml`
- there is already a pattern of custom taps installed from git URLs
- runs are triggered by simple shell wrappers like `mews.sh` and `stripe.sh`
- loader is `target-postgres`

Plan for this tap to be installable from git so it can be added there cleanly.

## Qalyptus API facts gathered so far

From the docs:

- auth is API-key based
- API base path is `/api/v1`
- the docs do not clearly show the auth header name/security scheme in the captured output
- pagination/incremental support is not obvious from the docs

Likely top-level GET endpoints:

- `GET /api/v1/users`
- `GET /api/v1/groups`
- `GET /api/v1/projects`
- `GET /api/v1/filters`
- `GET /api/v1/reports`
- `GET /api/v1/tasks`

Likely child/fan-out endpoints:

- `GET /api/v1/tasks/{task_id}/recipients`
- `GET /api/v1/tasks/{task_id}/reports`
- `GET /api/v1/tasks/{task_id}/reports/{task_report_id}`
- `GET /api/v1/tasks/{task_id}/triggers`
- `GET /api/v1/filters/report/{report_id}`
- `GET /api/v1/reports/{report_id}/template-items`

Open questions to verify against the live API:

- exact tenant base URL
- exact API key header name
- exact response schema for child endpoints
- whether `report_objects` should come from `template-items`, `objects`, or both
- whether there is any usable pagination or incremental filter support

## Recommended tap scope v1

Build v1 as full refresh only.

Top-level streams:

- `users`
- `groups`
- `projects`
- `filters`
- `reports`
- `tasks`

Child streams:

- `task_recipients`
- `task_reports`
- `task_report`
- `task_triggers`
- `report_objects`

Optional stream for parity only:

- `report_filters`

Note: `report_filters` is lower priority because downstream dbt currently derives this relationship from `task_report.filters` instead.

## Suggested connector design

Use the Meltano SDK.

Project shape:

- `pyproject.toml`
- package directory, e.g. `tap_qalyptus/`
- `tap_qalyptus/tap.py`
- `tap_qalyptus/client.py` or `streams/base.py`
- stream modules under `tap_qalyptus/streams/`
- tests with canned JSON fixtures

Suggested config settings:

- `api_url`
- `api_key`
- `api_key_header`
- `request_timeout`
- `start_date` (optional placeholder; likely unused in v1)

Implementation notes:

- make child streams depend on parent streams and carry the parent ID through in emitted records
- keep v1 simple and explicit rather than over-abstracting
- use full refresh replication for every stream unless the live API proves a safe incremental path
- include retries/backoff for rate limits and transient failures
- prefer explicit schemas where the payloads are small and stable enough to model

## Proposed build order

1. Bootstrap the package and CLI entry point.
2. Implement auth and a reusable base REST stream.
3. Add top-level streams: `users`, `groups`, `projects`, `filters`, `reports`, `tasks`.
4. Run a live API probe to confirm actual response shapes.
5. Add child streams: `task_recipients`, `task_reports`, `task_report`, `task_triggers`, `report_objects`.
6. Decide whether `report_filters` should be emitted as its own raw stream.
7. Add tests and fixtures.
8. Write a short README with config and local run instructions.
9. Prepare integration notes for `bbgmeltano-new`.

## Validation checklist

Before handing off to ETL/Meltano integration, verify:

- `tap-qalyptus --discover` works
- each stream can emit records locally
- child streams correctly fan out from parent IDs
- primary key behavior is sane, especially for `task_report`
- row counts are in the same ballpark as the old Airbyte load
- nested JSON fields needed downstream are preserved

## Cutover options

There are two reasonable cutover paths:

1. Recommended: load into a new raw schema such as `tap_qalyptus`, then update dbt sources or create compatibility views.
2. Compatibility-first: load directly into `ab_source__qalyptus` with matching table names.

Do not choose this casually. The current dbt source points at `ab_source__qalyptus`, so schema choice affects cutover effort.

## Suggested next task for the implementing agent

Start by scaffolding the tap repo and then do a live API verification spike before writing all child streams.

Concrete first deliverable:

- a runnable `tap-qalyptus` package that can authenticate and `--discover`
- working top-level streams for `users`, `groups`, `projects`, `filters`, `reports`, and `tasks`
- notes on the confirmed auth header and endpoint/response shapes for the child streams
