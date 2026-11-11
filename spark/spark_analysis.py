
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, sum as spark_sum, count

spark = (
    SparkSession.builder
    .appName("AUCA E-Commerce Analytics")
    .master("local[2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

data_dir = Path(__file__).resolve().parent.parent / "data"

transactions = spark.read.option("multiLine", "true").json(
    str(data_dir / "transactions.json")
)

sessions = spark.read.option("multiLine", "true").json(
    str(data_dir / "sessions_0.json")
)

print("\n===== DATASET VERIFICATION =====")
print("Transactions:", transactions.count())
print("Sessions:", sessions.count())

print("\n===== REVENUE BY PRODUCT =====")

items = transactions.select(
    col("transaction_id"),
    explode(col("items")).alias("item")
)

revenue = (
    items.groupBy(col("item.product_id").alias("product_id"))
    .agg(
        spark_sum("item.subtotal").alias("gross_revenue"),
        spark_sum("item.quantity").alias("units_sold"),
        count("transaction_id").alias("transaction_lines")
    )
    .orderBy(col("gross_revenue").desc())
)

revenue.show(10, truncate=False)

print("\n===== SESSIONS BY CONVERSION STATUS =====")

sessions.groupBy("conversion_status").count().show()

from pyspark.sql.functions import size, array_distinct, sort_array, collect_set

print("\n===== DATA CLEANING AND NORMALIZATION =====")

clean_transactions = (
    transactions
    .dropna(subset=["transaction_id", "user_id"])
    .dropDuplicates(["transaction_id"])
    .filter(col("items").isNotNull())
    .filter(size(col("items")) > 0)
)

print("Clean transactions:", clean_transactions.count())

print("\n===== PRODUCT AFFINITY ANALYSIS =====")

# Extract distinct products purchased in each transaction.
purchase_items = (
    clean_transactions
    .select(
        "transaction_id",
        explode("items").alias("item")
    )
    .select(
        "transaction_id",
        col("item.product_id").alias("product_id")
    )
    .dropna(subset=["product_id"])
    .dropDuplicates(["transaction_id", "product_id"])
)

# Match products purchased together in the same transaction.
left_items = purchase_items.alias("a")
right_items = purchase_items.alias("b")

product_pairs = (
    left_items.join(
        right_items,
        (col("a.transaction_id") == col("b.transaction_id"))
        & (col("a.product_id") < col("b.product_id"))
    )
    .groupBy(
        col("a.product_id").alias("product_a"),
        col("b.product_id").alias("product_b")
    )
    .agg(
        count("*").alias("times_bought_together")
    )
    .orderBy(col("times_bought_together").desc())
)

product_pairs.show(10, truncate=False)

spark.stop()
