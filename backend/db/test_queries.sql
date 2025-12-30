-- Test queries for the Customer Support database
-- These can be used to test the SQL agent

-- Simple queries
SELECT COUNT(*) as total_customers FROM customers;
SELECT COUNT(*) as total_orders FROM orders;
SELECT COUNT(*) as total_products FROM products;
SELECT COUNT(*) as open_tickets FROM support_tickets WHERE status = 'open';

-- Customer queries
SELECT email, first_name, last_name, status FROM customers WHERE status = 'active';
SELECT * FROM customers ORDER BY created_at DESC LIMIT 5;

-- Order queries
SELECT 
    o.id,
    o.order_date,
    o.total_amount,
    o.status,
    c.email as customer_email
FROM orders o
JOIN customers c ON o.customer_id = c.id
ORDER BY o.order_date DESC;

-- Product queries
SELECT name, price, stock_quantity, category FROM products ORDER BY price DESC;
SELECT category, COUNT(*) as product_count, AVG(price) as avg_price 
FROM products 
GROUP BY category;

-- Ticket queries
SELECT 
    t.id,
    t.subject,
    t.status,
    t.priority,
    c.email as customer_email,
    t.created_at
FROM support_tickets t
JOIN customers c ON t.customer_id = c.id
WHERE t.status IN ('open', 'in_progress')
ORDER BY 
    CASE t.priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;

-- Aggregation queries
SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue
FROM orders
WHERE status != 'cancelled'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;

SELECT 
    status,
    COUNT(*) as count,
    AVG(total_amount) as avg_amount
FROM orders
GROUP BY status;

-- Join queries
SELECT 
    c.email,
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.email, c.first_name, c.last_name
ORDER BY total_spent DESC NULLS LAST;

-- Product sales
SELECT 
    p.name,
    p.category,
    SUM(oi.quantity) as total_sold,
    SUM(oi.subtotal) as total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'cancelled'
GROUP BY p.id, p.name, p.category
ORDER BY total_revenue DESC;

-- Ticket analysis
SELECT 
    priority,
    status,
    COUNT(*) as ticket_count,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, CURRENT_TIMESTAMP) - created_at))/3600) as avg_hours
FROM support_tickets
GROUP BY priority, status
ORDER BY priority, status;

-- Customer with most orders
SELECT 
    c.email,
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(DISTINCT o.id) as order_count,
    SUM(o.total_amount) as lifetime_value
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.email, c.first_name, c.last_name
HAVING COUNT(DISTINCT o.id) > 0
ORDER BY order_count DESC, lifetime_value DESC
LIMIT 10;

