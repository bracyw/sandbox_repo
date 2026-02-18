import io

from s3db import ClientError, RecordNotFoundError, S3Database


class FakeS3Client:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, **kwargs):
        if isinstance(Body, str):
            Body = Body.encode("utf-8")
        self.objects[(Bucket, Key)] = Body
        return {"ETag": "fake"}

    def get_object(self, Bucket, Key):
        obj = self.objects.get((Bucket, Key))
        if obj is None:
            raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
        return {"Body": io.BytesIO(obj)}

    def delete_object(self, Bucket, Key):
        self.objects.pop((Bucket, Key), None)

    def list_objects_v2(self, Bucket, Prefix, ContinuationToken=None):
        keys = [k for (b, k) in self.objects if b == Bucket and k.startswith(Prefix)]
        keys.sort()
        return {"IsTruncated": False, "Contents": [{"Key": key} for key in keys]}


def test_put_get_delete_roundtrip():
    client = FakeS3Client()
    db = S3Database(bucket="cheap-db", client=client)

    db.create_table("users")
    written = db.put("users", "u1", {"email": "a@example.com", "tier": "free"})
    assert written.id == "u1"
    fetched = db.get("users", "u1")
    assert fetched.data["email"] == "a@example.com"

    db.delete("users", "u1")
    try:
        db.get("users", "u1")
        assert False, "expected missing record"
    except RecordNotFoundError:
        pass


def test_query_and_index_lookup():
    client = FakeS3Client()
    db = S3Database(bucket="cheap-db", client=client)

    db.batch_put(
        "events",
        {
            "e1": {"type": "click", "user": "u1"},
            "e2": {"type": "view", "user": "u1"},
            "e3": {"type": "click", "user": "u2"},
        },
        index_fields=["type", "user"],
    )

    clicked = db.query("events", where={"type": "click"})
    assert {r.id for r in clicked} == {"e1", "e3"}

    u1_events = db.query_by_index("events", "user", "u1")
    assert {r.id for r in u1_events} == {"e1", "e2"}
