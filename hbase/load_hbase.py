
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = Path(__file__).resolve().parent / "load_commands.hbase"

with open(DATA / "sessions_0.json", encoding="utf-8") as f:
    sessions = json.load(f)

def safe(value):
    """Escape values for HBase Shell string arguments."""
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ") + "'"

def put(table, row, column, value):
    return f"put {safe(table)}, {safe(row)}, {safe(column)}, {safe(value)}\n"

daily_views = defaultdict(int)
event_count = 0

with open(OUTPUT, "w", encoding="utf-8") as out:
    for session in sessions[:100]:
        user_id = session.get("user_id")
        session_id = session.get("session_id")

        if not user_id or not session_id:
            continue

        for index, page in enumerate(session.get("page_views") or []):
            product_id = page.get("product_id")
            timestamp = page.get("timestamp")
            page_type = page.get("page_type", "unknown")

            if not product_id or not timestamp:
                continue

            # User prefix enables efficient customer-event scans.
            row_key = f"{user_id}#{timestamp}#{session_id}#{index:04d}"

            out.write(put("user_events", row_key,
                          "event:type", page_type))
            out.write(put("user_events", row_key,
                          "event:product_id", product_id))
            out.write(put("user_events", row_key,
                          "event:timestamp", timestamp))
            out.write(put("user_events", row_key,
                          "session:session_id", session_id))
            out.write(put("user_events", row_key,
                          "session:user_id", user_id))

            date = timestamp[:10]
            daily_views[(product_id, date)] += 1
            event_count += 1

    for (product_id, date), views in sorted(daily_views.items()):
        row_key = f"{product_id}#{date}"
        out.write(put("product_daily_metrics", row_key,
                      "metrics:views", views))

print("HBase command file created:", OUTPUT)
print("Sessions processed:", min(100, len(sessions)))
print("Page-view events prepared:", event_count)
print("Product-day metrics prepared:", len(daily_views))
