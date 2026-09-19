CREATE TABLE customer_analytics AS

WITH order_metrics AS (
    SELECT c.customer_id, COUNT(DISTINCT o.order_id) AS total_orders,
           COALESCE(SUM(o.total_order_value), 0) AS total_spending,
           COALESCE(AVG(o.total_order_value), 0) AS avg_order_value,
           MIN(o.order_date) AS first_order_date,
           MAX(o.order_date) AS last_order_date
    FROM customers c LEFT JOIN orders o
    ON c.customer_id = o.customer_id AND o.order_status = 'Delivered'
    GROUP BY c.customer_id
),

product_metrics AS (
    SELECT o.customer_id, COUNT(DISTINCT oi.product_id) AS unique_products_bought,
           COALESCE(SUM(oi.quantity), 0) AS total_items_purchased
    FROM orders o JOIN order_items oi
    ON o.order_id = oi.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id
),

category_sales AS (
    SELECT o.customer_id, p.category,SUM(oi.item_total) AS category_revenue
    FROM orders o JOIN order_items oi
    ON o.order_id = oi.order_id 
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Delivered'
    GROUP BY  o.customer_id, p.category
),

favorite_category AS (
    SELECT customer_id, category AS favorite_category
    FROM (
        SELECT customer_id,category,
            ROW_NUMBER() OVER ( PARTITION BY customer_id ORDER BY category_revenue DESC) AS category_rank
        FROM category_sales
    ) ranked
    WHERE category_rank = 1
),

customer_base AS (
    SELECT
        customer_id,first_name,last_name,
        age,gender,city,state,occupation,income,
        marital_status,preferred_channel,loyalty_tier
    FROM customers
)

SELECT
    cb.customer_id,cb.first_name,cb.last_name,
    cb.age,cb.gender,cb.city,cb.state,
    cb.occupation,cb.income,cb.marital_status,
    cb.preferred_channel,cb.loyalty_tier,

    om.total_orders,om.total_spending,om.avg_order_value,
    om.first_order_date,om.last_order_date,

    COALESCE(pm.unique_products_bought, 0) AS unique_products_bought,
    COALESCE(pm.total_items_purchased, 0)AS total_items_purchased,
    fc.favorite_category,

    CASE
        WHEN COALESCE(om.total_spending, 0) >= 100000 THEN 'High Value'
        WHEN COALESCE(om.total_spending, 0) >= 50000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_value_segment

FROM customer_base cb
LEFT JOIN order_metrics om
    ON cb.customer_id = om.customer_id
LEFT JOIN product_metrics pm
    ON cb.customer_id = pm.customer_id
LEFT JOIN favorite_category fc
    ON cb.customer_id = fc.customer_id;



SELECT *
FROM customer_analytics
LIMIT 20;

SELECT COUNT(*)
FROM customer_analytics;

SELECT column_name,  data_type
FROM information_schema.columns
WHERE table_name = 'customer_analytics'
ORDER BY ordinal_position;

SELECT customer_id,
    CURRENT_DATE - last_order_date AS recency_days
FROM customer_analytics;