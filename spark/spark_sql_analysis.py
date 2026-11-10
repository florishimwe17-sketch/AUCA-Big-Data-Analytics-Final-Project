
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col

spark = (
    SparkSession.builder
    .appName("AUCA Spark SQL Analysis")
    .master("local[2]")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

data_dir = Path(__file__).resolve().parent.parent / "data"

def read_json(filename):
    return spark.read.option("multiLine", "true").json(
        str(data_dir / filename)
    )

transactions = read_json("transactions.json")
products = read_json("products.json")
categories = read_json("categories.json")

# Clean data by excluding transactions without items
transactions = transactions.filter(
    col("transaction_id").isNotNull()
    & col("items").isNotNull()
)

# Flatten nested transaction items
transaction_items = transactions.select(
    "transaction_id",
    "status",
    explode("items").alias("item")
).select(
    "transaction_id",
    "status",
    col("item.product_id").alias("product_id"),
    col("item.quantity").alias("quantity"),
    col("item.subtotal").alias("subtotal")
)

transaction_items.createOrReplaceTempView("transaction_items")
products.createOrReplaceTempView("products")
categories.createOrReplaceTempView("categories")

query = """
SELECT
    c.category_id,
    c.name AS category_name,
    ROUND(SUM(t.subtotal), 2) AS gross_revenue,
    SUM(t.quantity) AS units_sold,
    COUNT(DISTINCT t.transaction_id) AS transaction_count
FROM transaction_items t
INNER JOIN products p
    ON t.product_id = p.product_id
INNER JOIN categories c
    ON p.category_id = c.category_id
WHERE t.status IN ('completed', 'shipped', 'delivered')
GROUP BY c.category_id, c.name
ORDER BY gross_revenue DESC
LIMIT 10
"""

result = spark.sql(query)

print("\n===== SPARK SQL: TOP 10 CATEGORIES =====")
result.show(10, truncate=False)

spark.stop()
