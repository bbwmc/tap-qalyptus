"""Tap class for tap-qalyptus."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_qalyptus.streams import (
    FiltersStream,
    GroupsStream,
    ProjectsStream,
    ReportFiltersStream,
    ReportObjectsStream,
    ReportsStream,
    TaskRecipientsStream,
    TaskReportStream,
    TaskReportsStream,
    TaskTriggersStream,
    TasksStream,
    UsersStream,
)


class TapQalyptus(Tap):
    """Singer tap for the Qalyptus API."""

    name = "tap-qalyptus"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            required=True,
            description="Tenant root URL or API base URL for Qalyptus.",
        ),
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            description="Raw API key or complete auth header value.",
        ),
        th.Property(
            "api_key_header",
            th.StringType,
            default="Authorization",
            description="HTTP header used to send the credential.",
        ),
        th.Property(
            "request_timeout",
            th.IntegerType,
            default=60,
            description="HTTP request timeout in seconds.",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Reserved for future incremental support.",
        ),
    ).to_dict()

    def discover_streams(self):
        return [
            UsersStream(self),
            GroupsStream(self),
            ProjectsStream(self),
            FiltersStream(self),
            ReportsStream(self),
            ReportFiltersStream(self),
            ReportObjectsStream(self),
            TasksStream(self),
            TaskRecipientsStream(self),
            TaskReportsStream(self),
            TaskReportStream(self),
            TaskTriggersStream(self),
        ]


if __name__ == "__main__":
    TapQalyptus.cli()
