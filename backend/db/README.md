# Database Schema

This directory contains the database initialization script for the Customer Support system.

## Schema Overview

The database includes the following tables:

### Core Tables

1. **customers** - Customer information
   - id (UUID, Primary Key)
   - email (Unique)
   - first_name, last_name
   - phone
   - status (active, inactive, suspended)
   - created_at, updated_at

2. **products** - Product catalog
   - id (UUID, Primary Key)
   - name, description
   - price
   - stock_quantity
   - category
   - created_at

3. **orders** - Customer orders
   - id (UUID, Primary Key)
   - customer_id (Foreign Key → customers)
   - order_date
   - total_amount
   - status (pending, processing, shipped, delivered, cancelled)
   - shipping_address
   - created_at, updated_at

4. **order_items** - Order line items
   - id (UUID, Primary Key)
   - order_id (Foreign Key → orders)
   - product_id (Foreign Key → products)
   - quantity, unit_price, subtotal
   - created_at

5. **support_tickets** - Customer support tickets
   - id (UUID, Primary Key)
   - customer_id (Foreign Key → customers)
   - order_id (Foreign Key → orders, nullable)
   - subject, description
   - status (open, in_progress, resolved, closed)
   - priority (low, medium, high, urgent)
   - assigned_to
   - created_at, updated_at, resolved_at

6. **ticket_messages** - Ticket conversation messages
   - id (UUID, Primary Key)
   - ticket_id (Foreign Key → support_tickets)
   - sender_type (customer, agent, system)
   - message
   - created_at

### Views

1. **order_summary** - Aggregated order information with customer details
2. **ticket_stats** - Ticket statistics by status and priority

## Sample Data

The initialization script includes sample data:
- 5 customers
- 5 products
- 5 orders with order items
- 5 support tickets with messages

## Usage

The database is automatically initialized when the PostgreSQL container starts for the first time. The `init.sql` script is mounted to `/docker-entrypoint-initdb.d/` which PostgreSQL executes automatically.

## Example Queries

### Get all customers
```sql
SELECT * FROM customers;
```

### Get orders with customer information
```sql
SELECT * FROM order_summary;
```

### Get ticket statistics
```sql
SELECT * FROM ticket_stats;
```

### Count orders by status
```sql
SELECT status, COUNT(*) as count 
FROM orders 
GROUP BY status;
```

### Get customer's order history
```sql
SELECT o.*, c.email, c.first_name, c.last_name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.email = 'john.doe@example.com';
```

### Get open tickets with customer info
```sql
SELECT 
    t.id,
    t.subject,
    t.status,
    t.priority,
    c.email as customer_email,
    c.first_name || ' ' || c.last_name as customer_name
FROM support_tickets t
JOIN customers c ON t.customer_id = c.id
WHERE t.status = 'open'
ORDER BY 
    CASE t.priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    t.created_at;
```

## Connection

When using docker-compose, the database connection string is:
```
postgresql://postgres:postgres@postgres:5432/customersupport
```

Or using individual settings:
- Host: `postgres` (container name)
- Port: `5432`
- Database: `customersupport` (or value from DB_NAME env var)
- User: `postgres` (or value from DB_USER env var)
- Password: `postgres` (or value from DB_PASSWORD env var)

## Notes

- The script uses `IF NOT EXISTS` and `ON CONFLICT DO NOTHING` to be idempotent
- UUIDs are used for primary keys
- Foreign key constraints ensure data integrity
- Indexes are created for common query patterns
- The script can be run multiple times safely

