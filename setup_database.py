import sqlite3
import pandas as pd
import os

# ==========================================
# DATABASE
# ==========================================

DB_NAME = "darkstorenet.db"

conn = sqlite3.connect(DB_NAME)

print("Connected to SQLite database.")


# ==========================================
# CSV FILES
# ==========================================

files = {
    "stores": "stores.csv",
    "products": "products.csv",
    "daily_orders": "daily_orders.csv",
    "inventory_snapshots": "inventory_snapshots.csv",
    "restock_events": "restock_events.csv"
}


# ==========================================
# LOAD EACH CSV
# ==========================================

for table_name, file_name in files.items():

    print(f"\nLoading {file_name}...")

    if not os.path.exists(file_name):
        print(f"ERROR: {file_name} not found.")
        continue

    df = pd.read_csv(file_name)

    # Convert dates
    if "launch_date" in df.columns:
        df["launch_date"] = pd.to_datetime(
            df["launch_date"]
        ).dt.strftime("%Y-%m-%d")

    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(
            df["order_date"]
        ).dt.strftime("%Y-%m-%d")

    if "snapshot_date" in df.columns:
        df["snapshot_date"] = pd.to_datetime(
            df["snapshot_date"]
        ).dt.strftime("%Y-%m-%d")

    if "restock_date" in df.columns:
        df["restock_date"] = pd.to_datetime(
            df["restock_date"]
        ).dt.strftime("%Y-%m-%d")

    # Write to SQLite
    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    print(
        f"Loaded {len(df):,} rows into {table_name}"
    )


# ==========================================
# CREATE INDEXES
# ==========================================

print("\nCreating indexes...")


indexes = [

    """
    CREATE INDEX IF NOT EXISTS
    idx_orders_store
    ON daily_orders(store_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_orders_sku
    ON daily_orders(sku_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_orders_date
    ON daily_orders(order_date)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_inventory_store
    ON inventory_snapshots(store_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_inventory_sku
    ON inventory_snapshots(sku_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_inventory_date
    ON inventory_snapshots(snapshot_date)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_restock_store
    ON restock_events(store_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_restock_sku
    ON restock_events(sku_id)
    """
]


for index_sql in indexes:

    conn.execute(index_sql)


conn.commit()


# ==========================================
# VERIFY TABLES
# ==========================================

print("\n================================")
print("DATABASE SETUP COMPLETE")
print("================================")

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

print("\nTables in database:")

print(tables)


# ==========================================
# ROW COUNTS
# ==========================================

print("\nRow counts:")

for table_name in files.keys():

    result = pd.read_sql_query(
        f"SELECT COUNT(*) AS total FROM {table_name}",
        conn
    )

    print(
        f"{table_name:<25} "
        f"{result['total'].iloc[0]:,}"
    )


# ==========================================
# CLOSE
# ==========================================

conn.close()

print("\nDatabase saved as:")
print(DB_NAME) 