
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("AUCA Integrated Funnel Analysis")
    .master("local[2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

data_dir = Path(__file__).resolve().parent.parent / "data"

sessions = spark.read.option("multiLine", "true").json(
    str(data_dir / "sessions_0.json")
)

transactions = spark.read.option("multiLine", "true").json(
    str(data_dir / "transactions.json")
)

# Identify sessions with a completed or fulfilled transaction
purchases = (
    transactions
    .filter(F.col("status").isin(
        "completed", "shipped", "delivered"
    ))
    .filter(F.col("session_id").isNotNull())
    .groupBy("session_id")
    .agg(
        F.countDistinct("transaction_id").alias("purchase_count"),
        F.sum("total").alias("purchase_revenue")
    )
)

# Join browsing sessions with actual purchases
funnel = (
    sessions
    .join(purchases, on="session_id", how="left")
    .fillna({
        "purchase_count": 0,
        "purchase_revenue": 0.0
    })
    .withColumn(
        "has_purchase",
        F.when(F.col("purchase_count") > 0, 1).otherwise(0)
    )
)

print("\n===== OVERALL FUNNEL =====")

funnel.agg(
    F.count("*").alias("total_sessions"),
    F.sum("has_purchase").alias("purchasing_sessions"),
    F.round(
        F.avg("has_purchase") * 100, 2
    ).alias("purchase_conversion_rate_pct"),
    F.round(
        F.sum("purchase_revenue"), 2
    ).alias("linked_purchase_revenue")
).show(truncate=False)

print("\n===== CONVERSION BY REFERRAL CHANNEL =====")

channels = (
    funnel.groupBy("referrer")
    .agg(
        F.count("*").alias("sessions"),
        F.sum("has_purchase").alias("purchases"),
        F.round(
            F.avg("has_purchase") * 100, 2
        ).alias("conversion_rate_pct"),
        F.round(
            F.sum("purchase_revenue"), 2
        ).alias("revenue")
    )
    .orderBy(F.col("conversion_rate_pct").desc())
)

channels.show(truncate=False)

print("\n===== SESSION STATUS VS ACTUAL PURCHASE =====")

funnel.groupBy("conversion_status").agg(
    F.count("*").alias("sessions"),
    F.sum("has_purchase").alias("purchasing_sessions")
).show(truncate=False)

spark.stop()
