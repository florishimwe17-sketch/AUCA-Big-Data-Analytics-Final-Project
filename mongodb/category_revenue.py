
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["auca_ecommerce_analytics"]

pipeline = [
    {"$match": {"status": {"$in": [
        "completed", "shipped", "delivered"
    ]}}},
    {"$unwind": "$items"},
    {"$lookup": {
        "from": "products",
        "localField": "items.product_id",
        "foreignField": "product_id",
        "as": "product"
    }},
    {"$unwind": "$product"},
    {"$lookup": {
        "from": "categories",
        "localField": "product.category_id",
        "foreignField": "category_id",
        "as": "category"
    }},
    {"$unwind": "$category"},
    {"$group": {
        "_id": "$category.category_id",
        "category_name": {"$first": "$category.name"},
        "total_revenue": {"$sum": "$items.subtotal"},
        "items_sold": {"$sum": "$items.quantity"},
        "transactions": {"$addToSet": "$transaction_id"}
    }},
    {"$project": {
        "_id": 0,
        "category_id": "$_id",
        "category_name": 1,
        "total_revenue": {"$round": ["$total_revenue", 2]},
        "items_sold": 1,
        "transaction_count": {"$size": "$transactions"}
    }},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 10}
]

results = list(db.transactions.aggregate(pipeline))

print("\nTOP 10 PRODUCT CATEGORIES BY REVENUE")
print("-" * 75)

for rank, row in enumerate(results, 1):
    print(
        f"{rank}. {row['category_id']} | "
        f"{row['category_name']} | "
        f"Revenue: ${row['total_revenue']:,.2f} | "
        f"Units: {row['items_sold']} | "
        f"Transactions: {row['transaction_count']}"
    )

client.close()
