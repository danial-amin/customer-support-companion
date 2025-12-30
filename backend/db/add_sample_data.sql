-- Add More Sample Data to Customer Support Database
-- This script adds additional sample data to the existing database
-- Run this after the initial database setup

-- Add more customers
INSERT INTO customers (email, first_name, last_name, phone, status) VALUES
    ('sarah.connor@example.com', 'Sarah', 'Connor', '+1-555-0201', 'active'),
    ('michael.scott@example.com', 'Michael', 'Scott', '+1-555-0202', 'active'),
    ('pam.beesly@example.com', 'Pam', 'Beesly', '+1-555-0203', 'active'),
    ('dwight.schrute@example.com', 'Dwight', 'Schrute', '+1-555-0204', 'active'),
    ('jim.halpert@example.com', 'Jim', 'Halpert', '+1-555-0205', 'active'),
    ('angela.martin@example.com', 'Angela', 'Martin', '+1-555-0206', 'active'),
    ('kevin.malone@example.com', 'Kevin', 'Malone', '+1-555-0207', 'active'),
    ('oscar.martinez@example.com', 'Oscar', 'Martinez', '+1-555-0208', 'active'),
    ('stanley.hudson@example.com', 'Stanley', 'Hudson', '+1-555-0209', 'inactive'),
    ('phyllis.vance@example.com', 'Phyllis', 'Vance', '+1-555-0210', 'active')
ON CONFLICT (email) DO NOTHING;

-- Add more products
INSERT INTO products (name, description, price, stock_quantity, category) VALUES
    ('Gaming Mouse', 'RGB gaming mouse with 12,000 DPI', 79.99, 100, 'Gaming'),
    ('Webcam HD', '1080p HD webcam with microphone', 59.99, 150, 'Accessories'),
    ('Headphones Pro', 'Wireless noise-cancelling headphones', 199.99, 80, 'Audio'),
    ('Tablet 10"', '10-inch Android tablet with stylus', 299.99, 60, 'Electronics'),
    ('Smart Watch', 'Fitness tracking smartwatch', 249.99, 120, 'Wearables'),
    ('Power Bank 20K', '20,000mAh portable charger', 39.99, 200, 'Accessories'),
    ('SSD 1TB', '1TB NVMe SSD for laptops', 89.99, 90, 'Storage'),
    ('RAM 16GB', '16GB DDR4 laptop memory', 69.99, 110, 'Components'),
    ('External HDD 2TB', '2TB portable external hard drive', 79.99, 70, 'Storage'),
    ('USB Hub', '7-port USB 3.0 hub', 24.99, 300, 'Accessories')
ON CONFLICT DO NOTHING;

-- Get customer IDs for orders (using emails to find IDs)
-- Add more orders
INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address)
SELECT 
    c.id,
    order_date,
    total_amount,
    status,
    shipping_address
FROM (VALUES
    ('sarah.connor@example.com', '2024-03-01 10:00:00', 199.99, 'delivered', '100 Tech Blvd, San Francisco, CA 94102'),
    ('michael.scott@example.com', '2024-03-05 14:30:00', 79.99, 'shipped', '200 Paper St, Scranton, PA 18503'),
    ('pam.beesly@example.com', '2024-03-10 09:15:00', 59.99, 'processing', '300 Art Ave, Scranton, PA 18503'),
    ('dwight.schrute@example.com', '2024-03-12 16:45:00', 299.99, 'pending', '400 Beet Farm Rd, Scranton, PA 18503'),
    ('jim.halpert@example.com', '2024-03-15 11:20:00', 249.99, 'delivered', '500 Prank St, Scranton, PA 18503'),
    ('angela.martin@example.com', '2024-03-18 13:00:00', 39.99, 'shipped', '600 Cat Ln, Scranton, PA 18503'),
    ('kevin.malone@example.com', '2024-03-20 15:30:00', 89.99, 'processing', '700 Chili Ave, Scranton, PA 18503'),
    ('oscar.martinez@example.com', '2024-03-22 10:45:00', 69.99, 'delivered', '800 Finance Dr, Scranton, PA 18503'),
    ('sarah.connor@example.com', '2024-03-25 12:00:00', 79.99, 'shipped', '100 Tech Blvd, San Francisco, CA 94102'),
    ('michael.scott@example.com', '2024-03-28 14:15:00', 24.99, 'pending', '200 Paper St, Scranton, PA 18503')
) AS new_orders(email, order_date, total_amount, status, shipping_address)
JOIN customers c ON c.email = new_orders.email
ON CONFLICT DO NOTHING;

-- Add order items for the new orders
-- This is a bit complex, so we'll do it step by step
-- First, let's add items for orders placed by sarah.connor@example.com
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'sarah.connor@example.com' 
  AND o.order_date = '2024-03-01 10:00:00'
  AND p.name = 'Headphones Pro'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'michael.scott@example.com' 
  AND o.order_date = '2024-03-05 14:30:00'
  AND p.name = 'Gaming Mouse'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'pam.beesly@example.com' 
  AND o.order_date = '2024-03-10 09:15:00'
  AND p.name = 'Webcam HD'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'dwight.schrute@example.com' 
  AND o.order_date = '2024-03-12 16:45:00'
  AND p.name = 'Tablet 10"'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'jim.halpert@example.com' 
  AND o.order_date = '2024-03-15 11:20:00'
  AND p.name = 'Smart Watch'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'angela.martin@example.com' 
  AND o.order_date = '2024-03-18 13:00:00'
  AND p.name = 'Power Bank 20K'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'kevin.malone@example.com' 
  AND o.order_date = '2024-03-20 15:30:00'
  AND p.name = 'SSD 1TB'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'oscar.martinez@example.com' 
  AND o.order_date = '2024-03-22 10:45:00'
  AND p.name = 'RAM 16GB'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'sarah.connor@example.com' 
  AND o.order_date = '2024-03-25 12:00:00'
  AND p.name = 'External HDD 2TB'
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE c.email = 'michael.scott@example.com' 
  AND o.order_date = '2024-03-28 14:15:00'
  AND p.name = 'USB Hub'
ON CONFLICT DO NOTHING;

-- Add more support tickets
INSERT INTO support_tickets (customer_id, order_id, subject, description, status, priority, assigned_to, created_at)
SELECT 
    c.id,
    o.id,
    subject,
    description,
    status,
    priority,
    assigned_to,
    created_at
FROM (VALUES
    ('sarah.connor@example.com', '2024-03-01 10:00:00', 'Headphones not working', 'The headphones I received are not connecting to my device.', 'open', 'high', 'support_agent_1', '2024-03-05 10:00:00'),
    ('michael.scott@example.com', '2024-03-05 14:30:00', 'Gaming mouse button stuck', 'The left click button on my gaming mouse is stuck.', 'in_progress', 'medium', 'support_agent_2', '2024-03-08 14:30:00'),
    ('pam.beesly@example.com', '2024-03-10 09:15:00', 'Webcam quality issue', 'The webcam video quality is very poor.', 'open', 'medium', NULL, '2024-03-12 09:15:00'),
    ('dwight.schrute@example.com', '2024-03-12 16:45:00', 'Tablet screen cracked', 'My tablet arrived with a cracked screen.', 'open', 'urgent', 'support_agent_1', '2024-03-13 16:45:00'),
    ('jim.halpert@example.com', NULL, 'Smart watch battery life', 'How long does the battery last on the smart watch?', 'resolved', 'low', 'support_agent_2', '2024-03-16 11:20:00')
) AS new_tickets(email, order_date, subject, description, status, priority, assigned_to, created_at)
JOIN customers c ON c.email = new_tickets.email
LEFT JOIN orders o ON o.customer_id = c.id AND o.order_date::date = new_tickets.order_date::date
ON CONFLICT DO NOTHING;

-- Add ticket messages
INSERT INTO ticket_messages (ticket_id, sender_type, message, created_at)
SELECT 
    t.id,
    sender_type,
    message,
    created_at
FROM (VALUES
    ('sarah.connor@example.com', '2024-03-05 10:00:00', 'customer', 'The headphones I received are not connecting to my device.', '2024-03-05 10:00:00'),
    ('sarah.connor@example.com', '2024-03-05 10:00:00', 'agent', 'I apologize for the inconvenience. Let me help you troubleshoot the connection issue. Are you using Bluetooth or wired connection?', '2024-03-05 10:30:00'),
    ('michael.scott@example.com', '2024-03-08 14:30:00', 'customer', 'The left click button on my gaming mouse is stuck.', '2024-03-08 14:30:00'),
    ('michael.scott@example.com', '2024-03-08 14:30:00', 'agent', 'I''m sorry to hear about the issue. We can arrange a replacement. Please confirm your shipping address.', '2024-03-08 15:00:00'),
    ('pam.beesly@example.com', '2024-03-12 09:15:00', 'customer', 'The webcam video quality is very poor.', '2024-03-12 09:15:00'),
    ('dwight.schrute@example.com', '2024-03-13 16:45:00', 'customer', 'My tablet arrived with a cracked screen.', '2024-03-13 16:45:00'),
    ('dwight.schrute@example.com', '2024-03-13 16:45:00', 'agent', 'I''m very sorry about the damage. We will send a replacement immediately and arrange for return of the damaged unit.', '2024-03-13 17:00:00'),
    ('jim.halpert@example.com', NULL, 'customer', 'How long does the battery last on the smart watch?', '2024-03-16 11:20:00'),
    ('jim.halpert@example.com', NULL, 'agent', 'The smart watch battery lasts up to 7 days with normal use, or up to 2 days with heavy usage including GPS tracking.', '2024-03-16 11:45:00')
) AS new_messages(email, order_date, sender_type, message, created_at)
JOIN customers c ON c.email = new_messages.email
LEFT JOIN orders o ON o.customer_id = c.id AND (new_messages.order_date IS NULL OR o.order_date::date = new_messages.order_date::date)
LEFT JOIN support_tickets t ON t.customer_id = c.id AND (o.id IS NULL OR t.order_id = o.id)
WHERE t.id IS NOT NULL
ON CONFLICT DO NOTHING;

-- Display summary of added data
SELECT 'Customers added' as summary, COUNT(*) as count FROM customers;
SELECT 'Products added' as summary, COUNT(*) as count FROM products;
SELECT 'Orders added' as summary, COUNT(*) as count FROM orders;
SELECT 'Order items added' as summary, COUNT(*) as count FROM order_items;
SELECT 'Support tickets added' as summary, COUNT(*) as count FROM support_tickets;
SELECT 'Ticket messages added' as summary, COUNT(*) as count FROM ticket_messages;

