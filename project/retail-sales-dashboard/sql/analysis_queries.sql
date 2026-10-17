-- Stratax | Retail Sales Performance & Profitability
-- SQL examples intended for the cleaned CSV imported as dbo.retail_sales_clean.
-- All data is synthetic. Currency: Pakistani rupees (PKR).

-- 1. Executive KPIs
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity) AS units_sold,
    SUM(net_revenue_pkr) AS net_revenue_pkr,
    SUM(profit_pkr) AS profit_pkr,
    SUM(profit_pkr) / NULLIF(SUM(net_revenue_pkr), 0) AS profit_margin
FROM dbo.retail_sales_clean;

-- 2. Monthly trend: revenue, profit, and orders
SELECT
    DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1) AS sales_month,
    SUM(net_revenue_pkr) AS net_revenue_pkr,
    SUM(profit_pkr) AS profit_pkr,
    COUNT(DISTINCT order_id) AS total_orders
FROM dbo.retail_sales_clean
GROUP BY DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1)
ORDER BY sales_month;

-- 3. Category contribution and profitability
SELECT
    category,
    SUM(net_revenue_pkr) AS net_revenue_pkr,
    SUM(profit_pkr) AS profit_pkr,
    SUM(profit_pkr) / NULLIF(SUM(net_revenue_pkr), 0) AS profit_margin,
    SUM(discount_amount_pkr) / NULLIF(SUM(gross_revenue_pkr), 0) AS discount_rate
FROM dbo.retail_sales_clean
GROUP BY category
ORDER BY net_revenue_pkr DESC;

-- 4. Channel performance; compare margin instead of revenue alone
SELECT
    sales_channel,
    SUM(net_revenue_pkr) AS net_revenue_pkr,
    SUM(profit_pkr) AS profit_pkr,
    SUM(profit_pkr) / NULLIF(SUM(net_revenue_pkr), 0) AS profit_margin,
    SUM(discount_amount_pkr) / NULLIF(SUM(gross_revenue_pkr), 0) AS discount_rate,
    COUNT(DISTINCT order_id) AS total_orders
FROM dbo.retail_sales_clean
GROUP BY sales_channel
ORDER BY profit_margin DESC;

-- 5. City performance
SELECT
    city,
    SUM(net_revenue_pkr) AS net_revenue_pkr,
    SUM(profit_pkr) AS profit_pkr,
    COUNT(DISTINCT order_id) AS total_orders
FROM dbo.retail_sales_clean
GROUP BY city
ORDER BY net_revenue_pkr DESC;

-- 6. Product-level contribution: avoid ranking products on revenue alone
SELECT
    category,
    product,
    SUM(net_revenue_pkr) AS net_revenue_pkr,
    SUM(profit_pkr) AS profit_pkr,
    SUM(profit_pkr) / NULLIF(SUM(net_revenue_pkr), 0) AS profit_margin
FROM dbo.retail_sales_clean
GROUP BY category, product
ORDER BY profit_pkr DESC;
