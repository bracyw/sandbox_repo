import json
import os
import time

import redis


def run_job(payload: dict) -> dict:
    objective = payload.get("objective", "unspecified objective")
    return {
        "objective": objective,
        "tasks": [
            "Create priority list",
            "Assign owners",
            "Draft leadership update",
        ],
    }


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    queue_name = os.getenv("QUEUE_NAME", "chief_of_staff_jobs")
    client = redis.from_url(redis_url)

    while True:
        _, raw = client.blpop(queue_name)
        payload = json.loads(raw)
        result = run_job(payload)
        print(json.dumps({"input": payload, "result": result}), flush=True)
        time.sleep(0.25)


if __name__ == "__main__":
    main()
