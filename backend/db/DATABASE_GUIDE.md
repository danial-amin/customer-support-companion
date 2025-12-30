# Database Location and Data Management Guide

## Database Location

The database is a **PostgreSQL** database running in a Docker container.

### Physical Location
- **Container Name**: `customer-support-db`
- **Docker Volume**: `postgres_data` (persistent storage)
- **Volume Path in Container**: `/var/lib/postgresql/data`
- **External Port**: `5433` (mapped from internal port `5432`)

### Finding the Volume Location
To find where Docker stores the volume data on your host machine:

```bash
# List Docker volumes
docker volume ls

# Inspect the postgres_data volume
docker volume inspect postgres_data

# This will show you the "Mountpoint" which is where the data is actually stored
```

On macOS/Windows, Docker volumes are stored in the Docker VM, not directly accessible on the host.

## Database Connection Details

### Default Connection Settings
- **Host**: `localhost` (or `customer-support-db` from within Docker network)
- **Port**: `5433` (external) or `5432` (internal)
- **Database**: `customersupport` (or value from `DB_NAME` env var)
- **User**: `postgres` (or value from `DB_USER` env var)
- **Password**: `postgres` (or value from `DB_PASSWORD` env var)

### Connection String Format
```
postgresql://postgres:postgres@localhost:5433/customersupport
```

## Adding Data to the Database

### Method 1: Using the Provided SQL Script (Recommended)

1. **Use the add_sample_data.sql script**:
   ```bash
   # From the project root
   cd backend/db
   
   # Using psql directly
   PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d customersupport -f add_sample_data.sql
   
   # Or use the helper script
   ./add_data.sh
   ```

2. **Using Docker exec**:
   ```bash
   # Execute SQL script inside the container
   docker exec -i customer-support-db psql -U postgres -d customersupport < backend/db/add_sample_data.sql
   ```

### Method 2: Connect Directly with psql

```bash
# Connect to the database
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d customersupport

# Or using Docker exec
docker exec -it customer-support-db psql -U postgres -d customersupport
```

Then run SQL commands directly:
```sql
-- Example: Add a new customer
INSERT INTO customers (email, first_name, last_name, phone, status) 
VALUES ('new.customer@example.com', 'New', 'Customer', '+1-555-9999', 'active');

-- Example: Add a new product
INSERT INTO products (name, description, price, stock_quantity, category) 
VALUES ('New Product', 'Description here', 99.99, 50, 'Electronics');

-- View the data
SELECT * FROM customers;
SELECT * FROM products;
```

### Method 3: Using a Database GUI Tool

You can use tools like:
- **pgAdmin**: https://www.pgadmin.org/
- **DBeaver**: https://dbeaver.io/
- **TablePlus**: https://tableplus.com/
- **DataGrip**: https://www.jetbrains.com/datagrip/

**Connection settings**:
- Host: `localhost`
- Port: `5433`
- Database: `customersupport`
- User: `postgres`
- Password: `postgres`

### Method 4: Create Your Own SQL Script

1. Create a new SQL file in `backend/db/`:
   ```bash
   touch backend/db/my_custom_data.sql
   ```

2. Add your INSERT statements:
   ```sql
   -- Your custom data
   INSERT INTO customers (email, first_name, last_name, phone, status) 
   VALUES ('custom@example.com', 'Custom', 'User', '+1-555-0000', 'active');
   ```

3. Run it:
   ```bash
   docker exec -i customer-support-db psql -U postgres -d customersupport < backend/db/my_custom_data.sql
   ```

## Database Schema

The database contains the following tables:

1. **customers** - Customer information
2. **products** - Product catalog
3. **orders** - Customer orders
4. **order_items** - Items in each order
5. **support_tickets** - Customer support tickets
6. **ticket_messages** - Messages in support tickets

See `init.sql` for the complete schema definition.

## Useful Commands

### View all tables
```sql
\dt
```

### View table structure
```sql
\d customers
\d products
\d orders
```

### Count records in each table
```sql
SELECT 'customers' as table_name, COUNT(*) FROM customers
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

### Backup the database
```bash
docker exec customer-support-db pg_dump -U postgres customersupport > backup.sql
```

### Restore the database
```bash
docker exec -i customer-support-db psql -U postgres customersupport < backup.sql
```

### Reset the database (WARNING: Deletes all data)
```bash
# Stop and remove the container and volume
docker-compose down -v

# Start fresh
docker-compose up -d postgres
```

## Environment Variables

Database connection is configured via environment variables in `.env`:

```bash
DB_HOST=localhost
DB_PORT=5433
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=postgres
```

Or via `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/customersupport
```

## Troubleshooting

### Can't connect to database
- Check if the container is running: `docker ps | grep customer-support-db`
- Check the port: `docker port customer-support-db`
- Verify credentials in `.env` file

### Permission denied
- Make sure you're using the correct user and password
- Check if the database exists: `docker exec customer-support-db psql -U postgres -l`

### Data not persisting
- Check if the volume is mounted: `docker volume inspect postgres_data`
- Verify the volume is not being removed: `docker-compose down` (without `-v` flag)

