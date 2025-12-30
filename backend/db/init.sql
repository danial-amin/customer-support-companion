-- Customer Support Database Schema
-- This script initializes the database with tables and sample data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support Tickets Table
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Ticket Messages Table
CREATE TABLE IF NOT EXISTS ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('customer', 'agent', 'system')),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_id ON support_tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_priority ON support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);

-- Insert sample data
INSERT INTO customers (id, email, first_name, last_name, phone, status) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'john.doe@example.com', 'John', 'Doe', '+1-555-0101', 'active'),
    ('550e8400-e29b-41d4-a716-446655440001', 'jane.smith@example.com', 'Jane', 'Smith', '+1-555-0102', 'active'),
    ('550e8400-e29b-41d4-a716-446655440002', 'bob.johnson@example.com', 'Bob', 'Johnson', '+1-555-0103', 'active'),
    ('550e8400-e29b-41d4-a716-446655440003', 'alice.williams@example.com', 'Alice', 'Williams', '+1-555-0104', 'active'),
    ('550e8400-e29b-41d4-a716-446655440004', 'charlie.brown@example.com', 'Charlie', 'Brown', '+1-555-0105', 'inactive')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (id, name, description, price, stock_quantity, category) VALUES
    ('660e8400-e29b-41d4-a716-446655440000', 'Laptop Pro 15', 'High-performance laptop with 16GB RAM', 1299.99, 50, 'Electronics'),
    ('660e8400-e29b-41d4-a716-446655440001', 'Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 200, 'Accessories'),
    ('660e8400-e29b-41d4-a716-446655440002', 'USB-C Cable', 'High-speed USB-C charging cable', 19.99, 500, 'Accessories'),
    ('660e8400-e29b-41d4-a716-446655440003', 'Monitor 27"', '4K Ultra HD monitor', 399.99, 75, 'Electronics'),
    ('660e8400-e29b-41d4-a716-446655440004', 'Keyboard Mechanical', 'RGB mechanical keyboard', 89.99, 150, 'Accessories')
ON CONFLICT DO NOTHING;

INSERT INTO orders (id, customer_id, order_date, total_amount, status, shipping_address) VALUES
    ('770e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', '2024-01-15 10:30:00', 1329.98, 'delivered', '123 Main St, New York, NY 10001'),
    ('770e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '2024-01-20 14:20:00', 49.98, 'shipped', '456 Oak Ave, Los Angeles, CA 90001'),
    ('770e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', '2024-02-01 09:15:00', 399.99, 'processing', '789 Pine Rd, Chicago, IL 60601'),
    ('770e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', '2024-02-10 16:45:00', 89.99, 'pending', '123 Main St, New York, NY 10001'),
    ('770e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440003', '2024-02-15 11:30:00', 19.99, 'delivered', '321 Elm St, Houston, TX 77001')
ON CONFLICT DO NOTHING;

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    ('880e8400-e29b-41d4-a716-446655440000', '770e8400-e29b-41d4-a716-446655440000', '660e8400-e29b-41d4-a716-446655440000', 1, 1299.99, 1299.99),
    ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440000', '660e8400-e29b-41d4-a716-446655440001', 1, 29.99, 29.99),
    ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 1, 29.99, 29.99),
    ('880e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440002', 1, 19.99, 19.99),
    ('880e8400-e29b-41d4-a716-446655440004', '770e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440003', 1, 399.99, 399.99),
    ('880e8400-e29b-41d4-a716-446655440005', '770e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440004', 1, 89.99, 89.99),
    ('880e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440002', 1, 19.99, 19.99)
ON CONFLICT DO NOTHING;

INSERT INTO support_tickets (id, customer_id, order_id, subject, description, status, priority, assigned_to, created_at) VALUES
    ('990e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', '770e8400-e29b-41d4-a716-446655440000', 'Laptop not turning on', 'My laptop arrived but it won''t turn on. I tried charging it but nothing happens.', 'open', 'high', 'support_agent_1', '2024-02-20 10:00:00'),
    ('990e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001', 'Order delivery question', 'When will my order be delivered? I placed it 3 days ago.', 'in_progress', 'medium', 'support_agent_2', '2024-02-18 14:30:00'),
    ('990e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440002', 'Return request', 'I want to return my monitor. It has dead pixels.', 'open', 'medium', NULL, '2024-02-22 09:15:00'),
    ('990e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', NULL, 'Product inquiry', 'Do you have the Laptop Pro 15 in stock?', 'resolved', 'low', 'support_agent_1', '2024-02-15 11:20:00'),
    ('990e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440000', '770e8400-e29b-41d4-a716-446655440000', 'Warranty information', 'What is the warranty period for my laptop?', 'resolved', 'low', 'support_agent_2', '2024-02-16 15:45:00')
ON CONFLICT DO NOTHING;

INSERT INTO ticket_messages (id, ticket_id, sender_type, message, created_at) VALUES
    ('aa0e8400-e29b-41d4-a716-446655440000', '990e8400-e29b-41d4-a716-446655440000', 'customer', 'My laptop arrived but it won''t turn on. I tried charging it but nothing happens.', '2024-02-20 10:00:00'),
    ('aa0e8400-e29b-41d4-a716-446655440001', '990e8400-e29b-41d4-a716-446655440000', 'agent', 'I''m sorry to hear about the issue. Let me help you troubleshoot. Can you check if the power adapter LED is on?', '2024-02-20 10:30:00'),
    ('aa0e8400-e29b-41d4-a716-446655440002', '990e8400-e29b-41d4-a716-446655440001', 'customer', 'When will my order be delivered? I placed it 3 days ago.', '2024-02-18 14:30:00'),
    ('aa0e8400-e29b-41d4-a716-446655440003', '990e8400-e29b-41d4-a716-446655440001', 'agent', 'Your order is currently being processed and will be shipped within 24 hours. Expected delivery is 2-3 business days.', '2024-02-18 15:00:00'),
    ('aa0e8400-e29b-41d4-a716-446655440004', '990e8400-e29b-41d4-a716-446655440002', 'customer', 'I want to return my monitor. It has dead pixels.', '2024-02-22 09:15:00'),
    ('aa0e8400-e29b-41d4-a716-446655440005', '990e8400-e29b-41d4-a716-446655440003', 'customer', 'Do you have the Laptop Pro 15 in stock?', '2024-02-15 11:20:00'),
    ('aa0e8400-e29b-41d4-a716-446655440006', '990e8400-e29b-41d4-a716-446655440003', 'agent', 'Yes, we have 50 units in stock. Would you like to place an order?', '2024-02-15 11:45:00')
ON CONFLICT DO NOTHING;

-- Create a view for order summary
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.id as order_id,
    o.order_date,
    o.total_amount,
    o.status as order_status,
    c.email as customer_email,
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(oi.id) as item_count
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_date, o.total_amount, o.status, c.email, c.first_name, c.last_name;

-- Create a view for ticket statistics
CREATE OR REPLACE VIEW ticket_stats AS
SELECT 
    status,
    priority,
    COUNT(*) as ticket_count,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, CURRENT_TIMESTAMP) - created_at))/3600) as avg_hours_to_resolve
FROM support_tickets
GROUP BY status, priority;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;

