"""Top-level Qalyptus streams."""

from tap_qalyptus.client import QalyptusTopLevelStream
from tap_qalyptus.schemas import (
    FILTERS_SCHEMA,
    GROUPS_SCHEMA,
    PROJECTS_SCHEMA,
    REPORTS_SCHEMA,
    TASKS_SCHEMA,
    USERS_SCHEMA,
)


class UsersStream(QalyptusTopLevelStream):
    name = "users"
    path = "users"
    record_schema = USERS_SCHEMA


class GroupsStream(QalyptusTopLevelStream):
    name = "groups"
    path = "groups"
    record_schema = GROUPS_SCHEMA


class ProjectsStream(QalyptusTopLevelStream):
    name = "projects"
    path = "projects"
    record_schema = PROJECTS_SCHEMA


class FiltersStream(QalyptusTopLevelStream):
    name = "filters"
    path = "filters"
    record_schema = FILTERS_SCHEMA


class ReportsStream(QalyptusTopLevelStream):
    name = "reports"
    path = "reports"
    record_schema = REPORTS_SCHEMA

    def get_child_context(self, record, context):
        if "id" not in record:
            return None
        return {"report_id": record["id"]}


class TasksStream(QalyptusTopLevelStream):
    name = "tasks"
    path = "tasks"
    record_schema = TASKS_SCHEMA

    def get_child_context(self, record, context):
        if "id" not in record:
            return None
        return {"task_id": record["id"]}
