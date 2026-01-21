import os
import json
from datetime import datetime, timedelta, timezone
from collections import Counter

from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()


# CONFIG
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "Unknown")
BASE_ID = os.environ.get("BASE_ID", "Unknown")
REQUESTS_TABLE_ID = os.environ.get("REQUESTS_TABLE_ID", "Unknown")
CONSULTANTS_TABLE_ID = os.environ.get("CONSULTANTS_TABLE_ID", "Unknown")

REPORT_FILE = "weekly_report.json"


# INIT
api = Api(AIRTABLE_API_KEY)
requests_table = api.table(BASE_ID, REQUESTS_TABLE_ID)
consultants_table = api.table(BASE_ID, CONSULTANTS_TABLE_ID)

now = datetime.now(timezone.utc)
week_ago = now - timedelta(days=7)


# FETCH DATA
# get consultants
consultants_data = consultants_table.all()
consultant_map = {
    c["id"]: c["fields"].get("full_name", "Unknown")
    for c in consultants_data
}

# fetch metrics
new_requests = []
closed_requests = []
processing_times = []
consultant_counter = Counter()

for r in requests_table.all():
    fields = r["fields"]

    created_at = fields.get("created_at", "Unknown")
    completed_at = fields.get("completed_at")
    status = fields.get("status", "Unknown")

    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

    # new requests
    if week_ago <= created_dt <= now:
        new_requests.append(r)

    # completed (closed) requests
    if status == "Completed" and completed_at:
        closed_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))

        # if week_ago <= created_dt <= now:
        if week_ago <= closed_dt <= now:
            closed_requests.append(r)

            duration = (closed_dt - created_dt).total_seconds() / 3600
            processing_times.append(duration)

            consultant_ids = fields.get("consultants", [])
            for cid in consultant_ids:
                consultant_counter[cid] += 1

avg_processing_time = (
    round(sum(processing_times) / len(processing_times), 2)
    if processing_times
    else 0
)

top_3_consultants = [
    (consultant_map.get(cid, "Unknown"), count)
    for cid, count in consultant_counter.most_common(3)
]

# EXPORT JSON
report_data = {
    "report_period": {
        "from": week_ago.strftime('%Y-%m-%d'),
        "to": now.strftime('%Y-%m-%d'),
    },
    "metrics": {
        "new_requests_count": len(new_requests),
        "closed_requests_count": len(closed_requests),
        "average_processing_time_hours": avg_processing_time,
        "top_3_consultants": [
            {
                "consultant_name": name,
                "closed_requests": count
            }
            for name, count in top_3_consultants
        ],
    },
    "generated_at": now.strftime('%Y-%m-%d %H:%M'),
}

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    json.dump(report_data, f, ensure_ascii=False, indent=4)

print(f"✅ JSON report saved to {REPORT_FILE}")
