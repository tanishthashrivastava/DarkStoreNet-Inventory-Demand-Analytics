import pandas as pd
import numpy as np


# ==========================================
# LOAD DATA
# ==========================================

risk = pd.read_csv("stockout_risk.csv")
stores = pd.read_csv("stores.csv")


# ==========================================
# ADD STORE INFORMATION
# ==========================================

risk = risk.merge(
    stores[
        [
            "store_id",
            "city_zone",
            "store_type"
        ]
    ],
    on="store_id",
    how="left"
)


# ==========================================
# SOURCE STORE = OVERSTOCKED
# ==========================================

risk["excess_stock"] = (
    risk["stock_on_hand"]
    - risk["lead_time_demand"]
)

sources = risk[
    risk["excess_stock"] > 0
].copy()

sources = sources.rename(
    columns={
        "store_id": "source_store",
        "stock_on_hand": "source_stock",
        "excess_stock": "source_excess_stock",
        "forecast_daily_demand": "source_daily_demand",
        "lead_time_demand": "source_lead_time_demand"
    }
)


# ==========================================
# DESTINATION = HIGH / MEDIUM RISK
# ==========================================

destinations = risk[
    risk["risk_level"].isin(
        ["High", "Medium"]
    )
].copy()

destinations = destinations.rename(
    columns={
        "store_id": "destination_store",
        "stock_on_hand": "destination_stock",
        "risk_level": "destination_risk_level",
        "forecast_daily_demand": "destination_daily_demand",
        "lead_time_demand": "destination_lead_time_demand"
    }
)


# ==========================================
# MATCH SAME SKU + SAME CITY ZONE
# ==========================================

matches = sources.merge(
    destinations,
    on=[
        "sku_id",
        "city_zone"
    ],
    how="inner",
    suffixes=(
        "_source",
        "_destination"
    )
)


# ==========================================
# REMOVE SAME STORE
# ==========================================

matches = matches[
    matches["source_store"]
    !=
    matches["destination_store"]
].copy()


# ==========================================
# RISK PRIORITY
# ==========================================

matches["risk_priority"] = (
    matches["destination_risk_level"]
    .map({
        "High": 1,
        "Medium": 2
    })
)


# ==========================================
# RECOMMENDED TRANSFER QUANTITY
# ==========================================

matches["recommended_quantity"] = (
    np.minimum(
        matches["source_excess_stock"],
        matches["destination_lead_time_demand"]
    )
    .astype(int)
)


# Remove zero/negative transfers

matches = matches[
    matches["recommended_quantity"] > 0
].copy()


# ==========================================
# DAYS BEFORE STOCKOUT
# ==========================================

matches[
    "estimated_days_before_stockout"
] = np.where(

    matches["destination_daily_demand"] > 0,

    matches["destination_stock"]
    /
    matches["destination_daily_demand"],

    999
)


# ==========================================
# DAYS AFTER TRANSFER
# ==========================================

matches[
    "projected_days_after_transfer"
] = (

    matches["destination_stock"]
    +
    matches["recommended_quantity"]

) / np.where(

    matches["destination_daily_demand"] > 0,

    matches["destination_daily_demand"],

    1
)


# ==========================================
# RECOMMENDATION TEXT
# ==========================================

matches["recommendation"] = (
    "Move "
    + matches[
        "recommended_quantity"
    ].astype(str)
    + " units of "
    + matches["sku_id"]
    + " from "
    + matches["source_store"]
    + " to "
    + matches["destination_store"]
)


matches["reason"] = (
    "Destination is "
    + matches[
        "destination_risk_level"
    ].astype(str)
    + " risk and source has "
    + matches[
        "source_excess_stock"
    ].astype(int).astype(str)
    + " excess units"
)


# ==========================================
# RANK
# ==========================================

matches = matches.sort_values(
    [
        "risk_priority",
        "source_excess_stock"
    ],
    ascending=[
        True,
        False
    ]
)


# ==========================================
# FINAL OUTPUT
# ==========================================

recommendations = matches[
    [
        "source_store",
        "destination_store",
        "city_zone",
        "sku_id",
        "recommended_quantity",
        "destination_risk_level",
        "source_excess_stock",
        "destination_stock",
        "destination_daily_demand",
        "estimated_days_before_stockout",
        "projected_days_after_transfer",
        "recommendation",
        "reason"
    ]
].copy()


# ==========================================
# REMOVE DUPLICATES
# ==========================================

recommendations = (
    recommendations
    .drop_duplicates(
        [
            "source_store",
            "destination_store",
            "sku_id"
        ]
    )
    .reset_index(drop=True)
)


# ==========================================
# SAVE
# ==========================================

recommendations.to_csv(
    "redistribution_recommendations.csv",
    index=False
)


# ==========================================
# VALIDATION
# ==========================================

print("\n==========================================")
print("REDISTRIBUTION ENGINE COMPLETE")
print("==========================================")

print(
    "Total recommendations:",
    len(recommendations)
)

print(
    "Total units recommended:",
    recommendations[
        "recommended_quantity"
    ].sum()
)


print("\nHIGH-RISK RECOMMENDATIONS:")

high_risk = recommendations[
    recommendations[
        "destination_risk_level"
    ] == "High"
]

if len(high_risk) > 0:

    print(
        high_risk
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No High-risk recommendations found."
    )


print("\nSample recommendations:")

print(
    recommendations
    .head(10)
    .to_string(index=False)
)


print(
    "\nCreated file:"
)

print(
    "redistribution_recommendations.csv"
) 