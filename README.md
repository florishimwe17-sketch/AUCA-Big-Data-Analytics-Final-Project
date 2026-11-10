# AUCA Big Data Analytics Final Project

**Project:** Distributed Multi-Model Analytics for E-commerce Data  
**Student:** Florence Imanishimwe  
**Student ID:** 101399  
**Institution:** Adventist University of Central Africa (AUCA)

## Project Overview

This individual final project explores e-commerce analytics using three technologies:

- **MongoDB:** Document storage and aggregation of customer transactions and category revenue.
- **Apache HBase:** Wide-column storage of user events and daily product metrics.
- **Apache Spark:** Batch processing, SQL analysis, and integration of e-commerce datasets.

The project uses synthetically generated e-commerce data.

## Repository Structure

| Folder | Description |
|---|---|
| `data/` | Dataset-generation scripts |
| `mongodb/` | MongoDB import and analytical queries |
| `hbase/` | HBase table definitions and loading commands |
| `spark/` | Spark processing and SQL analysis scripts |
| `visualizations/` | Chart-generation script and resulting charts |
| `report/` | Final technical report in PDF format |

## Dataset

The project generates five JSON datasets:

- `users.json`
- `products.json`
- `categories.json`
- `transactions.json`
- `sessions_0.json`

The generated JSON files are excluded from GitHub because they can be regenerated locally.

## Reproducing the Project

### 1. Prepare the environment

Install Python, MongoDB, Apache Spark with PySpark, and Apache HBase. Docker Desktop can be used to run HBase.

Install the Python dependencies required by the scripts, including `pymongo`, `pyspark`, and `matplotlib`.

### 2. Generate the dataset

From the project root, run:

```bash
python data/dataset_generator_ready.py
```

### 3. Run MongoDB analysis

Start MongoDB, then run:

```bash
python mongodb/import_data.py
python mongodb/category_revenue.py
python mongodb/customer_analysis.py
```

### 4. Run HBase analysis

Start HBase and create the required tables using the scripts and commands in `hbase/`. Load the generated event and product metrics data, then use HBase Shell to inspect the tables.

### 5. Run Spark analysis

With Apache Spark configured, execute the scripts in `spark/`:

```bash
spark-submit spark/integrated_analysis.py
spark-submit spark/spark_analysis.py
spark-submit spark/spark_sql_analysis.py
```

The commands may require environment-specific configuration.

### 6. Generate visualizations

```bash
python visualizations/create_charts.py
```

## Selected Findings

MongoDB analysis identified:

- Highest-revenue category: `cat_019` (Powell PLC), with **$126,677.59** in revenue.
- Highest-spending customer: `user_000104`, with **$12,034.07** in total spending.

HBase validation included successful storage and retrieval of user-event and product-metric records.

Further analysis and visualizations are documented in the PDF report.

## Final Report

The complete technical report is available in:

`report/Florence_Imanishimwe_AUCA_Final_Project_Report (1).pdf`

## Notes

This project was developed for academic purposes using synthetic data. Reproduction requires the relevant database services and Python dependencies to be installed and configured.
