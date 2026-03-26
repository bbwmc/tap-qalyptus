"""JSON schemas for Qalyptus streams."""

from __future__ import annotations

from typing import Any

STRING = {"type": ["string", "null"]}
BOOLEAN = {"type": ["boolean", "null"]}
NUMBER = {"type": ["number", "null"]}
OBJECT = {"type": ["object", "null"], "additionalProperties": True}
ARRAY = {"type": ["array", "null"], "items": {}}


def build_schema(properties: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return a permissive object schema for a stream."""
    return {
        "type": "object",
        "properties": properties,
        "additionalProperties": True,
    }


USERS_SCHEMA = build_schema(
    {
        "id": STRING,
        "name": STRING,
        "type": STRING,
        "email": STRING,
        "groups": ARRAY,
        "status": STRING,
        "license": STRING,
        "isTenantOwner": BOOLEAN,
        "tenantAdminRole": STRING,
        "organizationRoles": ARRAY,
    }
)

GROUPS_SCHEMA = build_schema(
    {
        "id": STRING,
        "name": STRING,
        "members": NUMBER,
        "isDefault": BOOLEAN,
        "description": STRING,
        "organization": STRING,
        "organizationID": STRING,
    }
)

PROJECTS_SCHEMA = build_schema(
    {
        "id": STRING,
        "name": STRING,
        "owner": STRING,
        "isMine": BOOLEAN,
        "ownerName": STRING,
        "description": STRING,
        "isGlobalPermissions": BOOLEAN,
    }
)

FILTERS_SCHEMA = build_schema(
    {
        "id": STRING,
        "name": STRING,
        "owner": STRING,
        "isMine": BOOLEAN,
        "project": OBJECT,
        "ownerName": STRING,
        "description": STRING,
    }
)

REPORTS_SCHEMA = build_schema(
    {
        "id": STRING,
        "name": STRING,
        "type": STRING,
        "owner": STRING,
        "isMine": BOOLEAN,
        "project": OBJECT,
        "ownerName": STRING,
        "description": STRING,
        "isIteration": BOOLEAN,
        "templateFile": STRING,
        "outputFormats": ARRAY,
        "dynamicNameSeparator": STRING,
    }
)

TASKS_SCHEMA = build_schema(
    {
        "id": STRING,
        "name": STRING,
        "owner": STRING,
        "isMine": BOOLEAN,
        "project": OBJECT,
        "isActive": BOOLEAN,
        "testMode": BOOLEAN,
        "ownerName": STRING,
        "description": STRING,
        "isScheduled": BOOLEAN,
        "notifyIfError": BOOLEAN,
        "notifyIfSuccess": BOOLEAN,
        "notifyIfWarning": BOOLEAN,
        "sendNotifications": BOOLEAN,
        "testModeRecipients": STRING,
        "notificationRecipients": STRING,
        "notificationCc": STRING,
        "notificationBcc": STRING,
        "lastExecution": STRING,
    }
)

TASK_RECIPIENTS_SCHEMA = build_schema(
    {
        "task_id": STRING,
        "id": STRING,
        "name": STRING,
        "type": STRING,
        "email": STRING,
        "recipientID": STRING,
    }
)

TASK_REPORTS_SCHEMA = build_schema(
    {
        "task_id": STRING,
        "id": STRING,
        "name": STRING,
        "type": STRING,
        "format": STRING,
        "reportID": STRING,
        "description": STRING,
        "isIteration": BOOLEAN,
        "outputFormats": ARRAY,
        "emailEmbedment": BOOLEAN,
        "emailAttachment": BOOLEAN,
    }
)

TASK_REPORT_SCHEMA = build_schema(
    {
        "task_id": STRING,
        "id": STRING,
        "name": STRING,
        "type": STRING,
        "format": STRING,
        "filters": ARRAY,
        "reportID": STRING,
        "conditions": ARRAY,
        "description": STRING,
        "isIteration": BOOLEAN,
        "outputFormats": ARRAY,
        "emailEmbedment": BOOLEAN,
        "emailAttachment": BOOLEAN,
        "storageServices": ARRAY,
        "separatorOptions": OBJECT,
        "isOpenFilePasswordProtected": BOOLEAN,
        "isWriteFilePasswordProtected": BOOLEAN,
        "imageQuality": STRING,
        "iterationOptions": OBJECT,
        "hub": OBJECT,
        "fileStorage": OBJECT,
    }
)

TASK_TRIGGERS_SCHEMA = build_schema(
    {
        "task_id": STRING,
        "id": STRING,
        "day": NUMBER,
        "name": STRING,
        "type": STRING,
        "month": NUMBER,
        "atHour": NUMBER,
        "toHour": NUMBER,
        "atMinut": NUMBER,
        "endDate": STRING,
        "toMinut": NUMBER,
        "fromHour": NUMBER,
        "isActive": BOOLEAN,
        "priority": NUMBER,
        "timeZone": STRING,
        "execution": STRING,
        "frequency": STRING,
        "fromMinut": NUMBER,
        "startDate": STRING,
        "everyHours": NUMBER,
        "weeklyDays": STRING,
        "description": STRING,
        "timeZoneOfset": STRING,
        "nextExecutionDate": STRING,
        "appId": STRING,
        "eventType": STRING,
        "qlikEvent": STRING,
    }
)

REPORT_FILTERS_SCHEMA = build_schema(
    {
        "report_id": STRING,
        "id": STRING,
        "name": STRING,
        "owner": STRING,
        "isMine": BOOLEAN,
        "description": STRING,
        "ownerName": STRING,
        "project": OBJECT,
    }
)

REPORT_OBJECTS_SCHEMA = build_schema(
    {
        "report_id": STRING,
        "name": STRING,
        "type": STRING,
        "icon": STRING,
        "objects": ARRAY,
    }
)
