import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime

# -----------------------------
# SETUP
# -----------------------------
fake = Faker("en_IN")
np.random.seed(42)

# -----------------------------
# 1. GENERATE STORES
# -----------------------------
num_stores = 18

store_types = (
    ["residential"] * 10 +
    ["commercial"] * 8
)

zones = [
    "North Zone",
    "South Zone",
    "East Zone",
    "West Zone",
    "Central Zone"
]

stores = []

for i in range(1, num_stores + 1):

    store = {
        "store_id": f"STORE_{i:02d}",
        "city_zone": np.random.choice(zones),
        "store_type": store_types[i - 1],
        "capacity_sqft": np.random.randint(800, 2500),
        "launch_date": fake.date_between(
            start_date="-3y",
            end_date="-6m"
        )
    }

    stores.append(store)

stores_df = pd.DataFrame(stores)

# -----------------------------
# 2. GENERATE PRODUCTS
# -----------------------------
num_products = 250

categories = [
    "Dairy",
    "Grocery",
    "Fruits & Vegetables",
    "Snacks",
    "Beverages",
    "Personal Care",
    "Household",
    "Bakery",
    "Frozen Food",
    "Staples"
]

product_names = {
    "Dairy": ["Milk", "Curd", "Paneer", "Cheese", "Butter"],
    "Grocery": ["Biscuits", "Noodles", "Pasta", "Sauce", "Jam"],
    "Fruits & Vegetables": ["Apple", "Banana", "Tomato", "Potato", "Onion"],
    "Snacks": ["Chips", "Namkeen", "Popcorn", "Chocolate", "Cookies"],
    "Beverages": ["Coke", "Juice", "Water", "Coffee", "Energy Drink"],
    "Personal Care": ["Shampoo", "Soap", "Toothpaste", "Face Wash", "Lotion"],
    "Household": ["Detergent", "Dishwash", "Cleaner", "Tissue", "Garbage Bags"],
    "Bakery": ["Bread", "Bun", "Cake", "Muffin", "Croissant"],
    "Frozen Food": ["Ice Cream", "Frozen Peas", "Frozen Corn", "Fries", "Nuggets"],
    "Staples": ["Rice", "Wheat", "Sugar", "Salt", "Dal"]
}

products = []

for i in range(1, num_products + 1):

    category = np.random.choice(categories)

    base_name = np.random.choice(product_names[category])

    product = {
        "sku_id": f"SKU_{i:03d}",
        "name": f"{base_name} {i}",
        "category": category,
        "unit_cost": round(np.random.uniform(20, 400), 2),
        "unit_price": 0,
        "shelf_life_days": np.random.randint(3, 365)
    }

    # Selling price = cost + margin
    product["unit_price"] = round(
        product["unit_cost"] * np.random.uniform(1.15, 1.50),
        2
    )

    products.append(product)

products_df = pd.DataFrame(products)

# -----------------------------
# 3. SAVE DATA
# -----------------------------

stores_df.to_csv("stores.csv", index=False)
products_df.to_csv("products.csv", index=False)

# -----------------------------
# 4. BASIC CHECK
# -----------------------------

print("DATA GENERATION COMPLETE")
print("-------------------------")

print(f"Stores generated   : {len(stores_df)}")
print(f"Products generated : {len(products_df)}")

print("\nSTORE SAMPLE:")
print(stores_df.head())

print("\nPRODUCT SAMPLE:")
print(products_df.head()) 