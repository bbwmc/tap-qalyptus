"""Child Qalyptus streams."""

from __future__ import annotations

from collections.abc import Iterable
import decimal
from typing import Any

from tap_qalyptus.client import QalyptusChildStream
from tap_qalyptus.schemas import (
    REPORT_FILTERS_SCHEMA,
    REPORT_OBJECTS_SCHEMA,
    TASK_RECIPIENTS_SCHEMA,
    TASK_REPORT_SCHEMA,
    TASK_REPORTS_SCHEMA,
    TASK_TRIGGERS_SCHEMA,
)
from tap_qalyptus.streams.top_level import ReportsStream, TasksStream


class TaskRecipientsStream(QalyptusChildStream):
    name = "task_recipients"
    parent_stream_type = TasksStream
    path = "tasks/{task_id}/recipients"
    key_properties = ("task_id", "id")
    record_schema = TASK_RECIPIENTS_SCHEMA
    context_fields = {"task_id": "task_id"}


class TaskReportsStream(QalyptusChildStream):
    name = "task_reports"
    parent_stream_type = TasksStream
    path = "tasks/{task_id}/reports"
    key_properties = ("task_id", "id")
    record_schema = TASK_REPORTS_SCHEMA
    context_fields = {"task_id": "task_id"}

    def get_child_context(self, record, context):
        task_id = (context or {}).get("task_id") or record.get("task_id")
        if not task_id or "id" not in record:
            return None
        return {"task_id": task_id, "task_report_id": record["id"]}


class TaskReportStream(QalyptusChildStream):
    name = "task_report"
    parent_stream_type = TaskReportsStream
    path = "tasks/{task_id}/reports/{task_report_id}"
    key_properties = ("task_id", "id")
    record_schema = TASK_REPORT_SCHEMA
    context_fields = {"task_id": "task_id"}


class TaskTriggersStream(QalyptusChildStream):
    name = "task_triggers"
    parent_stream_type = TasksStream
    path = "tasks/{task_id}/triggers"
    key_properties = ("task_id", "id")
    record_schema = TASK_TRIGGERS_SCHEMA
    context_fields = {"task_id": "task_id"}


class ReportFiltersStream(QalyptusChildStream):
    name = "report_filters"
    parent_stream_type = ReportsStream
    path = "filters/report/{report_id}"
    key_properties = ("report_id", "id")
    record_schema = REPORT_FILTERS_SCHEMA
    context_fields = {"report_id": "report_id"}


class ReportObjectsStream(QalyptusChildStream):
    name = "report_objects"
    parent_stream_type = ReportsStream
    path = "reports/{report_id}/template-items"
    key_properties = ("report_id", "name", "type")
    record_schema = REPORT_OBJECTS_SCHEMA
    context_fields = {"report_id": "report_id"}

    def parse_response(self, response) -> Iterable[dict[str, Any]]:
        payload = response.json(parse_float=decimal.Decimal)
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            return

        for node in data.get("nodes") or []:
            if isinstance(node, dict):
                yield node
