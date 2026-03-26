"""Top-level Qalyptus streams."""

from tap_qalyptus.client import QalyptusTopLevelStream


class UsersStream(QalyptusTopLevelStream):
    name = "users"
    path = "users"


class GroupsStream(QalyptusTopLevelStream):
    name = "groups"
    path = "groups"


class ProjectsStream(QalyptusTopLevelStream):
    name = "projects"
    path = "projects"


class FiltersStream(QalyptusTopLevelStream):
    name = "filters"
    path = "filters"


class ReportsStream(QalyptusTopLevelStream):
    name = "reports"
    path = "reports"

    def get_child_context(self, record, context):
        if "id" not in record:
            return None
        return {"report_id": record["id"]}


class TasksStream(QalyptusTopLevelStream):
    name = "tasks"
    path = "tasks"

    def get_child_context(self, record, context):
        if "id" not in record:
            return None
        return {"task_id": record["id"]}
