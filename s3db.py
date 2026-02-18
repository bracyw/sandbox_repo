"""A tiny S3-backed document database wrapper.

This module treats S3 as a low-cost document store. Each record is one JSON
object, and optional secondary-index pointers can be written for faster lookups.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional
from urllib.parse import quote, unquote

try:  # Prefer real AWS exceptions when available.
    from botocore.exceptions import ClientError
except ModuleNotFoundError:  # pragma: no cover

    class ClientError(Exception):
        """Fallback ClientError compatible with the botocore error shape."""

        def __init__(self, response: dict, operation_name: str):
            super().__init__(operation_name)
            self.response = response


try:
    import boto3
except ModuleNotFoundError:  # pragma: no cover
    boto3 = None


class RecordNotFoundError(KeyError):
    """Raised when a document does not exist."""


@dataclass(frozen=True)
class Record:
    """Represents a fetched record from S3."""

    id: str
    data: Dict[str, Any]
    updated_at: str


class S3Database:
    """S3-backed document database wrapper.

    Data layout:
      - Records: {prefix}/{table}/records/{id}.json
      - Optional secondary index pointers:
        {prefix}/{table}/indexes/{field}/{value}/{id}.idx

    Notes:
      - S3 is eventually consistent for some list/read patterns.
      - `query` is a scan. Use `query_by_index` for repeated lookups.
    """

    def __init__(
        self,
        bucket: str,
        prefix: str = "s3db",
        client: Any | None = None,
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")

        if client is not None:
            self.client = client
        else:
            if boto3 is None:
                raise ModuleNotFoundError("boto3 is required when no custom S3 client is provided")
            self.client = boto3.client("s3")

    def create_table(self, table: str) -> None:
        """Create table marker object."""
        self.client.put_object(Bucket=self.bucket, Key=self._table_marker_key(table), Body=b"{}")

    def put(
        self,
        table: str,
        record_id: str,
        document: Dict[str, Any],
        index_fields: Optional[Iterable[str]] = None,
    ) -> Record:
        """Insert or replace a record and maintain index pointers.

        On overwrite, stale pointers from previously indexed values are removed.
        """
        index_field_set = set(index_fields or [])

        # Remove stale pointers when overwriting an existing record.
        try:
            old_payload = self._fetch_record_payload(table, record_id)
        except RecordNotFoundError:
            old_payload = None

        if old_payload is not None:
            old_data = old_payload.get("data", {})
            old_indexed_fields = set(old_payload.get("_indexed_fields", []))
            self._remove_index_pointers(table, record_id, old_data, old_indexed_fields)

        now = self._utc_now()
        payload = {
            "id": record_id,
            "updated_at": now,
            "data": document,
            "_indexed_fields": sorted(index_field_set),
        }
        self.client.put_object(
            Bucket=self.bucket,
            Key=self._record_key(table, record_id),
            Body=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            ContentType="application/json",
        )

        self._write_index_pointers(table, record_id, document, index_field_set)

        return Record(id=record_id, data=document, updated_at=now)

    def batch_put(
        self,
        table: str,
        items: Dict[str, Dict[str, Any]],
        index_fields: Optional[Iterable[str]] = None,
    ) -> List[Record]:
        """Write many documents sequentially and return inserted records."""
        return [self.put(table, rid, doc, index_fields=index_fields) for rid, doc in items.items()]

    def get(self, table: str, record_id: str, default: Record | None = ...) -> Record | None:
        """Fetch one record by id.

        If `default` is passed, return it when the record is missing.
        """
        try:
            payload = self._fetch_record_payload(table, record_id)
        except RecordNotFoundError:
            if default is ...:
                raise
            return default
        return Record(id=payload["id"], data=payload["data"], updated_at=payload["updated_at"])

    def delete(self, table: str, record_id: str) -> None:
        """Delete one record and its index pointers if metadata is available."""
        try:
            raw = self._fetch_record_payload(table, record_id)
        except RecordNotFoundError:
            raw = None

        if raw is not None:
            self._remove_index_pointers(
                table=table,
                record_id=record_id,
                document=raw.get("data", {}),
                index_fields=set(raw.get("_indexed_fields", [])),
            )
        self.client.delete_object(Bucket=self.bucket, Key=self._record_key(table, record_id))

    def query(
        self,
        table: str,
        where: Optional[Dict[str, Any]] = None,
        *,
        limit: Optional[int] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Record]:
        """Scan a table and filter documents in-memory."""
        out: List[Record] = []
        for key in self._list_keys(self._records_prefix(table)):
            if not key.endswith(".json"):
                continue
            record_id = self._decode_record_id(key)
            record = self.get(table, record_id, default=None)
            if record is None:
                continue
            if where and not all(record.data.get(k) == v for k, v in where.items()):
                continue
            if predicate and not predicate(record.data):
                continue
            out.append(record)
            if limit is not None and len(out) >= limit:
                break
        return out

    def query_by_index(
        self,
        table: str,
        field: str,
        value: Any,
        *,
        limit: Optional[int] = None,
    ) -> List[Record]:
        """Fetch records via secondary-index pointer objects."""
        out: List[Record] = []
        for key in self._list_keys(self._index_prefix(table, field, str(value))):
            if not key.endswith(".idx"):
                continue
            record = self.get(table, self._decode_index_record_id(key), default=None)
            if record is None:
                continue
            out.append(record)
            if limit is not None and len(out) >= limit:
                break
        return out

    def _fetch_record_payload(self, table: str, record_id: str) -> Dict[str, Any]:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self._record_key(table, record_id))
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                raise RecordNotFoundError(record_id) from exc
            raise
        return json.loads(response["Body"].read().decode("utf-8"))

    def _write_index_pointers(
        self,
        table: str,
        record_id: str,
        document: Dict[str, Any],
        index_fields: set[str],
    ) -> None:
        for field in index_fields:
            value = document.get(field)
            if value is None:
                continue
            self.client.put_object(
                Bucket=self.bucket,
                Key=self._index_key(table, field, str(value), record_id),
                Body=b"",
                ContentType="application/octet-stream",
            )

    def _remove_index_pointers(
        self,
        table: str,
        record_id: str,
        document: Dict[str, Any],
        index_fields: set[str],
    ) -> None:
        for field in index_fields:
            value = document.get(field)
            if value is None:
                continue
            self.client.delete_object(
                Bucket=self.bucket,
                Key=self._index_key(table, field, str(value), record_id),
            )

    def _list_keys(self, prefix: str) -> Iterator[str]:
        continuation_token: str | None = None
        while True:
            kwargs: Dict[str, Any] = {"Bucket": self.bucket, "Prefix": prefix}
            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token

            page = self.client.list_objects_v2(**kwargs)
            for item in page.get("Contents", []):
                yield item["Key"]

            if not page.get("IsTruncated"):
                break
            continuation_token = page.get("NextContinuationToken")

    def _record_key(self, table: str, record_id: str) -> str:
        return f"{self._records_prefix(table)}{quote(record_id, safe='')}.json"

    def _records_prefix(self, table: str) -> str:
        return f"{self.prefix}/{table}/records/"

    def _table_marker_key(self, table: str) -> str:
        return f"{self.prefix}/{table}/_table.json"

    def _index_prefix(self, table: str, field: str, value: str) -> str:
        return f"{self.prefix}/{table}/indexes/{quote(field, safe='')}/{quote(value, safe='')}/"

    def _index_key(self, table: str, field: str, value: str, record_id: str) -> str:
        return f"{self._index_prefix(table, field, value)}{quote(record_id, safe='')}.idx"

    @staticmethod
    def _decode_record_id(key: str) -> str:
        return unquote(key.rsplit("/", 1)[-1].removesuffix(".json"))

    @staticmethod
    def _decode_index_record_id(key: str) -> str:
        return unquote(key.rsplit("/", 1)[-1].removesuffix(".idx"))

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()
