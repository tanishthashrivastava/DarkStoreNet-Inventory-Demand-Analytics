-- ==========================================
-- QUERY 1: STORE PERFORMANCE
-- ==========================================

SELECT
    s.store_id,
    s.city_zone,
    s.store_type,

    COUNT(DISTINCT o.order_id) AS total_orders,

    SUM(o.quantity) AS total_units_sold,

    ROUND(
        AVG(o.quantity),
        2
    ) AS avg_units_per_order

FROM stores s

LEFT JOIN daily_orders o
    ON s.store_id = o.store_id

GROUP BY
    s.store_id,
    s.city_zone,
    s.store_type

ORDER BY
    total_units_sold DESC; 


-- ==========================================
-- QUERY 2: STOCKOUT FREQUENCY BY STORE
-- ==========================================

SELECT
    s.store_id,
    s.city_zone,
    s.store_type,

    COUNT(*) AS total_inventory_snapshots,

    SUM(
        CASE
            WHEN i.stock_on_hand = 0
            THEN 1
            ELSE 0
        END
    ) AS stockout_snapshots,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN i.stock_on_hand = 0
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS stockout_rate_percent

FROM stores s

JOIN inventory_snapshots i
    ON s.store_id = i.store_id

GROUP BY
    s.store_id,
    s.city_zone,
    s.store_type

ORDER BY
    stockout_rate_percent DESC;


-- ==========================================
-- QUERY 3: RESTOCK LAG BY STORE
-- ==========================================

SELECT
    s.store_id,
    s.city_zone,
    s.store_type,

    COUNT(r.restock_id) AS total_restock_events,

    ROUND(
        AVG(r.lag_days),
        2
    ) AS avg_restock_lag_days,

    MAX(r.lag_days) AS max_restock_lag_days

FROM stores s

LEFT JOIN restock_events r
    ON s.store_id = r.store_id

GROUP BY
    s.store_id,
    s.city_zone,
    s.store_type

ORDER BY
    avg_restock_lag_days DESC;


-- ==========================================
-- QUERY 4: STORE RANKING
-- ==========================================

WITH store_sales AS (

    SELECT
        store_id,
        SUM(quantity) AS total_units_sold

    FROM daily_orders

    GROUP BY store_id
)

SELECT
    store_id,
    total_units_sold,

    RANK() OVER (
        ORDER BY total_units_sold DESC
    ) AS store_rank

FROM store_sales

ORDER BY store_rank;


-- ==========================================
-- QUERY 5: SKU PERFORMANCE RANKING
-- ==========================================

WITH sku_sales AS (

    SELECT
        sku_id,

        SUM(quantity) AS total_units_sold,

        COUNT(DISTINCT order_id) AS total_orders

    FROM daily_orders

    GROUP BY
        sku_id
),

ranked_skus AS (

    SELECT
        sku_id,

        total_units_sold,

        total_orders,

        RANK() OVER (
            ORDER BY total_units_sold DESC
        ) AS sales_rank

    FROM sku_sales
)

SELECT
    sku_id,

    total_units_sold,

    total_orders,

    sales_rank

FROM ranked_skus

ORDER BY
    sales_rank;


-- ==========================================
-- QUERY 6: TOP 5 SKUs PER STORE
-- ==========================================

WITH store_sku_sales AS (

    SELECT
        store_id,
        sku_id,

        SUM(quantity) AS total_units_sold

    FROM daily_orders

    GROUP BY
        store_id,
        sku_id
),

ranked_sales AS (

    SELECT
        store_id,
        sku_id,
        total_units_sold,

        RANK() OVER (
            PARTITION BY store_id
            ORDER BY total_units_sold DESC
        ) AS sku_rank

    FROM store_sku_sales
)

SELECT
    store_id,
    sku_id,
    total_units_sold,
    sku_rank

FROM ranked_sales

WHERE sku_rank <= 5

ORDER BY
    store_id,
    sku_rank;


-- ==========================================
-- QUERY 7: DEMAND BY STORE TYPE,
--           HOUR AND DAY TYPE
-- ==========================================

SELECT
    s.store_type,

    o.order_hour,

    CASE
        WHEN CAST(
            strftime(
                '%w',
                o.order_date
            ) AS INTEGER
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


-- ==========================================
-- QUERY 8: WEEK-OVER-WEEK DEMAND CHANGE
-- ==========================================

WITH weekly_demand AS (

    SELECT
        store_id,

        strftime(
            '%Y-%W',
            order_date
        ) AS week,

        SUM(quantity) AS total_demand

    FROM daily_orders

    GROUP BY
        store_id,
        week
),

demand_comparison AS (

    SELECT
        store_id,
        week,
        total_demand,

        LAG(total_demand) OVER (
            PARTITION BY store_id
            ORDER BY week
        ) AS previous_week_demand

    FROM weekly_demand
)

SELECT
    store_id,
    week,
    total_demand,
    previous_week_demand,

    ROUND(
        100.0 *
        (
            total_demand
            - previous_week_demand
        )
        / NULLIF(
            previous_week_demand,
            0
        ),
        2
    ) AS demand_change_percent

FROM demand_comparison

ORDER BY
    store_id,
    week;


-- ==========================================
-- QUERY 9: STORE-SKU STOCKOUT ANALYSIS
-- ==========================================

WITH stockout_analysis AS (

    SELECT
        store_id,
        sku_id,

        COUNT(*) AS total_snapshots,

        SUM(
            CASE
                WHEN stock_on_hand = 0
                THEN 1
                ELSE 0
            END
        ) AS stockout_days,

        AVG(stock_on_hand) AS avg_stock

    FROM inventory_snapshots

    GROUP BY
        store_id,
        sku_id
)

SELECT
    store_id,
    sku_id,
    total_snapshots,
    stockout_days,

    ROUND(
        100.0 * stockout_days
        / NULLIF(total_snapshots, 0),
        2
    ) AS stockout_rate_percent,

    ROUND(
        avg_stock,
        2
    ) AS avg_stock

FROM stockout_analysis

WHERE stockout_days > 0

ORDER BY
    stockout_rate_percent DESC,
    stockout_days DESC;


-- ==========================================
-- QUERY 10: STOCKOUT RISK CLASSIFICATION
-- ==========================================

WITH stockout_analysis AS (

    SELECT
        store_id,
        sku_id,

        COUNT(*) AS total_snapshots,

        SUM(
            CASE
                WHEN stock_on_hand = 0
                THEN 1
                ELSE 0
            END
        ) AS stockout_days

    FROM inventory_snapshots

    GROUP BY
        store_id,
        sku_id
),

risk_calculation AS (

    SELECT
        store_id,
        sku_id,
        total_snapshots,
        stockout_days,

        ROUND(
            100.0 * stockout_days
            / NULLIF(total_snapshots, 0),
            2
        ) AS stockout_rate_percent

    FROM stockout_analysis
)

SELECT
    store_id,
    sku_id,
    stockout_days,
    stockout_rate_percent,

    CASE

        WHEN stockout_rate_percent >= 10
            THEN 'High'

        WHEN stockout_rate_percent >= 5
            THEN 'Medium'

        ELSE 'Low'

    END AS risk_level

FROM risk_calculation

ORDER BY
    CASE
        WHEN stockout_rate_percent >= 10 THEN 1
        WHEN stockout_rate_percent >= 5 THEN 2
        ELSE 3
    END,

    stockout_rate_percent DESC;




