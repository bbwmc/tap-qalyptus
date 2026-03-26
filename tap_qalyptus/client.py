"""Shared client and stream helpers for Qalyptus."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import decimal
from typing import Any
from urllib.parse import urlparse, urlunparse

from singer_sdk.streams import RESTStream

from tap_qalyptus import __version__

API_PREFIX = "/api/v1"
COMMON_RECORD_KEYS = ("data", "items", "results", "value")


def _object_schema(
    *identifier_fields: str,
    extra_properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    properties = {
        field: {"type": ["integer", "string", "null"]}
        for field in identifier_fields
    }
    if extra_properties:
        properties.update(extra_properties)

    return {
        "type": "object",
        "properties": properties,
        "additionalProperties": True,
    }


def normalize_api_url(api_url: str) -> str:
    """Normalize a user-supplied tenant URL onto the API base path."""
    parsed = urlparse(api_url.strip())
    path = parsed.path.rstrip("/")
    marker_index = path.find(API_PREFIX)

    if marker_index >= 0:
        normalized_path = path[: marker_index + len(API_PREFIX)]
    elif path:
        normalized_path = f"{path}{API_PREFIX}"
    else:
        normalized_path = API_PREFIX

    return urlunparse(
        parsed._replace(
            path=f"{normalized_path.rstrip('/')}/",
            params="",
            query="",
            fragment="",
        )
    )


class QalyptusStream(RESTStream):
    """Base REST stream for the Qalyptus API."""

    records_keys = COMMON_RECORD_KEYS
    extra_retry_statuses = [429]
    context_fields: dict[str, str] = {}

    @property
    def url_base(self) -> str:
        return normalize_api_url(self.config["api_url"])

    @property
    def http_headers(self) -> dict[str, str]:
        api_key_header = self.config["api_key_header"]
        api_key_value = self.config["api_key"]
        if api_key_header.lower() == "authorization" and not api_key_value.lower().startswith("bearer "):
            api_key_value = f"Bearer {api_key_value}"

        return {
            "Accept": "application/json",
            "User-Agent": f"tap-qalyptus/{__version__}",
            api_key_header: api_key_value,
        }

    @property
    def timeout(self) -> int:
        return int(self.config.get("request_timeout", 60))

    def get_new_paginator(self):
        return None

    def parse_response(self, response) -> Iterable[dict[str, Any]]:
        payload = response.json(parse_float=decimal.Decimal)
        for record in self._extract_records(payload):
            if isinstance(record, dict):
                yield record

    def get_records(self, context):
        for record in super().get_records(context):
            yield self._merge_context_fields(record, context)

    def _merge_context_fields(
        self,
        record: dict[str, Any],
        context: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if not context or not self.context_fields:
            return record

        merged = dict(record)
        for context_key, record_key in self.context_fields.items():
            if context_key in context:
                merged[record_key] = context[context_key]
        return merged

    def _extract_records(self, payload: Any) -> list[Any]:
        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):
            candidate_keys = (*self.records_keys, self.name, self.name.rstrip("s"))
            for key in candidate_keys:
                value = payload.get(key)
                if isinstance(value, list):
                    return value
                if isinstance(value, dict):
                    return [value]

            list_values = [value for value in payload.values() if isinstance(value, list)]
            if len(list_values) == 1:
                return list_values[0]

            dict_values = [value for value in payload.values() if isinstance(value, dict)]
            if len(dict_values) == 1:
                return dict_values

            return [payload]

        return []


class QalyptusTopLevelStream(QalyptusStream):
    """Base stream for top-level collection endpoints."""

    def __init__(self, tap, schema=None, name=None):
        super().__init__(tap=tap, schema=schema or _object_schema("id"), name=name)
        self._primary_keys = ["id"]


class QalyptusChildStream(QalyptusStream):
    """Base stream for child endpoints with parent context fields."""

    key_properties: tuple[str, ...] = ("id",)
    schema_identifier_fields: tuple[str, ...] = ("id",)
    schema_extra_properties: dict[str, Any] = {}

    def __init__(self, tap, schema=None, name=None):
        super().__init__(
            tap=tap,
            schema=schema
            or _object_schema(
                *self.schema_identifier_fields,
                extra_properties=self.schema_extra_properties,
            ),
            name=name,
        )
        self._primary_keys = list(self.key_properties)
