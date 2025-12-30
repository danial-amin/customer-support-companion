# Analytics Data Guide

## Overview

The `add_analytics_data.sql` script adds comprehensive data designed for analysis and querying. This data includes:

- **20 additional customers** (total: 35 customers)
- **15 additional products** (total: 30 products)
- **50 orders** spread across 5 months (November 2023 - March 2024)
- **Multiple order items per order** (realistic shopping patterns)
- **40+ support tickets** with various statuses, priorities, and dates

## Data Distribution

### Orders by Month

| Month | Order Count | Status Distribution |
|-------|------------|---------------------|
| November 2023 | 5 | All delivered |
| December 2023 | 13 | Mostly delivered |
| January 2024 | 11 | Mostly delivered |
| February 2024 | 12 | Mix: shipped, processing, pending |
| March 2024 | 9 | Mix: processing, pending |

### Order Status Distribution

- **Delivered**: ~30 orders (completed transactions)
- **Shipped**: ~5 orders (in transit)
- **Processing**: ~8 orders (being prepared)
- **Pending**: ~7 orders (just placed)

### Product Categories

- Gaming (chairs, keyboards, mice)
- Audio (earbuds, speakers)
- Electronics (monitors, webcams)
- Accessories (docking stations, hubs, cables)
- Furniture (desk accessories, stands)
- Storage (SSDs, external drives)

## Sample Analysis Queries

### Monthly Revenue Trends

```sql
SELECT 
    TO_CHAR(order_date, 'YYYY-MM') as month,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    MIN(total_amount) as min_order,
    MAX(total_amount) as max_order
FROM orders
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY month;
```

### Top Customers by Revenue

```sql
SELECT 
    c.email,
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.email, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 10;
```

### Product Performance

```sql
SELECT 
    p.name,
    p.category,
    COUNT(oi.id) as times_ordered,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.subtotal) as total_revenue,
    AVG(oi.unit_price) as avg_price
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name, p.category
ORDER BY total_revenue DESC NULLS LAST;
```

### Order Status Analysis

```sql
SELECT 
    status,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    MIN(order_date) as first_order,
    MAX(order_date) as last_order
FROM orders
GROUP BY status
ORDER BY order_count DESC;
```

### Support Ticket Analysis

```sql
SELECT 
    status,
    priority,
    COUNT(*) as ticket_count,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, CURRENT_TIMESTAMP) - created_at))/3600) as avg_hours_to_resolve
FROM support_tickets
GROUP BY status, priority
ORDER BY status, priority;
```

### Monthly Customer Acquisition

```sql
SELECT 
    TO_CHAR(created_at, 'YYYY-MM') as month,
    COUNT(*) as new_customers,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_customers
FROM customers
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY month;
```

### Product Category Revenue

```sql
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) as orders_with_category,
    SUM(oi.subtotal) as category_revenue,
    AVG(oi.unit_price) as avg_price
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;
```

### Customer Lifetime Value

```sql
SELECT 
    c.email,
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(DISTINCT o.id) as total_orders,
    SUM(o.total_amount) as lifetime_value,
    MIN(o.order_date) as first_order_date,
    MAX(o.order_date) as last_order_date,
    EXTRACT(DAYS FROM (MAX(o.order_date) - MIN(o.order_date))) as customer_lifespan_days
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.email, c.first_name, c.last_name
HAVING COUNT(o.id) > 1
ORDER BY lifetime_value DESC;
```

### Support Ticket Trends

```sql
SELECT 
    TO_CHAR(created_at, 'YYYY-MM') as month,
    COUNT(*) as tickets_created,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as tickets_resolved,
    COUNT(CASE WHEN priority = 'urgent' THEN 1 END) as urgent_tickets,
    AVG(CASE 
        WHEN resolved_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (resolved_at - created_at))/3600 
    END) as avg_resolution_hours
FROM support_tickets
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY month;
```

### Order Items Analysis

```sql
SELECT 
    o.order_date::date as order_date,
    COUNT(oi.id) as items_per_order,
    SUM(oi.quantity) as total_items,
    SUM(oi.subtotal) as order_total
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_date
ORDER BY order_date DESC;
```

## Running the Script

### Method 1: Using the Helper Script

```bash
cd backend/db
./add_analytics_data.sh
```

### Method 2: Using Docker

```bash
docker exec -i customer-support-db psql -U postgres -d customersupport < backend/db/add_analytics_data.sql
```

### Method 3: Direct psql

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d customersupport -f backend/db/add_analytics_data.sql
```

## Data Characteristics

### Realistic Patterns

- **Multiple orders per customer**: Some customers have 2-3 orders
- **Multiple items per order**: Orders typically have 1-4 items
- **Time-based distribution**: Orders spread across 5 months
- **Status progression**: Mix of pending, processing, shipped, delivered
- **Support ticket correlation**: Tickets linked to specific orders
- **Geographic diversity**: Customers from various locations

### Analysis-Ready Features

- **Monthly trends**: Data spans multiple months for trend analysis
- **Status tracking**: Orders in various stages for workflow analysis
- **Product variety**: Multiple categories for segmentation
- **Customer segments**: Mix of active/inactive customers
- **Support metrics**: Tickets with resolution times and priorities

## Use Cases

This data is perfect for:

1. **Revenue Analysis**: Monthly trends, customer lifetime value
2. **Product Analysis**: Best sellers, category performance
3. **Customer Analysis**: Segmentation, repeat customers
4. **Support Analysis**: Ticket resolution times, priority distribution
5. **Time Series Analysis**: Monthly patterns, seasonal trends
6. **Predictive Analysis**: Customer behavior, product demand

## Next Steps

After adding this data, you can:

1. Run SQL queries to analyze trends
2. Use the Analyzer agent to create visualizations
3. Generate reports on revenue, products, customers
4. Analyze support ticket patterns
5. Create dashboards with monthly metrics

Try queries like:
- "Show me monthly revenue trends"
- "What are the top selling products?"
- "Analyze customer lifetime value"
- "Create a chart of orders by status"
- "Show support ticket resolution times by priority"

