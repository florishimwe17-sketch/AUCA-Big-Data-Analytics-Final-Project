
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["auca_ecommerce_analytics"]

pipeline = [
    {"$match": {
        "status": {
            "$in": ["completed", "shipped", "delivered"]
        }
    }},
    {"$group": {
        "_id": "$user_id",
        "total_spent": {"$sum": "$total"},
        "transaction_count": {"$sum": 1},
        "average_order_value": {"$avg": "$total"}
    }},
    {"$lookup": {
        "from": "users",
        "localField": "_id",
        "foreignField": "user_id",
        "as": "user"
    }},
    {"$unwind": "$user"},
    {"$project": {
        "_id": 0,
        "user_id": "$_id",
        "country": "$user.geo_data.country",
        "total_spent": {"$round": ["$total_spent", 2]},
        "transaction_count": 1,
        "average_order_value": {
            "$round": ["$average_order_value", 2]
        }
    }},
    {"$sort": {"total_spent": -1}},
    {"$limit": 10}
]

results = list(db.transactions.aggregate(pipeline))

print("\nTOP 10 CUSTOMERS BY TOTAL SPENDING")
print("-" * 75)

for rank, row in enumerate(results, 1):
    print(
        f"{rank}. {row['user_id']} | "
        f"Country: {row['country']} | "
        f"Total: ${row['total_spent']:,.2f} | "
        f"Orders: {row['transaction_count']} | "
        f"Average: ${row['average_order_value']:,.2f}"
    )

client.close()
