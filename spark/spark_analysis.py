
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

spark.stop()
