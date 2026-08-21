import sqlite3
import pandas as pd
import numpy as np

DB_NAME = "darkstorenet.db"

conn = sqlite3.connect(DB_NAME)

orders = pd.read_sql_query(
    """
    SELECT
        store_id,
        sku_id,
        order_date,
        quantity
    FROM daily_orders
    """,
    conn
)

conn.close()

orders["order_date"] = pd.to_datetime(
    orders["order_date"]
)

# Daily demand
daily_demand = (
    orders
    .groupby(
        ["store_id", "sku_id", "order_date"],
        as_index=False
    )["quantity"]
    .sum()
)

results = []

for (store_id, sku_id), group in daily_demand.groupby(
    ["store_id", "sku_id"]
):

    group = group.sort_values("order_date").copy()

    if len(group) <= 21:
        continue

    # Last 14 days = held-out test period
    train = group.iloc[:-14].copy()
    test = group.iloc[-14:].copy()

    # 7-day moving average
    moving_average = (
        train["quantity"]
        .tail(7)
        .mean()
    )

    train["day_of_week"] = (
        train["order_date"].dt.dayofweek
    )

    weekday_avg = train[
        train["day_of_week"] < 5
    ]["quantity"].mean()

    weekend_avg = train[
        train["day_of_week"] >= 5
    ]["quantity"].mean()

    if (
        pd.isna(weekday_avg)
        or weekday_avg == 0
    ):
        weekend_multiplier = 1.0
    else:
        weekend_multiplier = (
            weekend_avg / weekday_avg
        )

    weekend_multiplier = np.clip(
        weekend_multiplier,
        0.8,
        1.8
    )

    for _, row in test.iterrows():

        if row["order_date"].dayofweek >= 5:
            predicted = (
                moving_average
                * weekend_multiplier
            )
        else:
            predicted = moving_average

        predicted = max(0, predicted)

        results.append({
            "store_id": store_id,
            "sku_id": sku_id,
            "date": row["order_date"],
            "actual_demand": row["quantity"],
            "predicted_demand": predicted
        })


evaluation = pd.DataFrame(results)

evaluation["absolute_error"] = (
    abs(
        evaluation["actual_demand"]
        - evaluation["predicted_demand"]
    )
)

evaluation["absolute_percentage_error"] = np.where(
    evaluation["actual_demand"] != 0,

    evaluation["absolute_error"]
    / evaluation["actual_demand"]
    * 100,

    np.nan
)

evaluation.to_csv(
    "forecast_evaluation.csv",
    index=False
)

print("\n================================")
print("FORECAST EVALUATION CREATED")
print("================================")

print(
    "Records:",
    len(evaluation)
)

print(
    "Overall MAPE:",
    round(
        evaluation[
            "absolute_percentage_error"
        ].mean(),
        2
    ),
    "%"
)

print("\nSample:")
print(
    evaluation.head(10)
)

print("\nCreated:")
print("forecast_evaluation.csv") 