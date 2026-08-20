import sqlite3
import pandas as pd
import numpy as np

# ==========================================
# SETUP
# ==========================================

DB_NAME = "darkstorenet.db"

conn = sqlite3.connect(DB_NAME)

print("Loading order data...")

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

print(
    "Total order records:",
    len(orders)
)


# ==========================================
# DAILY DEMAND
# ==========================================

daily_demand = (
    orders
    .groupby(
        [
            "store_id",
            "sku_id",
            "order_date"
        ],
        as_index=False
    )["quantity"]
    .sum()
)

print(
    "Daily demand records:",
    len(daily_demand)
)


# ==========================================
# FORECAST FUNCTION
# ==========================================

def forecast_store_sku(
    data,
    forecast_days=7
):

    data = data.sort_values(
        "order_date"
    ).copy()

    # ------------------------------
    # Last 14 days = test period
    # ------------------------------

    if len(data) <= 21:
        return None

    train = data.iloc[:-14].copy()
    test = data.iloc[-14:].copy()

    # ------------------------------
    # 7-day moving average
    # ------------------------------

    recent_demand = train[
        "quantity"
    ].tail(7)

    moving_average = (
        recent_demand.mean()
    )

    # ------------------------------
    # Weekend multiplier
    # ------------------------------

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
            weekend_avg /
            weekday_avg
        )

    # Keep multiplier reasonable
    weekend_multiplier = np.clip(
        weekend_multiplier,
        0.8,
        1.8
    )

    # ------------------------------
    # Generate forecast
    # ------------------------------

    last_date = data[
        "order_date"
    ].max()

    forecast_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=forecast_days
    )

    forecast_values = []

    for date in forecast_dates:

        if date.dayofweek >= 5:

            forecast = (
                moving_average
                * weekend_multiplier
            )

        else:

            forecast = moving_average

        forecast_values.append(
            max(0, forecast)
        )

    forecast_df = pd.DataFrame({
        "forecast_date": forecast_dates,
        "forecast_demand": forecast_values
    })

    # ------------------------------
    # Test prediction
    # ------------------------------

    test_predictions = []

    for date in test["order_date"]:

        if date.dayofweek >= 5:

            prediction = (
                moving_average
                * weekend_multiplier
            )

        else:

            prediction = moving_average

        test_predictions.append(
            max(0, prediction)
        )

    test = test.copy()

    test["predicted_demand"] = (
        test_predictions
    )

    # ------------------------------
    # MAPE
    # ------------------------------

    actual = test["quantity"].values

    predicted = (
        test["predicted_demand"].values
    )

    non_zero = actual != 0

    if non_zero.sum() > 0:

        mape = np.mean(
            np.abs(
                (
                    actual[non_zero]
                    - predicted[non_zero]
                )
                /
                actual[non_zero]
            )
        ) * 100

    else:

        mape = np.nan

    return (
        forecast_df,
        mape
    )


# ==========================================
# RUN FORECAST FOR EVERY STORE-SKU
# ==========================================

print("\nGenerating forecasts...")

forecast_results = []
accuracy_results = []

groups = daily_demand.groupby(
    [
        "store_id",
        "sku_id"
    ]
)

for (
    store_id,
    sku_id
), group in groups:

    result = forecast_store_sku(
        group,
        forecast_days=7
    )

    if result is None:
        continue

    forecast_df, mape = result

    forecast_df["store_id"] = store_id
    forecast_df["sku_id"] = sku_id

    forecast_results.append(
        forecast_df
    )

    accuracy_results.append({
        "store_id": store_id,
        "sku_id": sku_id,
        "MAPE": mape
    })


# ==========================================
# COMBINE RESULTS
# ==========================================

forecast_output = pd.concat(
    forecast_results,
    ignore_index=True
)

accuracy_output = pd.DataFrame(
    accuracy_results
)


# ==========================================
# SAVE FORECAST
# ==========================================

forecast_output = forecast_output[
    [
        "store_id",
        "sku_id",
        "forecast_date",
        "forecast_demand"
    ]
]

forecast_output.to_csv(
    "demand_forecast.csv",
    index=False
)

accuracy_output.to_csv(
    "forecast_accuracy.csv",
    index=False
)


# ==========================================
# SUMMARY
# ==========================================

print("\n================================")
print("FORECASTING COMPLETE")
print("================================")

print(
    "Forecast records:",
    len(forecast_output)
)

print(
    "Store-SKU pairs:",
    len(accuracy_output)
)

print(
    "Average MAPE:",
    round(
        accuracy_output["MAPE"].mean(),
        2
    ),
    "%"
)

print("\nForecast sample:")

print(
    forecast_output.head(10)
)

print("\nAccuracy sample:")

print(
    accuracy_output.head(10)
)

print("\nCreated files:")

print("demand_forecast.csv")
print("forecast_accuracy.csv")