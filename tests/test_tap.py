"""Tests for tap-qalyptus."""

from __future__ import annotations

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from tap_qalyptus.client import normalize_api_url
from tap_qalyptus.streams.child import ReportObjectsStream, TaskReportStream
from tap_qalyptus.streams.top_level import ReportsStream, UsersStream
from tap_qalyptus.tap import TapQalyptus

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _fixture(name: str):
    return json.loads((FIXTURES_DIR / name).read_text())


class _FixtureAPIHandler(BaseHTTPRequestHandler):
    expected_header_name = "Authorization"
    expected_header_value = "Bearer test-token"
    routes = {}

    def do_GET(self):
        if self.headers.get(self.expected_header_name) != self.expected_header_value:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "unauthorized"}')
            return

        payload = self.routes.get(self.path)
        if payload is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not_found"}')
            return

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A003
        return


@contextmanager
def _serve_fixture_api(*, routes, header_name="Authorization", header_value="Bearer test-token"):
    handler = type("FixtureAPIHandler", (_FixtureAPIHandler,), {})
    handler.routes = routes
    handler.expected_header_name = header_name
    handler.expected_header_value = header_value

    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join()


def test_discover_stream_names():
    tap = TapQalyptus(
        config={
            "api_url": "https://bedsandbars.qalyptus.net",
            "api_key": "test-token",
        }
    )

    assert [stream.name for stream in tap.discover_streams()] == [
        "users",
        "groups",
        "projects",
        "filters",
        "reports",
        "report_filters",
        "report_objects",
        "tasks",
        "task_recipients",
        "task_reports",
        "task_report",
        "task_triggers",
    ]


def test_normalize_api_url_accepts_root_or_endpoint_url():
    assert normalize_api_url("https://bedsandbars.qalyptus.net") == (
        "https://bedsandbars.qalyptus.net/api/v1/"
    )
    assert normalize_api_url("https://bedsandbars.qalyptus.net/api/v1/projects") == (
        "https://bedsandbars.qalyptus.net/api/v1/"
    )


def test_users_stream_requests_records_with_custom_header():
    routes = {"/api/v1/users": _fixture("users.json")}
    with _serve_fixture_api(routes=routes, header_name="X-API-Key", header_value="token-123") as api_url:
        tap = TapQalyptus(
            config={
                "api_url": api_url,
                "api_key": "token-123",
                "api_key_header": "X-API-Key",
            }
        )

        records = list(UsersStream(tap).get_records(None))

    assert [record["id"] for record in records] == [1, 2]
    assert records[0]["groups"] == [1, 2]


def test_reports_stream_parses_wrapped_payloads():
    routes = {"/api/v1/reports": _fixture("reports_wrapped.json")}
    with _serve_fixture_api(routes=routes) as api_url:
        tap = TapQalyptus(
            config={
                "api_url": api_url,
                "api_key": "test-token",
            }
        )

        records = list(ReportsStream(tap).get_records(None))

    assert [record["id"] for record in records] == [101, 102]
    assert records[0]["filters"][0]["label"] == "Active only"


def test_discovery_schemas_include_business_fields():
    tap = TapQalyptus(
        config={
            "api_url": "https://bedsandbars.qalyptus.net",
            "api_key": "test-token",
        }
    )

    users_schema = UsersStream(tap).schema["properties"]
    task_report_schema = TaskReportStream(tap).schema["properties"]
    report_objects_schema = ReportObjectsStream(tap).schema["properties"]

    assert {"id", "name", "email", "groups", "organizationRoles"} <= set(users_schema)
    assert {"task_id", "id", "filters", "reportID", "separatorOptions"} <= set(task_report_schema)
    assert {"report_id", "name", "type", "icon", "objects"} <= set(report_objects_schema)


def test_task_report_stream_parses_detail_payload_and_context_fields():
    routes = {"/api/v1/tasks/task-1/reports/task-report-1": _fixture("task_report_detail.json")}
    with _serve_fixture_api(routes=routes) as api_url:
        tap = TapQalyptus(
            config={
                "api_url": api_url,
                "api_key": "test-token",
            }
        )

        records = list(
            TaskReportStream(tap).get_records(
                {"task_id": "task-1", "task_report_id": "task-report-1"}
            )
        )

    assert len(records) == 1
    assert records[0]["task_id"] == "task-1"
    assert records[0]["filters"][0]["id"] == "filter-1"


def test_report_objects_stream_flattens_nested_template_items():
    routes = {"/api/v1/reports/report-1/template-items": _fixture("template_items.json")}
    with _serve_fixture_api(routes=routes) as api_url:
        tap = TapQalyptus(
            config={
                "api_url": api_url,
                "api_key": "test-token",
            }
        )

        records = list(ReportObjectsStream(tap).get_records({"report_id": "report-1"}))

    assert len(records) == 1
    assert records[0]["report_id"] == "report-1"
    assert records[0]["name"] == "Table"
    assert records[0]["type"] == "table"
    assert records[0]["icon"] == "table.svg"
    assert records[0]["objects"][0]["id"] == "object-parent-1"
