import sqlite3
import pandas as pd

conn = sqlite3.connect("darkstorenet.db")

query = """
SELECT
    s.store_type,

    o.order_hour,

    CASE
        WHEN CAST(
            strftime('%w', o.order_date)
            AS INTEGER
        ) IN (0, 6)
        THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    SUM(o.quantity) AS total_demand,
    COUNT(o.order_id) AS total_orders

FROM daily_orders o

JOIN stores s
    ON o.store_id = s.store_id

GROUP BY
    s.store_type,
    o.order_hour,
    day_type

ORDER BY
    s.store_type,
    o.order_hour,
    day_type;
"""

result = pd.read_sql_query(query, conn)

print("\n===== DEMAND BY STORE TYPE / HOUR / DAY TYPE =====\n")

print(result.to_string(index=False))

conn.close() 