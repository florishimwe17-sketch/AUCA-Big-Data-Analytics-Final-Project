
import json
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "visualizations"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_json(filename):
    with open(DATA / filename, "r", encoding="utf-8") as f:
        return json.load(f)


transactions = load_json("transactions.json")
products = load_json("products.json")
categories = load_json("categories.json")
sessions = load_json("sessions_0.json")

product_categories = {
    p["product_id"]: p["category_id"]
    for p in products
}

category_names = {
    c["category_id"]: c.get("name", c["category_id"])
    for c in categories
}


# CHART 1: TOP 10 CATEGORIES BY REVENUE

revenue = defaultdict(float)

for transaction in transactions:
    if transaction.get("status") != "completed":
        continue

    for item in transaction.get("items", []):
        product_id = item.get("product_id")
        category_id = product_categories.get(product_id)

        if category_id:
            revenue[category_id] += (
                float(item.get("quantity", 0))
                * float(item.get("unit_price", 0))
            )

top_categories = sorted(
    revenue.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]

if top_categories:
    labels = [
        category_names.get(cid, cid)
        for cid, _ in top_categories
    ]
    values = [value for _, value in top_categories]

    plt.figure(figsize=(11, 6))
    plt.barh(labels[::-1], values[::-1])
    plt.title("Top 10 Product Categories by Revenue")
    plt.xlabel("Revenue (USD)")
    plt.tight_layout()
    plt.savefig(OUTPUT / "category_revenue.png", dpi=200)
    plt.close()

    print("Chart 1 created: category_revenue.png")


# CHART 2: SESSION STATUS DISTRIBUTION

status_counts = defaultdict(int)

for session in sessions:
    status = session.get("conversion_status", "unknown")
    status_counts[status] += 1

plt.figure(figsize=(8, 5))
plt.bar(
    list(status_counts.keys()),
    list(status_counts.values())
)
plt.title("Sessions by Conversion Status")
plt.ylabel("Number of Sessions")
plt.tight_layout()
plt.savefig(OUTPUT / "session_status.png", dpi=200)
plt.close()

print("Chart 2 created: session_status.png")


# CHART 3: CONVERSION STATUS BY REFERRAL CHANNEL

channel_sessions = defaultdict(int)
channel_converted = defaultdict(int)

for session in sessions:
    channel = session.get("referrer", "unknown")
    channel_sessions[channel] += 1

    if session.get("conversion_status") == "converted":
        channel_converted[channel] += 1

channels = sorted(channel_sessions)

rates = [
    100 * channel_converted[ch] / channel_sessions[ch]
    for ch in channels
]

plt.figure(figsize=(9, 5))
plt.bar(channels, rates)
plt.title("Reported Conversion Status by Referral Channel")
plt.ylabel("Converted Sessions (%)")
plt.xticks(rotation=25)
plt.tight_layout()
plt.savefig(OUTPUT / "referral_conversion.png", dpi=200)
plt.close()

print("Chart 3 created: referral_conversion.png")

print()
print("SUCCESS! All three charts have been generated.")
print("Charts saved in:", OUTPUT)
