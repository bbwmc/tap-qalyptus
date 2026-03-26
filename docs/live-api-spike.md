# Live API spike notes

These notes capture the first credentialed API probe against `bedsandbars.qalyptus.net`.

## Confirmed so far

- Tenant example: `https://bedsandbars.qalyptus.net`
- API prefix: `/api/v1`
- Auth header: `Authorization: Bearer <token>`
- Top-level endpoints verified:
  - `GET /users` -> `data` list
  - `GET /groups` -> `data` list
  - `GET /projects` -> `data` list
  - `GET /filters` -> `data` list
  - `GET /reports` -> `data` list
  - `GET /tasks` -> `data` list
- Response wrapper shape is consistently:
  - `data`
  - `isSuccess`
  - `error`
  - `errorDetails`
- Sample live row counts observed during probing:
  - `users`: 219
  - `groups`: 6
  - `projects`: 11
  - `filters`: 102
  - `reports`: 89
  - `tasks`: 79
- Child endpoints verified:
  - `GET /tasks/{task_id}/recipients` -> `data` list
  - `GET /tasks/{task_id}/reports` -> `data` list
  - `GET /tasks/{task_id}/reports/{task_report_id}` -> `data` object
  - `GET /tasks/{task_id}/triggers` -> `data` list
  - `GET /filters/report/{report_id}` -> `data` list of filter objects
  - `GET /reports/{report_id}/template-items` -> `data.nodes[*].objects` tree

## Shape notes

- `task_reports` records include both `id` and `reportID`.
- `task_report` detail records preserve nested arrays like `filters`, `conditions`, and `storageServices`.
- `report_filters` is not a link table response; it returns full filter objects for a report.
- `report_objects` should be derived by flattening the `template-items` object tree rather than using the top-level node wrappers as rows.

## Still pending live verification

- Whether pagination exists and, if so, how it is exposed
- Full child row-count parity against the historical Airbyte tables
- Final primary-key choice review for `task_report` during warehouse validation

## Current implementation assumptions

- Full refresh is the safest initial replication strategy
- Payloads may contain nested JSON which should be preserved as-is
- `report_objects` rows should carry `report_id`, `parent_object_id`, and node metadata after flattening
