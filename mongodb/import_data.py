
import json
from pathlib import Path
from pymongo import MongoClient

# Connect to the local MongoDB server
client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)
client.admin.command("ping")

# Create/select the project database
db = client["auca_ecommerce_analytics"]

# Locate the generated JSON files
data_folder = Path(__file__).resolve().parent.parent / "data"

datasets = {
    "users": "users.json",
    "products": "products.json",
    "categories": "categories.json",
    "transactions": "transactions.json",
    "sessions": "sessions_0.json",
}

# Verify all files exist before importing
for filename in datasets.values():
    path = data_folder / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing dataset: {path}")

print("Connected to MongoDB successfully!")

for collection_name, filename in datasets.items():
    file_path = data_folder / filename

    print(f"Importing {filename}...")

    with open(file_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"{filename} must contain a JSON array")

    collection = db[collection_name]

    # Replace previous sample data if the script is rerun
    collection.delete_many({})

    if records:
        collection.insert_many(records)

    print(
        f"{collection_name}: "
        f"{collection.count_documents({})} records imported"
    )

# Create indexes for common analytical lookups
db.users.create_index("user_id", unique=True)
db.products.create_index("product_id", unique=True)
db.categories.create_index("category_id", unique=True)
db.transactions.create_index("user_id")
db.transactions.create_index("session_id")
db.sessions.create_index("session_id", unique=True)
db.sessions.create_index("user_id")

print("\nMongoDB import completed successfully!")
client.close()
