import json
import random
import os
from datetime import datetime, timedelta, timezone
from faker import Faker

from log_data import (
    EVENT_NAMES, EVENT_SOURCES, AWS_REGIONS,
    USER_AGENTS, ERROR_CODES, USER_TYPES,
)

fake = Faker()


def _account_id():
    return str(random.randint(100000000000, 999999999999))


def _request_id():
    return fake.uuid4().upper()


def generate_single_log(index, timestamp, account_id):
    event_name   = random.choice(EVENT_NAMES)
    event_source = random.choice(EVENT_SOURCES)
    region       = random.choice(AWS_REGIONS)
    error_code   = random.choice(ERROR_CODES)
    user_type    = random.choice(USER_TYPES)
    ts_str       = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "eventVersion":    "1.09",
        "eventID":         fake.uuid4(),
        "eventTime":       ts_str,
        "eventType":       "AwsApiCall",
        "eventName":       event_name,
        "eventSource":     event_source,
        "awsRegion":       region,
        "sourceIPAddress": fake.ipv4_public(),
        "userAgent":       random.choice(USER_AGENTS),
        "userIdentity": {
            "type":        user_type,
            "principalId": fake.uuid4(),
            "arn":         f"arn:aws:iam::{account_id}:{'user' if user_type == 'IAMUser' else 'role'}/{fake.user_name()}",
            "accountId":   account_id,
            "userName":    fake.user_name() if user_type == "IAMUser" else None,
        },
        "requestID": _request_id(),
        "requestParameters": {
            "bucketName": fake.slug()      if "Bucket" in event_name or "Object" in event_name else None,
            "key":        fake.file_path() if "Object" in event_name else None,
            "instanceId": f"i-{fake.hexify(text='^^^^^^^^^^')}" if "Instance" in event_name else None,
        },
        "responseElements": {
            "requestId":  _request_id(),
            "instanceId": f"i-{fake.hexify(text='^^^^^^^^^^')}" if "Instance" in event_name else None,
        },
        "errorCode":          error_code,
        "errorMessage":       f"User is not authorized to perform: {event_name}" if error_code == "AccessDenied" else None,
        "readOnly":           event_name.startswith(("Get", "Describe", "List")),
        "recipientAccountId": account_id,
        "managementEvent":    True,
        "index":              index,
    }


def generate_log_file(size_label, count):
    print(f"\n[LOG-GENERATOR] Generating {count:,} entries ({size_label})...")

    account_id = _account_id()
    base_time  = datetime.now(timezone.utc) - timedelta(days=30)
    logs       = []

    for i in range(count):
        timestamp = base_time + timedelta(seconds=i * random.randint(1, 10))
        logs.append(generate_single_log(i, timestamp, account_id))

        if count >= 10000 and (i + 1) % (count // 10) == 0:
            pct = (i + 1) / count * 100
            print(f"  Progress: {pct:.0f}% ({i+1:,}/{count:,})")

    output_path = f"/app/data/logs_{size_label}.json"
    with open(output_path, "w") as f:
        json.dump(logs, f, indent=2)

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"[LOG-GENERATOR] Saved: {output_path} ({count:,} entries, {size_mb:.2f} MB)")
