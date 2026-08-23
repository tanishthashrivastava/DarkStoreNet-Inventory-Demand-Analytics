# DarkStoreNet: Inventory, Demand & Redistribution Analytics

An end-to-end data analytics project for a quick-commerce dark-store network. The project analyzes historical demand, forecasts future demand, identifies stockout risks, and generates inventory redistribution recommendations.

**Tech Stack:** Python, Pandas, NumPy, SQL, SQLite, Power BI, Git & GitHub

---

## 📌 Project Overview

This project helps answer key inventory and operations questions:

- Which stores and products have the highest demand?
- How does demand vary across stores, categories, and time?
- Which store-SKU combinations are at risk of stockout?
- What demand is expected over the next 7 days?
- How can excess inventory be redistributed to reduce stockout risk?

The complete workflow includes:

```text
Data Generation
      ↓
SQL Analysis
      ↓
Demand Forecasting
      ↓
Stockout Risk Analysis
      ↓
Redistribution Recommendations
      ↓
Recommendation Validation
      ↓
Power BI Dashboard

📊 Dataset
The synthetic dark-store network includes:

  • 18 Stores
  • 250 Products/SKUs
  • 8 Months of Historical Data
  •243 Days of Order History

Main datasets:
  • stores.csv
  • products.csv
  • daily_orders.csv
  • inventory.csv
  • demand_forecast.csv
  • stockout_risk.csv
  • redistribution_recommendations.csv

📈 Key Results
| Metric                         |   Result |
| ------------------------------ | -------: |
| Forecast Records               |   31,500 |
| Average MAPE                   |   63.88% |
| Redistribution Recommendations |    5,149 |
| Recommendations Validated      |       10 |
| Validation Rate                | **100%** |

🔍 Key Features
📈 Demand Forecasting
  • Store-SKU level demand forecasting
  • 7-day moving average approach
  • Weekday vs weekend demand adjustment
  • Actual vs predicted demand evaluation
⚠️ Stockout Risk Analysis
Risk is evaluated using:
  • Current stock
  • Forecasted demand
  • Lead time
  • Days of inventory cover

Store-SKU combinations are classified as:
🔴 High Risk | 🟠 Medium Risk | 🟢 Low Risk

🔄 Redistribution Engine
The project generates actionable recommendations such as:
  Move inventory from a store with excess stock to a store facing potential stockout.
Each recommendation includes the source store, destination store, SKU, recommended quantity, risk level, stockout urgency, and projected improvement after transfer.

📊 Power BI Dashboard
The project includes a 5-page interactive Power BI dashboard:
  1. Network Overview
    Network-level KPIs, store and product insights.

  2. Demand & Inventory Analysis
    Demand trends, category performance, and inventory analysis.

  3. Demand Forecast
    7-day forecast, actual vs predicted demand, and forecast accuracy.

  4. Stockout Risk Watchlist
    Prioritized High/Medium/Low risk store-SKU combinations.

  5. Redistribution Recommendations
    Actionable inventory transfer recommendations across the network.

🖼️ Dashboard Preview
1️⃣ Network Overview
<img width="1037" height="651" alt="Dashboard 1  Network Overview" src="https://github.com/user-attachments/assets/a842bc95-1a16-4bd4-990c-18e02787d72f" />


2️⃣ Demand & Inventory Analysis
<img width="1165" height="653" alt="Dashboard 2 Demand   Inventory Analysis" src="https://github.com/user-attachments/assets/3882b4e2-b378-481c-8f44-969d9921fe5c" />

3️⃣ Demand Forecast
<img width="1167" height="658" alt="Dashboard 3 Demand Forecast" src="https://github.com/user-attachments/assets/9e46c249-8318-438b-ac81-3b8a8f3b67c6" />

4️⃣ Stockout Risk Watchlist
<img width="1137" height="654" alt="Dashboard 4 Stockout Risk Watchlist" src="https://github.com/user-attachments/assets/cb33e8fa-9485-46fb-979e-9745bb480b89" />

5️⃣ Redistribution Recommendations
<img width="1380" height="777" alt="Dashboard 5 Redistribution Recommendations" src="https://github.com/user-attachments/assets/4eca65e5-afdf-4b1c-8f05-e7061a4566ac" />
