import pandas as pd
import numpy as np

# ==========================================
# LOAD DATA
# ==========================================

inventory = pd.read_csv(
    "inventory_snapshots.csv"
)

forecast = pd.read_csv(
    "demand_forecast.csv"
)

restock = pd.read_csv(
    "restock_events.csv"
)

# Convert dates
inventory["snapshot_date"] = pd.to_datetime(
    inventory["snapshot_date"]
)

forecast["forecast_date"] = pd.to_datetime(
    forecast["forecast_date"]
)

restock["restock_date"] = pd.to_datetime(
    restock["restock_date"]
)

print("Inventory records :", len(inventory))
print("Forecast records  :", len(forecast))
print("Restock records   :", len(restock))


# ==========================================
# 1. CURRENT INVENTORY
# ==========================================

latest_inventory = (
    inventory
    .sort_values("snapshot_date")
    .groupby(
        ["store_id", "sku_id"],
        as_index=False
    )
    .tail(1)
)

latest_inventory = latest_inventory[
    [
        "store_id",
        "sku_id",
        "snapshot_date",
        "stock_on_hand",
        "reorder_point"
    ]
]


# ==========================================
# 2. AVERAGE RESTOCK LEAD TIME
# ==========================================

lead_time = (
    restock
    .groupby(
        ["store_id", "sku_id"],
        as_index=False
    )["lag_days"]
    .mean()
)

lead_time.rename(
    columns={
        "lag_days": "avg_lead_time_days"
    },
    inplace=True
)


# ==========================================
# 3. MERGE INVENTORY + LEAD TIME
# ==========================================

risk = latest_inventory.merge(
    lead_time,
    on=["store_id", "sku_id"],
    how="left"
)

# If no restock history exists
risk["avg_lead_time_days"] = (
    risk["avg_lead_time_days"]
    .fillna(3)
)

risk["avg_lead_time_days"] = np.ceil(
    risk["avg_lead_time_days"]
).astype(int)


# ==========================================
# 4. FORECAST DEMAND
# ==========================================

# Total forecast for next 7 days
forecast_demand = (
    forecast
    .groupby(
        ["store_id", "sku_id"],
        as_index=False
    )["forecast_demand"]
    .sum()
)

forecast_demand.rename(
    columns={
        "forecast_demand":
        "forecast_7_day_demand"
    },
    inplace=True
)

risk = risk.merge(
    forecast_demand,
    on=["store_id", "sku_id"],
    how="left"
)

risk["forecast_7_day_demand"] = (
    risk["forecast_7_day_demand"]
    .fillna(0)
)


# ==========================================
# 5. DAILY FORECAST
# ==========================================

risk["forecast_daily_demand"] = (
    risk["forecast_7_day_demand"] / 7
)


# ==========================================
# 6. DEMAND DURING LEAD TIME
# ==========================================

risk["lead_time_demand"] = (
    risk["forecast_daily_demand"]
    *
    risk["avg_lead_time_days"]
)


# ==========================================
# 7. DAYS OF COVER
# ==========================================

risk["days_of_cover"] = np.where(
    risk["forecast_daily_demand"] > 0,

    risk["stock_on_hand"]
    /
    risk["forecast_daily_demand"],

    999
)


# ==========================================
# 8. STOCK SURPLUS / DEFICIT
# ==========================================

risk["stock_surplus_deficit"] = (
    risk["stock_on_hand"]
    -
    risk["lead_time_demand"]
)


# ==========================================
# 9. RISK SCORE
# ==========================================

risk["risk_score"] = np.where(

    risk["forecast_daily_demand"] > 0,

    risk["stock_on_hand"]
    /
    (
        risk["forecast_daily_demand"]
        *
        risk["avg_lead_time_days"]
    ),

    999
)


# ==========================================
# 10. RISK CLASSIFICATION
# ==========================================

def classify_risk(row):

    if row["risk_score"] < 1:

        return "High"

    elif row["risk_score"] < 2:

        return "Medium"

    else:

        return "Low"


risk["risk_level"] = risk.apply(
    classify_risk,
    axis=1
)


# ==========================================
# 11. EXPECTED STOCKOUT DAYS
# ==========================================

risk["estimated_stockout_days"] = np.where(

    risk["forecast_daily_demand"] > 0,

    risk["stock_on_hand"]
    /
    risk["forecast_daily_demand"],

    999
)


# ==========================================
# 12. SORT BY RISK
# ==========================================

risk_priority = {
    "High": 1,
    "Medium": 2,
    "Low": 3
}

risk["risk_priority"] = (
    risk["risk_level"]
    .map(risk_priority)
)

risk = risk.sort_values(
    [
        "risk_priority",
        "days_of_cover"
    ]
)


# ==========================================
# 13. FINAL COLUMNS
# ==========================================

risk_output = risk[
    [
        "store_id",
        "sku_id",
        "snapshot_date",
        "stock_on_hand",
        "reorder_point",
        "avg_lead_time_days",
        "forecast_7_day_demand",
        "forecast_daily_demand",
        "lead_time_demand",
        "days_of_cover",
        "stock_surplus_deficit",
        "risk_score",
        "risk_level",
        "estimated_stockout_days"
    ]
]


# ==========================================
# SAVE
# ==========================================

risk_output.to_csv(
    "stockout_risk.csv",
    index=False
)


# ==========================================
# VALIDATION
# ==========================================

print("\n================================")
print("STOCKOUT RISK ANALYSIS COMPLETE")
print("================================")

print(
    "Total store-SKU pairs:",
    len(risk_output)
)

print("\nRisk distribution:")

print(
    risk_output["risk_level"]
    .value_counts()
)


print("\nHIGH-RISK PAIRS:")

print(
    risk_output[
        risk_output["risk_level"] == "High"
    ]
    .head(20)
    .to_string(index=False)
)


print("\nAverage days of cover:")

print(
    round(
        risk_output["days_of_cover"].mean(),
        2
    )
)


print("\nCreated file:")
print("stockout_risk.csv") 