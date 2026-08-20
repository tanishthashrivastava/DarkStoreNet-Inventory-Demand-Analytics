import pandas as pd
import numpy as np

# ==========================================
# SETUP
# ==========================================

np.random.seed(42)

stores = pd.read_csv("stores.csv")
products = pd.read_csv("products.csv")
orders = pd.read_csv("daily_orders.csv")

orders["order_date"] = pd.to_datetime(orders["order_date"])

dates = pd.date_range(
    start=orders["order_date"].min(),
    end=orders["order_date"].max(),
    freq="D"
)

print("Stores  :", len(stores))
print("Products:", len(products))
print("Days    :", len(dates))


# ==========================================
# INTENTIONAL STORE CONDITIONS
# ==========================================

# Chronic understocking
understocked_stores = {
    "STORE_03",
    "STORE_07",
    "STORE_11"
}

# Chronic overstocking
overstocked_stores = {
    "STORE_05",
    "STORE_12",
    "STORE_16"
}


# ==========================================
# 1. DAILY DEMAND
# ==========================================

print("\nCalculating daily demand...")

daily_demand = (
    orders
    .groupby(
        ["store_id", "sku_id", "order_date"],
        as_index=False
    )["quantity"]
    .sum()
)

daily_demand.rename(
    columns={"quantity": "daily_demand"},
    inplace=True
)


# ==========================================
# 2. COMPLETE STORE-SKU-DATE GRID
# ==========================================

print("Creating inventory grid...")

store_skus = (
    stores[["store_id"]]
    .assign(key=1)
    .merge(
        products[["sku_id"]].assign(key=1),
        on="key"
    )
    .drop(columns="key")
)

date_df = pd.DataFrame({
    "snapshot_date": dates
})

date_df["key"] = 1
store_skus["key"] = 1

inventory_df = (
    store_skus
    .merge(date_df, on="key")
    .drop(columns="key")
)

print(
    "Total inventory snapshots:",
    len(inventory_df)
)


# ==========================================
# 3. MERGE DEMAND
# ==========================================

print("Merging demand data...")

demand_for_merge = daily_demand.rename(
    columns={
        "order_date": "snapshot_date"
    }
)

inventory_df = inventory_df.merge(
    demand_for_merge,
    on=[
        "store_id",
        "sku_id",
        "snapshot_date"
    ],
    how="left"
)

inventory_df["daily_demand"] = (
    inventory_df["daily_demand"]
    .fillna(0)
)


# ==========================================
# 4. AVERAGE DEMAND PER STORE-SKU
# ==========================================

avg_demand = (
    daily_demand
    .groupby(
        ["store_id", "sku_id"]
    )["daily_demand"]
    .mean()
    .reset_index()
)

avg_demand.rename(
    columns={
        "daily_demand": "avg_daily_demand"
    },
    inplace=True
)

inventory_df = inventory_df.merge(
    avg_demand,
    on=["store_id", "sku_id"],
    how="left"
)

inventory_df["avg_daily_demand"] = (
    inventory_df["avg_daily_demand"]
    .fillna(1.0)
)


# ==========================================
# 5. REORDER POINT
# ==========================================

inventory_df["reorder_point"] = np.maximum(
    2,
    (inventory_df["avg_daily_demand"] * 4)
    .astype(int)
)


# ==========================================
# 6. INITIAL STOCK
# ==========================================

inventory_df["stock_on_hand"] = (
    inventory_df["avg_daily_demand"] * 10
).astype(int)

inventory_df["stock_on_hand"] = np.maximum(
    inventory_df["stock_on_hand"],
    5
)


# ==========================================
# 7. STORE PERSONALITY
# ==========================================

# Understocked stores
under_mask = inventory_df["store_id"].isin(
    understocked_stores
)

inventory_df.loc[
    under_mask,
    "stock_on_hand"
] = np.maximum(
    2,
    (
        inventory_df.loc[
            under_mask,
            "avg_daily_demand"
        ] * 3
    ).astype(int)
)


# Overstocked stores
over_mask = inventory_df["store_id"].isin(
    overstocked_stores
)

inventory_df.loc[
    over_mask,
    "stock_on_hand"
] = np.maximum(
    5,
    (
        inventory_df.loc[
            over_mask,
            "avg_daily_demand"
        ] * 18
    ).astype(int)
)


# ==========================================
# 8. SIMULATE DAILY INVENTORY
# ==========================================

print("Simulating inventory movement...")

inventory_df = inventory_df.sort_values(
    [
        "store_id",
        "sku_id",
        "snapshot_date"
    ]
).reset_index(drop=True)


# Instead of expensive row-by-row operations,
# create a simple inventory trajectory.

inventory_df["demand_factor"] = (
    inventory_df["daily_demand"]
)


# ==========================================
# STOCK MOVEMENT
# ==========================================

stock_values = []

current_store = None
current_sku = None
current_stock = 0

for row in inventory_df.itertuples(index=False):

    # New store-SKU combination
    if (
        row.store_id != current_store
        or row.sku_id != current_sku
    ):

        current_store = row.store_id
        current_sku = row.sku_id

        avg = row.avg_daily_demand

        if row.store_id in understocked_stores:

            current_stock = max(
                2,
                int(avg * 3)
            )

        elif row.store_id in overstocked_stores:

            current_stock = max(
                5,
                int(avg * 18)
            )

        else:

            current_stock = max(
                5,
                int(avg * 10)
            )

    # Consume demand
    current_stock -= int(
        row.daily_demand
    )

    current_stock = max(
        0,
        current_stock
    )

    # Small natural variation
    variation = np.random.randint(
        -1,
        3
    )

    displayed_stock = max(
        0,
        current_stock + variation
    )

    stock_values.append(
        displayed_stock
    )

    # Replenishment
    if current_stock <= row.reorder_point:

        avg = row.avg_daily_demand

        if row.store_id in understocked_stores:

            restock_qty = max(
                2,
                int(avg * 4)
            )

        elif row.store_id in overstocked_stores:

            restock_qty = max(
                5,
                int(avg * 12)
            )

        else:

            restock_qty = max(
                3,
                int(avg * 7)
            )

        current_stock += restock_qty


inventory_df["stock_on_hand"] = stock_values


# ==========================================
# 9. FINAL COLUMNS
# ==========================================

inventory_df = inventory_df[
    [
        "store_id",
        "sku_id",
        "snapshot_date",
        "stock_on_hand",
        "reorder_point"
    ]
]


# ==========================================
# 10. SAVE
# ==========================================

inventory_df.to_csv(
    "inventory_snapshots.csv",
    index=False
)


# ==========================================
# 11. VALIDATION
# ==========================================

print("\n========================================")
print("INVENTORY GENERATION COMPLETE")
print("========================================")

print(
    "Total snapshots :",
    len(inventory_df)
)

print(
    "Unique stores    :",
    inventory_df["store_id"].nunique()
)

print(
    "Unique SKUs      :",
    inventory_df["sku_id"].nunique()
)

print(
    "Date range       :",
    inventory_df["snapshot_date"].min(),
    "to",
    inventory_df["snapshot_date"].max()
)

print(
    "\nZero-stock snapshots:",
    (
        inventory_df["stock_on_hand"] == 0
    ).sum()
)


# ==========================================
# STORE-LEVEL STOCK CHECK
# ==========================================

print("\nAverage stock by store:")

store_stock = (
    inventory_df
    .groupby("store_id")["stock_on_hand"]
    .mean()
    .sort_values()
)

print(store_stock)


# ==========================================
# SAMPLE
# ==========================================

print("\nSample inventory records:")

print(
    inventory_df.head(10)
)

print(
    "\nFile created successfully:"
)

print(
    "inventory_snapshots.csv"
)