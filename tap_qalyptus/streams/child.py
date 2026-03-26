"""Child Qalyptus streams."""

from __future__ import annotations

from collections.abc import Iterable
import decimal
from typing import Any

from tap_qalyptus.client import QalyptusChildStream
from tap_qalyptus.streams.top_level import ReportsStream, TasksStream


class TaskRecipientsStream(QalyptusChildStream):
    name = "task_recipients"
    parent_stream_type = TasksStream
    path = "tasks/{task_id}/recipients"
    key_properties = ("task_id", "id")
    schema_identifier_fields = ("task_id", "id")
    context_fields = {"task_id": "task_id"}


class TaskReportsStream(QalyptusChildStream):
    name = "task_reports"
    parent_stream_type = TasksStream
    path = "tasks/{task_id}/reports"
    key_properties = ("task_id", "id")
    schema_identifier_fields = ("task_id", "id")
    context_fields = {"task_id": "task_id"}

    def get_child_context(self, record: dict[str, Any], context: dict[str, Any] | None):
        task_id = (context or {}).get("task_id") or record.get("task_id")
        if not task_id or "id" not in record:
            return None
        return {"task_id": task_id, "task_report_id": record["id"]}


class TaskReportStream(QalyptusChildStream):
    name = "task_report"
    parent_stream_type = TaskReportsStream
    path = "tasks/{task_id}/reports/{task_report_id}"
    key_properties = ("task_id", "id")
    schema_identifier_fields = ("task_id", "id", "task_report_id")
    context_fields = {
        "task_id": "task_id",
        "task_report_id": "task_report_id",
    }


class TaskTriggersStream(QalyptusChildStream):
    name = "task_triggers"
    parent_stream_type = TasksStream
    path = "tasks/{task_id}/triggers"
    key_properties = ("task_id", "id")
    schema_identifier_fields = ("task_id", "id")
    context_fields = {"task_id": "task_id"}


class ReportFiltersStream(QalyptusChildStream):
    name = "report_filters"
    parent_stream_type = ReportsStream
    path = "filters/report/{report_id}"
    key_properties = ("report_id", "id")
    schema_identifier_fields = ("report_id", "id")
    context_fields = {"report_id": "report_id"}


class ReportObjectsStream(QalyptusChildStream):
    name = "report_objects"
    parent_stream_type = ReportsStream
    path = "reports/{report_id}/template-items"
    key_properties = ("report_id", "id")
    schema_identifier_fields = ("report_id", "id", "parent_object_id")
    schema_extra_properties = {
        "node_name": {"type": ["string", "null"]},
        "node_type": {"type": ["string", "null"]},
        "node_icon": {"type": ["string", "null"]},
        "object_depth": {"type": ["integer", "null"]},
    }
    context_fields = {"report_id": "report_id"}

    def parse_response(self, response) -> Iterable[dict[str, Any]]:
        payload = response.json(parse_float=decimal.Decimal)
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            return

        for node in data.get("nodes") or []:
            node_name = node.get("name")
            node_type = node.get("type")
            node_icon = node.get("icon")
            for obj in node.get("objects") or []:
                yield from self._flatten_object_tree(
                    obj,
                    node_name=node_name,
                    node_type=node_type,
                    node_icon=node_icon,
                )

    def _flatten_object_tree(
        self,
        obj: dict[str, Any],
        *,
        node_name: str | None,
        node_type: str | None,
        node_icon: str | None,
        parent_object_id: str | None = None,
        depth: int = 0,
    ) -> Iterable[dict[str, Any]]:
        row = dict(obj)
        children = row.pop("objects", None)
        row["parent_object_id"] = parent_object_id
        row["node_name"] = node_name
        row["node_type"] = node_type
        row["node_icon"] = node_icon
        row["object_depth"] = depth
        yield row

        if isinstance(children, list):
            for child in children:
                yield from self._flatten_object_tree(
                    child,
                    node_name=node_name,
                    node_type=node_type,
                    node_icon=node_icon,
                    parent_object_id=obj.get("id"),
                    depth=depth + 1,
                )
