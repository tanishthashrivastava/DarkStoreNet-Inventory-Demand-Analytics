import pandas as pd
import numpy as np

np.random.seed(42)

# ==========================================
# LOAD DATA
# ==========================================

stores = pd.read_csv("stores.csv")
products = pd.read_csv("products.csv")
inventory = pd.read_csv("inventory_snapshots.csv")

inventory["snapshot_date"] = pd.to_datetime(
    inventory["snapshot_date"]
)

print("Preparing restock events...")


# ==========================================
# TARGET = 7,000 EVENTS
# ==========================================

N = 7000


# ==========================================
# RANDOMLY SELECT STORE-SKU COMBINATIONS
# ==========================================

store_ids = stores["store_id"].values
sku_ids = products["sku_id"].values

selected_stores = np.random.choice(
    store_ids,
    size=N,
    replace=True
)

selected_skus = np.random.choice(
    sku_ids,
    size=N,
    replace=True
)


# ==========================================
# RANDOM RESTOCK DATES
# ==========================================

dates = inventory["snapshot_date"].values

selected_dates = np.random.choice(
    dates,
    size=N,
    replace=True
)


# ==========================================
# CREATE DATAFRAME
# ==========================================

restock_df = pd.DataFrame({
    "restock_id": [
        f"RESTOCK_{i:06d}"
        for i in range(1, N + 1)
    ],
    "store_id": selected_stores,
    "sku_id": selected_skus,
    "restock_date": selected_dates
})


# ==========================================
# STORE TYPE / CONDITION
# ==========================================

understocked_stores = {
    "STORE_03",
    "STORE_07",
    "STORE_11"
}

overstocked_stores = {
    "STORE_05",
    "STORE_12",
    "STORE_16"
}


# ==========================================
# RESTOCK LAG
# ==========================================

restock_df["lag_days"] = np.random.randint(
    1,
    5,
    size=N
)

# Understocked stores = slower
under_mask = restock_df["store_id"].isin(
    understocked_stores
)

restock_df.loc[
    under_mask,
    "lag_days"
] = np.random.randint(
    3,
    7,
    size=under_mask.sum()
)


# Overstocked stores = faster
over_mask = restock_df["store_id"].isin(
    overstocked_stores
)

restock_df.loc[
    over_mask,
    "lag_days"
] = np.random.randint(
    1,
    3,
    size=over_mask.sum()
)


# ==========================================
# REORDER POINT
# ==========================================

reorder_points = (
    inventory[
        ["store_id", "sku_id", "reorder_point"]
    ]
    .drop_duplicates(
        ["store_id", "sku_id"]
    )
)

restock_df = restock_df.merge(
    reorder_points,
    on=[
        "store_id",
        "sku_id"
    ],
    how="left"
)

restock_df["reorder_point"] = (
    restock_df["reorder_point"]
    .fillna(5)
)


# ==========================================
# QUANTITY RECEIVED
# ==========================================

random_factor = np.random.uniform(
    1.5,
    2.5,
    size=N
)

restock_df["quantity_received"] = (
    restock_df["reorder_point"]
    * random_factor
).astype(int)


# Understocked → smaller replenishment
restock_df.loc[
    under_mask,
    "quantity_received"
] = (
    restock_df.loc[
        under_mask,
        "reorder_point"
    ]
    * np.random.uniform(
        1.0,
        1.8,
        size=under_mask.sum()
    )
).astype(int)


# Overstocked → larger replenishment
restock_df.loc[
    over_mask,
    "quantity_received"
] = (
    restock_df.loc[
        over_mask,
        "reorder_point"
    ]
    * np.random.uniform(
        2.5,
        4.0,
        size=over_mask.sum()
    )
).astype(int)


restock_df["quantity_received"] = np.maximum(
    restock_df["quantity_received"],
    5
)


# ==========================================
# FINAL COLUMNS
# ==========================================

restock_df = restock_df[
    [
        "restock_id",
        "store_id",
        "sku_id",
        "restock_date",
        "quantity_received",
        "lag_days"
    ]
]


# ==========================================
# SORT
# ==========================================

restock_df = restock_df.sort_values(
    "restock_date"
).reset_index(drop=True)


# ==========================================
# SAVE
# ==========================================

restock_df.to_csv(
    "restock_events.csv",
    index=False
)


# ==========================================
# VALIDATION
# ==========================================

print("\n================================")
print("RESTOCK GENERATION COMPLETE")
print("================================")

print(
    "Total events:",
    len(restock_df)
)

print(
    "Unique stores:",
    restock_df["store_id"].nunique()
)

print(
    "Unique SKUs:",
    restock_df["sku_id"].nunique()
)

print(
    "Average quantity:",
    round(
        restock_df["quantity_received"].mean(),
        2
    )
)

print(
    "Average lag:",
    round(
        restock_df["lag_days"].mean(),
        2
    ),
    "days"
)

print("\nSample:")
print(restock_df.head())

print(
    "\nCreated: restock_events.csv"
) 