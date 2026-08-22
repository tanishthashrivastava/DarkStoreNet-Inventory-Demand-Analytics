import pandas as pd

# ==========================================
# LOAD DATA
# ==========================================

recommendations = pd.read_csv(
    "redistribution_recommendations.csv"
)

print("\n===================================")
print("REDISTRIBUTION RECOMMENDATION CHECK")
print("===================================")

print("\nTotal recommendations:",
      len(recommendations))


# ==========================================
# TAKE 10 SAMPLE RECOMMENDATIONS
# ==========================================

sample = recommendations.head(10).copy()

print("\nValidating first 10 recommendations...\n")


# ==========================================
# VALIDATION CONDITIONS
# ==========================================

sample["quantity_valid"] = (
    sample["recommended_quantity"] > 0
)

sample["source_excess_valid"] = (
    sample["recommended_quantity"]
    <= sample["source_excess_stock"]
)

sample["source_store_not_same"] = (
    sample["source_store"]
    != sample["destination_store"]
)

sample["destination_risk_valid"] = (
    sample["destination_risk_level"]
    .isin(["High", "Medium"])
)

sample["stockout_urgency_valid"] = (
    sample["estimated_days_before_stockout"] <= 7
)

sample["projected_improvement_valid"] = (
    sample["projected_days_after_transfer"]
    > sample["estimated_days_before_stockout"]
)


# ==========================================
# FINAL VALIDATION RESULT
# ==========================================

validation_columns = [
    "quantity_valid",
    "source_excess_valid",
    "source_store_not_same",
    "destination_risk_valid",
    "stockout_urgency_valid",
    "projected_improvement_valid"
]

sample["recommendation_valid"] = (
    sample[validation_columns]
    .all(axis=1)
)


# ==========================================
# SHOW RESULTS
# ==========================================

display_columns = [
    "source_store",
    "destination_store",
    "sku_id",
    "recommended_quantity",
    "source_excess_stock",
    "destination_risk_level",
    "estimated_days_before_stockout",
    "projected_days_after_transfer",
    "recommendation_valid"
]

print(sample[display_columns].to_string(index=False))


# ==========================================
# VALIDATION METRIC
# ==========================================

valid_count = sample["recommendation_valid"].sum()

total_checked = len(sample)

validation_rate = (
    valid_count / total_checked
) * 100

print("\n===================================")
print("FINAL VALIDATION SUMMARY")
print("===================================")

print("Recommendations checked:",
      total_checked)

print("Valid recommendations:",
      valid_count)

print("Invalid recommendations:",
      total_checked - valid_count)

print(
    "Validation rate:",
    round(validation_rate, 2),
    "%"
)


# ==========================================
# SAVE VALIDATION RESULTS
# ==========================================

sample.to_csv(
    "recommendation_validation.csv",
    index=False
)

print(
    "\nValidation file created:"
)

print(
    "recommendation_validation.csv"
) 