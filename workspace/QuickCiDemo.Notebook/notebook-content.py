# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Quick CI/CD demo
#
# Validate a tiny sales dataset and summarize revenue by region.
# All data is synthetic and stays in memory: no credentials, lakehouse,
# external connections, or environment-specific settings are needed.
#
# The PR runs this notebook's Python code through pytest without Spark.
# Merging to main deploys the definition when production is configured;
# deployment does not execute the notebook. In Fabric, use Run all.

# CELL ********************

orders = [
    {"order_id": 1, "region": "North", "amount_cents": 12000},
    {"order_id": 2, "region": "South", "amount_cents": 8000},
    {"order_id": 3, "region": "North", "amount_cents": 3500},
    {"order_id": 4, "region": "South", "amount_cents": 2500},
    {"order_id": 5, "region": "North", "amount_cents": -500},
]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Separate invalid rows and aggregate valid sales
#
# Negative amounts are rejected for this sample. Integer cents avoid
# floating-point rounding when totaling money.

# CELL ********************

valid_orders = [order for order in orders if order["amount_cents"] >= 0]
rejected_orders = [order for order in orders if order["amount_cents"] < 0]

revenue_by_region = {}
for order in valid_orders:
    region = order["region"]
    revenue_by_region[region] = revenue_by_region.get(region, 0) + order["amount_cents"]

summary = {
    "input_rows": len(orders),
    "valid_rows": len(valid_orders),
    "rejected_rows": len(rejected_orders),
    "total_revenue_cents": sum(revenue_by_region.values()),
}

for region, amount_cents in sorted(revenue_by_region.items()):
    print(f"{region}: {amount_cents / 100:.2f}")
print(summary)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Verify the expected result
#
# Expected: five input rows, four valid rows, one rejected row, and 260.00
# total revenue. A mismatch fails both Run all and the notebook's pytest check.

# CELL ********************

assert summary == {
    "input_rows": 5,
    "valid_rows": 4,
    "rejected_rows": 1,
    "total_revenue_cents": 26000,
}, f"Unexpected summary: {summary}"
assert revenue_by_region == {"North": 15500, "South": 10500}, revenue_by_region
assert summary["input_rows"] == summary["valid_rows"] + summary["rejected_rows"]
print("QuickCiDemo passed.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
