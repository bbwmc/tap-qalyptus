# tap-qalyptus

Custom Singer tap for Qalyptus, built with the Meltano Singer SDK.

This repo currently includes the v1 scaffold plus working streams for:

- `users`
- `groups`
- `projects`
- `filters`
- `reports`
- `tasks`
- `task_recipients`
- `task_reports`
- `task_report`
- `task_triggers`
- `report_objects`
- `report_filters`

The tap uses full-refresh replication and preserves nested payloads with permissive schemas during the first production cut.

## Status

- Full-refresh only
- `Authorization: Bearer <token>` verified against the live API
- Stream discovery includes both top-level and child streams
- Generic schemas with `additionalProperties: true` to preserve nested source payloads during the initial spike

## Configuration

The tap expects a config file like:

```json
{
  "api_url": "https://bedsandbars.qalyptus.net/api/v1",
  "api_key": "REPLACE_ME",
  "api_key_header": "Authorization",
  "request_timeout": 60
}
```

Notes:

- `api_url` accepts either the tenant root URL or the `/api/v1` base URL.
- `api_key` is sent as a bearer token when `api_key_header` is `Authorization`.
- The current live tenant expects `Authorization: Bearer <token>`.
- If another tenant differs, you can still override `api_key_header` and pass a complete header value.

## Local development

Install the package in editable mode:

```bash
python -m pip install -e '.[dev]'
```

Discover the catalog:

```bash
tap-qalyptus --config config.json --discover
```

Run the test suite:

```bash
pytest
```

## Design notes

- The tap normalizes `api_url` onto the `/api/v1` base path.
- Top-level endpoints are treated as simple GET collection endpoints.
- The live API wraps responses as `data`, `isSuccess`, `error`, and `errorDetails`.
- `task_report` comes from `/tasks/{task_id}/reports/{task_report_id}` and preserves nested `filters`.
- `report_objects` flattens `template-items` from `data.nodes[*].objects` into one row per object and carries `report_id`, `parent_object_id`, and node metadata.
- Pagination is disabled for now until the live API proves the actual mechanism.

## Remote Meltano integration

Recommended first cutover path:

1. Install this tap from git in `ssh etl:~/bbgmeltano-new`.
2. Load into a new raw schema first.
3. Compare counts and downstream dbt behavior before replacing `ab_source__qalyptus`.

## Pending live verification

See `docs/live-api-spike.md` for the confirmed auth/result shape notes and remaining pagination questions.
