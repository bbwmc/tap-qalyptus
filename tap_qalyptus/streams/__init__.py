"""Qalyptus stream definitions."""

from tap_qalyptus.streams.child import (
    ReportFiltersStream,
    ReportObjectsStream,
    TaskRecipientsStream,
    TaskReportStream,
    TaskReportsStream,
    TaskTriggersStream,
)
from tap_qalyptus.streams.top_level import (
    FiltersStream,
    GroupsStream,
    ProjectsStream,
    ReportsStream,
    TasksStream,
    UsersStream,
)

__all__ = [
    "FiltersStream",
    "GroupsStream",
    "ProjectsStream",
    "ReportFiltersStream",
    "ReportObjectsStream",
    "ReportsStream",
    "TaskRecipientsStream",
    "TaskReportStream",
    "TaskReportsStream",
    "TaskTriggersStream",
    "TasksStream",
    "UsersStream",
]
