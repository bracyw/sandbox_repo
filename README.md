# Cheap S3 Database Wrapper

`S3Database` is a lightweight wrapper that lets you use Amazon S3 like a simple document database.

It is intentionally minimal and cost-focused:

- **Storage is cheap**: each row is one JSON object in S3.
- **No servers to run**: no managed DB cluster to provision.
- **Simple API**: `put/get/delete/query` plus optional secondary index pointers.

## Install

```bash
pip install boto3
```

## Example

```python
from s3db import S3Database

db = S3Database(bucket="my-app-data", prefix="prod")

db.create_table("users")
db.put("users", "u_123", {"email": "a@example.com", "plan": "free"}, index_fields=["plan"])

user = db.get("users", "u_123")
print(user.data)

free_users = db.query_by_index("users", "plan", "free")
print([u.id for u in free_users])

# overwrite updates index pointers too
# record leaves old plan index and appears in new one
updated = db.put("users", "u_123", {"email": "a@example.com", "plan": "pro"}, index_fields=["plan"])
print(updated.updated_at)
```

## Design notes

- Records are stored at: `{prefix}/{table}/records/{id}.json`
- Optional index pointers are stored at: `{prefix}/{table}/indexes/{field}/{value}/{id}.idx`
- A small `_indexed_fields` metadata list is stored in each record so overwrites/deletes can clean up stale index pointers.
- `query()` performs a prefix scan of a table. Use it for low-volume workloads.
- `query_by_index()` is faster for point lookups if you populated `index_fields` during writes.

## Tradeoffs

This wrapper works best for:

- low-to-moderate write rates,
- workloads that can tolerate eventual consistency,
- cost-sensitive use cases where "cheap and simple" beats strict relational features.

It does **not** provide SQL joins, multi-row ACID transactions, or advanced query planning.
