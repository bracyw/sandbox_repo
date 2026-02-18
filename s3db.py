"""A tiny S3-backed document database wrapper.

This module makes it easy to treat S3 as a low-cost key-value/document store.
Each record is stored as one JSON object in S3, which keeps storage costs low
and avoids provisioning a dedicated database service.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional
from urllib.parse import quote, unquote

try:
    import boto3
except ModuleNotFoundError:  # pragma: no cover
    boto3 = None


class ClientError(Exception):
    """Fallback ClientError compatible with botocore shape."""

    def __init__(self, response: dict, operation_name: str):
        super().__init__(operation_name)
        self.response = response


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
        """Create table marker object if missing."""
        key = self._table_marker_key(table)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=b"{}")

    def put(
        self,
        table: str,
        record_id: str,
        document: Dict[str, Any],
        index_fields: Optional[Iterable[str]] = None,
    ) -> Record:
        """Insert or replace a record and update configured index pointers."""
        now = self._utc_now()
        payload = {"id": record_id, "updated_at": now, "data": document}
        self.client.put_object(
            Bucket=self.bucket,
            Key=self._record_key(table, record_id),
            Body=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            ContentType="application/json",
        )

        for field in index_fields or []:
            value = document.get(field)
            if value is None:
                continue
            self.client.put_object(
                Bucket=self.bucket,
                Key=self._index_key(table, field, str(value), record_id),
                Body=b"",
                ContentType="application/octet-stream",
            )

        return Record(id=record_id, data=document, updated_at=now)

    def batch_put(
        self,
        table: str,
        items: Dict[str, Dict[str, Any]],
        index_fields: Optional[Iterable[str]] = None,
    ) -> List[Record]:
        """Write many documents (sequentially) and return inserted records."""
        written: List[Record] = []
        for record_id, document in items.items():
            written.append(self.put(table, record_id, document, index_fields=index_fields))
        return written

    def get(self, table: str, record_id: str) -> Record:
        """Fetch one record by id."""
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=self._record_key(table, record_id),
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                raise RecordNotFoundError(record_id) from exc
            raise

        payload = json.loads(response["Body"].read().decode("utf-8"))
        return Record(id=payload["id"], data=payload["data"], updated_at=payload["updated_at"])

    def delete(self, table: str, record_id: str) -> None:
        """Delete one record by id."""
        self.client.delete_object(Bucket=self.bucket, Key=self._record_key(table, record_id))

    def query(
        self,
        table: str,
        where: Optional[Dict[str, Any]] = None,
        *,
        limit: Optional[int] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Record]:
        """Scan a table and filter documents.

        Keep this for low-volume workloads. For high-frequency lookups, use
        `query_by_index` with precomputed index_fields.
        """
        out: List[Record] = []
        prefix = self._records_prefix(table)

        for key in self._list_keys(prefix):
            if not key.endswith(".json"):
                continue
            record_id = self._decode_record_id(key)
            record = self.get(table, record_id)
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
        """Fetch records via secondary index pointer objects."""
        out: List[Record] = []
        prefix = self._index_prefix(table, field, str(value))
        for key in self._list_keys(prefix):
            if not key.endswith(".idx"):
                continue
            record_id = self._decode_index_record_id(key)
            try:
                out.append(self.get(table, record_id))
            except RecordNotFoundError:
                continue
            if limit is not None and len(out) >= limit:
                break
        return out

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
        return f"{self._records_prefix(table)}{quote(record_id, safe='')}" + ".json"

    def _records_prefix(self, table: str) -> str:
        return f"{self.prefix}/{table}/records/"

    def _table_marker_key(self, table: str) -> str:
        return f"{self.prefix}/{table}/_table.json"

    def _index_prefix(self, table: str, field: str, value: str) -> str:
        return f"{self.prefix}/{table}/indexes/{quote(field, safe='')}/{quote(value, safe='')}/"

    def _index_key(self, table: str, field: str, value: str, record_id: str) -> str:
        return f"{self._index_prefix(table, field, value)}{quote(record_id, safe='')}.idx"

    def _decode_record_id(self, key: str) -> str:
        encoded = key.rsplit("/", 1)[-1].removesuffix(".json")
        return unquote(encoded)

    def _decode_index_record_id(self, key: str) -> str:
        encoded = key.rsplit("/", 1)[-1].removesuffix(".idx")
        return unquote(encoded)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()
