# Additional Data Summary

## Data Added by `add_sample_data.sql`

The script adds the following additional sample data to your database:

### Customers
- **10 new customers** (in addition to the original 5)
- Total after running script: **15 customers**
- Includes characters from "The Office" TV show for variety

### Products
- **10 new products** (in addition to the original 5)
- Total after running script: **15 products**
- Categories: Gaming, Audio, Wearables, Storage, Components, Accessories

### Orders
- **10 new orders** (in addition to the original 5)
- Total after running script: **15 orders**
- Various statuses: delivered, shipped, processing, pending
- Dates range from March 2024

### Order Items
- **10 new order items** (one per new order)
- Total after running script: **17 order items** (7 original + 10 new)

### Support Tickets
- **5 new support tickets** (in addition to the original 5)
- Total after running script: **10 support tickets**
- Various priorities: urgent, high, medium, low
- Various statuses: open, in_progress, resolved

### Ticket Messages
- **9 new ticket messages** (in addition to the original 7)
- Total after running script: **16 ticket messages**
- Mix of customer and agent messages

## Summary Table

| Table | Original | Added | Total After Script |
|-------|----------|-------|-------------------|
| customers | 5 | 10 | 15 |
| products | 5 | 10 | 15 |
| orders | 5 | 10 | 15 |
| order_items | 7 | 10 | 17 |
| support_tickets | 5 | 5 | 10 |
| ticket_messages | 7 | 9 | 16 |

## Running the Script

To add this data to your database:

```bash
# Method 1: Using the helper script
cd backend/db
./add_data.sh

# Method 2: Using Docker
docker exec -i customer-support-db psql -U postgres -d customersupport < backend/db/add_sample_data.sql

# Method 3: Direct psql
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d customersupport -f backend/db/add_sample_data.sql
```

## Verification

After running the script, verify the data was added:

```sql
SELECT 'customers' as table_name, COUNT(*) as count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'support_tickets', COUNT(*) FROM support_tickets
UNION ALL
SELECT 'ticket_messages', COUNT(*) FROM ticket_messages;
```
