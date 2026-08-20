import pandas as pd
import numpy as np

# ==========================================
# SETUP
# ==========================================

np.random.seed(42)

stores = pd.read_csv("stores.csv")
products = pd.read_csv("products.csv")

# 8 months of historical data
dates = pd.date_range(
    start="2025-10-01",
    end="2026-05-31",
    freq="D"
)

print("Stores :", len(stores))
print("Products :", len(products))
print("Days :", len(dates))


# ==========================================
# PRODUCT DEMAND WEIGHTS
# ==========================================

category_weights = {
    "Dairy": 1.4,
    "Grocery": 1.2,
    "Fruits & Vegetables": 1.3,
    "Snacks": 1.1,
    "Beverages": 1.2,
    "Personal Care": 0.7,
    "Household": 0.8,
    "Bakery": 1.0,
    "Frozen Food": 0.9,
    "Staples": 1.0
}


# ==========================================
# ORDER-HOUR PROBABILITIES
# Residential stores
# ==========================================

residential_hours = np.arange(7, 23)

residential_weights = np.array([
    0.08, 0.07, 0.07, 0.06,
    0.05, 0.05, 0.05, 0.05,
    0.05, 0.05, 0.06, 0.08,
    0.10, 0.09, 0.09, 0.05
])

# Automatically make total exactly 1
residential_weights = (
    residential_weights /
    residential_weights.sum()
)


# ==========================================
# GENERATE ORDERS
# ==========================================

orders = []

order_id = 1

for _, store in stores.iterrows():

    store_type = store["store_type"]

    for date in dates:

        weekday = date.weekday()

        # --------------------------------------
        # WEEKEND EFFECT
        # --------------------------------------

        if weekday >= 5:
            weekend_multiplier = 1.40
        else:
            weekend_multiplier = 1.00

        # --------------------------------------
        # SEASONAL EFFECT
        # --------------------------------------

        month = date.month

        if month in [4, 5]:
            summer_multiplier = 1.15
        else:
            summer_multiplier = 1.00

        # --------------------------------------
        # LOOP THROUGH PRODUCTS
        # --------------------------------------

        for _, product in products.iterrows():

            category = product["category"]

            category_weight = category_weights[category]

            # ----------------------------------
            # STORE PERSONALITY
            # ----------------------------------

            store_multiplier = 1.0

            # Residential stores
            if store_type == "residential":

                if category in [
                    "Dairy",
                    "Grocery",
                    "Fruits & Vegetables",
                    "Staples"
                ]:
                    store_multiplier = 1.60

            # Commercial stores
            elif store_type == "commercial":

                if category in [
                    "Snacks",
                    "Beverages",
                    "Bakery"
                ]:
                    store_multiplier = 1.60

            # ----------------------------------
            # BASE DEMAND
            # ----------------------------------

            base_demand = (
                1.10
                * category_weight
                * store_multiplier
                * weekend_multiplier
                * summer_multiplier
            )

            # ----------------------------------
            # RANDOM DEMAND
            # ----------------------------------

            quantity = np.random.poisson(base_demand)

            # Skip zero-demand combinations
            if quantity <= 0:
                continue

            # ----------------------------------
            # ORDER HOUR
            # ----------------------------------

            if store_type == "residential":

                # Grocery / dairy etc.
                if category in [
                    "Dairy",
                    "Grocery",
                    "Fruits & Vegetables",
                    "Staples"
                ]:

                    hour = np.random.choice(
                        residential_hours,
                        p=residential_weights
                    )

                else:

                    hour = np.random.randint(8, 23)

            else:

                # Commercial store
                if category in [
                    "Snacks",
                    "Beverages",
                    "Bakery"
                ]:

                    hour = np.random.randint(9, 19)

                else:

                    hour = np.random.randint(8, 21)

            # ----------------------------------
            # CREATE ORDER RECORD
            # ----------------------------------

            orders.append({
                "order_id": f"ORD_{order_id:07d}",
                "store_id": store["store_id"],
                "sku_id": product["sku_id"],
                "order_date": date.date(),
                "quantity": quantity,
                "order_hour": hour
            })

            order_id += 1


# ==========================================
# CREATE DATAFRAME
# ==========================================

orders_df = pd.DataFrame(orders)


# ==========================================
# SHUFFLE DATA
# ==========================================

orders_df = orders_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ==========================================
# SAVE DATA
# ==========================================

orders_df.to_csv(
    "daily_orders.csv",
    index=False
)


# ==========================================
# VALIDATION
# ==========================================

print("\n================================")
print("DAILY ORDERS GENERATION COMPLETE")
print("================================")

print(
    "Total orders    :",
    len(orders_df)
)

print(
    "Unique stores   :",
    orders_df["store_id"].nunique()
)

print(
    "Unique SKUs     :",
    orders_df["sku_id"].nunique()
)

print(
    "Date range      :",
    orders_df["order_date"].min(),
    "to",
    orders_df["order_date"].max()
)


# ==========================================
# STORE TYPE VALIDATION
# ==========================================

print("\nOrders by store type:")

store_type_check = orders_df.merge(
    stores[["store_id", "store_type"]],
    on="store_id"
)

print(
    store_type_check["store_type"]
    .value_counts()
)


# ==========================================
# CATEGORY VALIDATION
# ==========================================

print("\nOrders by category:")

category_check = orders_df.merge(
    products[["sku_id", "category"]],
    on="sku_id"
)

print(
    category_check["category"]
    .value_counts()
)


# ==========================================
# SAMPLE
# ==========================================

print("\nSample orders:")

print(
    orders_df.head(10)
)


# ==========================================
# FINAL CHECK
# ==========================================

if len(orders_df) >= 150000:

    print("\nSUCCESS:")
    print("150,000+ order target achieved.")

else:

    print("\nWARNING:")
    print(
        "Order count is below 150,000."
    )
    print(
        "We will increase demand volume "
        "before moving to the next step."
    ) 