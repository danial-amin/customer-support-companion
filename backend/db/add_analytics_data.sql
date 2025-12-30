-- Comprehensive Analytics Data for Customer Support System
-- This script adds detailed data across multiple months for analysis and queries
-- Run this after initial setup and add_sample_data.sql

-- Add more customers (20 additional customers)
INSERT INTO customers (email, first_name, last_name, phone, status, created_at) VALUES
    ('emma.watson@example.com', 'Emma', 'Watson', '+1-555-0301', 'active', '2023-11-15 10:00:00'),
    ('chris.evans@example.com', 'Chris', 'Evans', '+1-555-0302', 'active', '2023-11-20 14:30:00'),
    ('scarlett.johansson@example.com', 'Scarlett', 'Johansson', '+1-555-0303', 'active', '2023-12-01 09:15:00'),
    ('robert.downey@example.com', 'Robert', 'Downey', '+1-555-0304', 'active', '2023-12-05 16:45:00'),
    ('mark.ruffalo@example.com', 'Mark', 'Ruffalo', '+1-555-0305', 'active', '2023-12-10 11:20:00'),
    ('chris.hemsworth@example.com', 'Chris', 'Hemsworth', '+1-555-0306', 'active', '2023-12-15 13:00:00'),
    ('tom.holland@example.com', 'Tom', 'Holland', '+1-555-0307', 'active', '2023-12-20 15:30:00'),
    ('zendaya@example.com', 'Zendaya', 'Coleman', '+1-555-0308', 'active', '2024-01-02 10:00:00'),
    ('timothee.chalamet@example.com', 'Timothée', 'Chalamet', '+1-555-0309', 'active', '2024-01-05 14:00:00'),
    ('florence.pugh@example.com', 'Florence', 'Pugh', '+1-555-0310', 'active', '2024-01-10 09:30:00'),
    ('paul.rudd@example.com', 'Paul', 'Rudd', '+1-555-0311', 'active', '2024-01-15 12:00:00'),
    ('benedict.cumberbatch@example.com', 'Benedict', 'Cumberbatch', '+1-555-0312', 'active', '2024-01-20 16:00:00'),
    ('elizabeth.olsen@example.com', 'Elizabeth', 'Olsen', '+1-555-0313', 'active', '2024-02-01 10:30:00'),
    ('jeremy.renner@example.com', 'Jeremy', 'Renner', '+1-555-0314', 'active', '2024-02-05 14:15:00'),
    ('samuel.jackson@example.com', 'Samuel', 'Jackson', '+1-555-0315', 'active', '2024-02-10 11:45:00'),
    ('don.cheadle@example.com', 'Don', 'Cheadle', '+1-555-0316', 'active', '2024-02-15 13:30:00'),
    ('anthony.mackie@example.com', 'Anthony', 'Mackie', '+1-555-0317', 'active', '2024-02-20 15:00:00'),
    ('sebastian.stan@example.com', 'Sebastian', 'Stan', '+1-555-0318', 'active', '2024-03-01 09:00:00'),
    ('paul.bettany@example.com', 'Paul', 'Bettany', '+1-555-0319', 'active', '2024-03-05 12:30:00'),
    ('karen.gillan@example.com', 'Karen', 'Gillan', '+1-555-0320', 'active', '2024-03-10 14:00:00')
ON CONFLICT (email) DO NOTHING;

-- Add more products (15 additional products)
INSERT INTO products (name, description, price, stock_quantity, category, created_at) VALUES
    ('Gaming Chair Pro', 'Ergonomic gaming chair with RGB lighting', 299.99, 45, 'Furniture', '2023-11-01'),
    ('Mechanical Keyboard RGB', 'Full RGB mechanical keyboard with Cherry MX switches', 149.99, 120, 'Gaming', '2023-11-01'),
    ('4K Webcam Pro', '4K UHD webcam with AI noise cancellation', 199.99, 80, 'Accessories', '2023-11-01'),
    ('Noise Cancelling Earbuds', 'True wireless earbuds with active noise cancellation', 179.99, 200, 'Audio', '2023-11-01'),
    ('Portable Monitor 15"', '15-inch portable USB-C monitor', 249.99, 60, 'Electronics', '2023-11-01'),
    ('Docking Station USB-C', 'USB-C docking station with dual 4K support', 129.99, 90, 'Accessories', '2023-11-01'),
    ('External SSD 1TB', '1TB portable SSD with USB-C', 99.99, 150, 'Storage', '2023-11-01'),
    ('Wireless Charger Stand', 'Qi wireless charging stand for phone and watch', 49.99, 250, 'Accessories', '2023-11-01'),
    ('Desk Lamp LED', 'LED desk lamp with adjustable brightness and color temperature', 79.99, 180, 'Furniture', '2023-11-01'),
    ('Monitor Stand Dual', 'Dual monitor stand with gas spring arms', 159.99, 70, 'Furniture', '2023-11-01'),
    ('USB-C Hub 8-in-1', '8-in-1 USB-C hub with HDMI, USB, SD card reader', 69.99, 200, 'Accessories', '2023-11-01'),
    ('Bluetooth Speaker', 'Portable Bluetooth speaker with 360° sound', 89.99, 160, 'Audio', '2023-11-01'),
    ('Laptop Stand Aluminum', 'Aluminum laptop stand with ventilation', 39.99, 300, 'Furniture', '2023-11-01'),
    ('Cable Management Kit', 'Cable management kit with clips and sleeves', 24.99, 400, 'Accessories', '2023-11-01'),
    ('Desk Mat Extended', 'Extended desk mat with wrist support', 34.99, 220, 'Accessories', '2023-11-01')
ON CONFLICT DO NOTHING;

-- Add comprehensive orders across multiple months (50 orders from November 2023 to March 2024)
-- November 2023 orders
INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address, created_at, updated_at)
SELECT 
    c.id,
    order_date,
    total_amount,
    status,
    shipping_address,
    order_date,
    CASE 
        WHEN status IN ('delivered', 'cancelled') THEN order_date + INTERVAL '3 days'
        WHEN status = 'shipped' THEN order_date + INTERVAL '2 days'
        ELSE order_date
    END
FROM (VALUES
    -- November 2023
    ('emma.watson@example.com', '2023-11-18 10:30:00', 299.99, 'delivered', '100 Hollywood Blvd, Los Angeles, CA 90028', '2023-11-18 10:30:00'),
    ('chris.evans@example.com', '2023-11-22 14:15:00', 449.98, 'delivered', '200 Boston St, Boston, MA 02101', '2023-11-22 14:15:00'),
    ('scarlett.johansson@example.com', '2023-11-25 09:45:00', 179.99, 'delivered', '300 Manhattan Ave, New York, NY 10001', '2023-11-25 09:45:00'),
    ('robert.downey@example.com', '2023-11-28 16:20:00', 599.98, 'delivered', '400 Malibu Dr, Malibu, CA 90265', '2023-11-28 16:20:00'),
    ('mark.ruffalo@example.com', '2023-11-30 11:00:00', 249.99, 'delivered', '500 Green St, Madison, WI 53703', '2023-11-30 11:00:00'),
    
    -- December 2023
    ('chris.hemsworth@example.com', '2023-12-03 13:30:00', 129.99, 'delivered', '600 Sydney Rd, Sydney, NSW 2000', '2023-12-03 13:30:00'),
    ('tom.holland@example.com', '2023-12-05 15:45:00', 349.98, 'delivered', '700 London St, London, UK SW1A 1AA', '2023-12-05 15:45:00'),
    ('zendaya@example.com', '2023-12-08 10:15:00', 199.99, 'delivered', '800 Oakland Ave, Oakland, CA 94601', '2023-12-08 10:15:00'),
    ('timothee.chalamet@example.com', '2023-12-10 14:00:00', 89.99, 'delivered', '900 Brooklyn Heights, Brooklyn, NY 11201', '2023-12-10 14:00:00'),
    ('florence.pugh@example.com', '2023-12-12 09:30:00', 259.98, 'delivered', '1000 Oxford St, Oxford, UK OX1 1DP', '2023-12-12 09:30:00'),
    ('paul.rudd@example.com', '2023-12-15 12:20:00', 179.99, 'delivered', '1100 Kansas Ave, Kansas City, MO 64108', '2023-12-15 12:20:00'),
    ('benedict.cumberbatch@example.com', '2023-12-18 16:00:00', 399.98, 'delivered', '1200 Baker St, London, UK NW1 6XE', '2023-12-18 16:00:00'),
    ('elizabeth.olsen@example.com', '2023-12-20 10:45:00', 149.99, 'delivered', '1300 Westchester Ave, Westchester, NY 10595', '2023-12-20 10:45:00'),
    ('jeremy.renner@example.com', '2023-12-22 14:30:00', 229.98, 'delivered', '1400 Modesto Blvd, Modesto, CA 95354', '2023-12-22 14:30:00'),
    ('samuel.jackson@example.com', '2023-12-24 11:00:00', 99.99, 'delivered', '1500 Washington DC, Washington, DC 20001', '2023-12-24 11:00:00'),
    ('don.cheadle@example.com', '2023-12-26 15:15:00', 319.98, 'delivered', '1600 Denver St, Denver, CO 80202', '2023-12-26 15:15:00'),
    ('anthony.mackie@example.com', '2023-12-28 09:00:00', 189.99, 'delivered', '1700 Atlanta Ave, Atlanta, GA 30309', '2023-12-28 09:00:00'),
    ('sebastian.stan@example.com', '2023-12-30 13:45:00', 279.98, 'delivered', '1800 Bucharest St, Bucharest, Romania', '2023-12-30 13:45:00'),
    
    -- January 2024
    ('paul.bettany@example.com', '2024-01-03 10:20:00', 159.99, 'delivered', '1900 Cambridge Rd, Cambridge, UK CB2 1TN', '2024-01-03 10:20:00'),
    ('karen.gillan@example.com', '2024-01-05 14:00:00', 369.98, 'delivered', '2000 Inverness Way, Inverness, Scotland', '2024-01-05 14:00:00'),
    ('emma.watson@example.com', '2024-01-08 11:30:00', 249.99, 'delivered', '100 Hollywood Blvd, Los Angeles, CA 90028', '2024-01-08 11:30:00'),
    ('chris.evans@example.com', '2024-01-10 15:00:00', 199.99, 'delivered', '200 Boston St, Boston, MA 02101', '2024-01-10 15:00:00'),
    ('scarlett.johansson@example.com', '2024-01-12 09:15:00', 449.97, 'delivered', '300 Manhattan Ave, New York, NY 10001', '2024-01-12 09:15:00'),
    ('robert.downey@example.com', '2024-01-15 13:45:00', 129.99, 'delivered', '400 Malibu Dr, Malibu, CA 90265', '2024-01-15 13:45:00'),
    ('mark.ruffalo@example.com', '2024-01-18 10:00:00', 299.98, 'delivered', '500 Green St, Madison, WI 53703', '2024-01-18 10:00:00'),
    ('chris.hemsworth@example.com', '2024-01-20 14:30:00', 179.99, 'delivered', '600 Sydney Rd, Sydney, NSW 2000', '2024-01-20 14:30:00'),
    ('tom.holland@example.com', '2024-01-22 16:00:00', 349.98, 'delivered', '700 London St, London, UK SW1A 1AA', '2024-01-22 16:00:00'),
    ('zendaya@example.com', '2024-01-25 11:15:00', 89.99, 'delivered', '800 Oakland Ave, Oakland, CA 94601', '2024-01-25 11:15:00'),
    ('timothee.chalamet@example.com', '2024-01-28 09:30:00', 259.98, 'delivered', '900 Brooklyn Heights, Brooklyn, NY 11201', '2024-01-28 09:30:00'),
    
    -- February 2024
    ('florence.pugh@example.com', '2024-02-01 12:00:00', 399.98, 'shipped', '1000 Oxford St, Oxford, UK OX1 1DP', '2024-02-01 12:00:00'),
    ('paul.rudd@example.com', '2024-02-03 14:45:00', 149.99, 'shipped', '1100 Kansas Ave, Kansas City, MO 64108', '2024-02-03 14:45:00'),
    ('benedict.cumberbatch@example.com', '2024-02-05 10:20:00', 229.98, 'shipped', '1200 Baker St, London, UK NW1 6XE', '2024-02-05 10:20:00'),
    ('elizabeth.olsen@example.com', '2024-02-08 15:00:00', 179.99, 'shipped', '1300 Westchester Ave, Westchester, NY 10595', '2024-02-08 15:00:00'),
    ('jeremy.renner@example.com', '2024-02-10 11:30:00', 319.98, 'processing', '1400 Modesto Blvd, Modesto, CA 95354', '2024-02-10 11:30:00'),
    ('samuel.jackson@example.com', '2024-02-12 13:15:00', 99.99, 'processing', '1500 Washington DC, Washington, DC 20001', '2024-02-12 13:15:00'),
    ('don.cheadle@example.com', '2024-02-15 09:45:00', 249.99, 'processing', '1600 Denver St, Denver, CO 80202', '2024-02-15 09:45:00'),
    ('anthony.mackie@example.com', '2024-02-18 14:00:00', 189.98, 'processing', '1700 Atlanta Ave, Atlanta, GA 30309', '2024-02-18 14:00:00'),
    ('sebastian.stan@example.com', '2024-02-20 16:30:00', 279.99, 'pending', '1800 Bucharest St, Bucharest, Romania', '2024-02-20 16:30:00'),
    ('paul.bettany@example.com', '2024-02-22 10:00:00', 159.98, 'pending', '1900 Cambridge Rd, Cambridge, UK CB2 1TN', '2024-02-22 10:00:00'),
    ('karen.gillan@example.com', '2024-02-25 12:45:00', 369.99, 'pending', '2000 Inverness Way, Inverness, Scotland', '2024-02-25 12:45:00'),
    ('emma.watson@example.com', '2024-02-28 15:20:00', 199.98, 'pending', '100 Hollywood Blvd, Los Angeles, CA 90028', '2024-02-28 15:20:00'),
    
    -- March 2024
    ('chris.evans@example.com', '2024-03-02 11:00:00', 449.99, 'processing', '200 Boston St, Boston, MA 02101', '2024-03-02 11:00:00'),
    ('scarlett.johansson@example.com', '2024-03-05 14:30:00', 179.98, 'processing', '300 Manhattan Ave, New York, NY 10001', '2024-03-05 14:30:00'),
    ('robert.downey@example.com', '2024-03-08 09:15:00', 599.99, 'pending', '400 Malibu Dr, Malibu, CA 90265', '2024-03-08 09:15:00'),
    ('mark.ruffalo@example.com', '2024-03-10 13:00:00', 249.98, 'pending', '500 Green St, Madison, WI 53703', '2024-03-10 13:00:00'),
    ('chris.hemsworth@example.com', '2024-03-12 16:45:00', 129.98, 'pending', '600 Sydney Rd, Sydney, NSW 2000', '2024-03-12 16:45:00'),
    ('tom.holland@example.com', '2024-03-15 10:30:00', 349.99, 'pending', '700 London St, London, UK SW1A 1AA', '2024-03-15 10:30:00'),
    ('zendaya@example.com', '2024-03-18 14:00:00', 199.98, 'pending', '800 Oakland Ave, Oakland, CA 94601', '2024-03-18 14:00:00'),
    ('timothee.chalamet@example.com', '2024-03-20 11:15:00', 89.98, 'pending', '900 Brooklyn Heights, Brooklyn, NY 11201', '2024-03-20 11:15:00')
) AS new_orders(email, order_date, total_amount, status, shipping_address, created_at, updated_at)
JOIN customers c ON c.email = new_orders.email
ON CONFLICT DO NOTHING;

-- Add detailed order items for all the new orders
-- This creates realistic order items with multiple products per order
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    quantity,
    p.price,
    p.price * quantity
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN LATERAL (
    SELECT id, price, name FROM products WHERE name = product_name
) p
CROSS JOIN LATERAL (
    SELECT quantity FROM (VALUES (qty)) AS q(quantity)
) q
WHERE (c.email, o.order_date::date, product_name, qty) IN (
    -- November 2023
    ('emma.watson@example.com', '2023-11-18', 'Gaming Chair Pro', 1),
    ('chris.evans@example.com', '2023-11-22', 'Gaming Chair Pro', 1),
    ('chris.evans@example.com', '2023-11-22', 'Mechanical Keyboard RGB', 1),
    ('scarlett.johansson@example.com', '2023-11-25', 'Noise Cancelling Earbuds', 1),
    ('robert.downey@example.com', '2023-11-28', 'Gaming Chair Pro', 1),
    ('robert.downey@example.com', '2023-11-28', '4K Webcam Pro', 1),
    ('mark.ruffalo@example.com', '2023-11-30', 'Portable Monitor 15"', 1),
    
    -- December 2023
    ('chris.hemsworth@example.com', '2023-12-03', 'Docking Station USB-C', 1),
    ('tom.holland@example.com', '2023-12-05', 'Gaming Chair Pro', 1),
    ('tom.holland@example.com', '2023-12-05', 'Mechanical Keyboard RGB', 1),
    ('zendaya@example.com', '2023-12-08', '4K Webcam Pro', 1),
    ('timothee.chalamet@example.com', '2023-12-10', 'Bluetooth Speaker', 1),
    ('florence.pugh@example.com', '2023-12-12', 'Portable Monitor 15"', 1),
    ('florence.pugh@example.com', '2023-12-12', 'Docking Station USB-C', 1),
    ('paul.rudd@example.com', '2023-12-15', 'Noise Cancelling Earbuds', 1),
    ('benedict.cumberbatch@example.com', '2023-12-18', 'Gaming Chair Pro', 1),
    ('benedict.cumberbatch@example.com', '2023-12-18', 'Mechanical Keyboard RGB', 1),
    ('elizabeth.olsen@example.com', '2023-12-20', 'Mechanical Keyboard RGB', 1),
    ('jeremy.renner@example.com', '2023-12-22', '4K Webcam Pro', 1),
    ('jeremy.renner@example.com', '2023-12-22', 'Bluetooth Speaker', 1),
    ('samuel.jackson@example.com', '2023-12-24', 'External SSD 1TB', 1),
    ('don.cheadle@example.com', '2023-12-26', 'Gaming Chair Pro', 1),
    ('don.cheadle@example.com', '2023-12-26', 'Monitor Stand Dual', 1),
    ('anthony.mackie@example.com', '2023-12-28', 'Noise Cancelling Earbuds', 1),
    ('sebastian.stan@example.com', '2023-12-30', 'Portable Monitor 15"', 1),
    ('sebastian.stan@example.com', '2023-12-30', 'Docking Station USB-C', 1),
    
    -- January 2024
    ('paul.bettany@example.com', '2024-01-03', 'Monitor Stand Dual', 1),
    ('karen.gillan@example.com', '2024-01-05', 'Gaming Chair Pro', 1),
    ('karen.gillan@example.com', '2024-01-05', 'Mechanical Keyboard RGB', 1),
    ('karen.gillan@example.com', '2024-01-05', '4K Webcam Pro', 1),
    ('emma.watson@example.com', '2024-01-08', 'Portable Monitor 15"', 1),
    ('chris.evans@example.com', '2024-01-10', '4K Webcam Pro', 1),
    ('scarlett.johansson@example.com', '2024-01-12', 'Gaming Chair Pro', 1),
    ('scarlett.johansson@example.com', '2024-01-12', 'Mechanical Keyboard RGB', 1),
    ('scarlett.johansson@example.com', '2024-01-12', 'Noise Cancelling Earbuds', 1),
    ('robert.downey@example.com', '2024-01-15', 'Docking Station USB-C', 1),
    ('mark.ruffalo@example.com', '2024-01-18', 'Gaming Chair Pro', 1),
    ('mark.ruffalo@example.com', '2024-01-18', 'Bluetooth Speaker', 1),
    ('chris.hemsworth@example.com', '2024-01-20', 'Noise Cancelling Earbuds', 1),
    ('tom.holland@example.com', '2024-01-22', 'Gaming Chair Pro', 1),
    ('tom.holland@example.com', '2024-01-22', 'Mechanical Keyboard RGB', 1),
    ('zendaya@example.com', '2024-01-25', 'Bluetooth Speaker', 1),
    ('timothee.chalamet@example.com', '2024-01-28', 'Portable Monitor 15"', 1),
    ('timothee.chalamet@example.com', '2024-01-28', 'Docking Station USB-C', 1),
    
    -- February 2024
    ('florence.pugh@example.com', '2024-02-01', 'Gaming Chair Pro', 1),
    ('florence.pugh@example.com', '2024-02-01', 'Mechanical Keyboard RGB', 1),
    ('paul.rudd@example.com', '2024-02-03', 'Mechanical Keyboard RGB', 1),
    ('benedict.cumberbatch@example.com', '2024-02-05', '4K Webcam Pro', 1),
    ('benedict.cumberbatch@example.com', '2024-02-05', 'Bluetooth Speaker', 1),
    ('elizabeth.olsen@example.com', '2024-02-08', 'Noise Cancelling Earbuds', 1),
    ('jeremy.renner@example.com', '2024-02-10', 'Gaming Chair Pro', 1),
    ('jeremy.renner@example.com', '2024-02-10', 'Monitor Stand Dual', 1),
    ('samuel.jackson@example.com', '2024-02-12', 'External SSD 1TB', 1),
    ('don.cheadle@example.com', '2024-02-15', 'Portable Monitor 15"', 1),
    ('anthony.mackie@example.com', '2024-02-18', 'Noise Cancelling Earbuds', 1),
    ('anthony.mackie@example.com', '2024-02-18', 'Bluetooth Speaker', 1),
    ('sebastian.stan@example.com', '2024-02-20', 'Gaming Chair Pro', 1),
    ('sebastian.stan@example.com', '2024-02-20', '4K Webcam Pro', 1),
    ('paul.bettany@example.com', '2024-02-22', 'Monitor Stand Dual', 1),
    ('paul.bettany@example.com', '2024-02-22', 'Docking Station USB-C', 1),
    ('karen.gillan@example.com', '2024-02-25', 'Gaming Chair Pro', 1),
    ('karen.gillan@example.com', '2024-02-25', 'Mechanical Keyboard RGB', 1),
    ('karen.gillan@example.com', '2024-02-25', '4K Webcam Pro', 1),
    ('emma.watson@example.com', '2024-02-28', '4K Webcam Pro', 1),
    ('emma.watson@example.com', '2024-02-28', 'Bluetooth Speaker', 1),
    
    -- March 2024
    ('chris.evans@example.com', '2024-03-02', 'Gaming Chair Pro', 1),
    ('chris.evans@example.com', '2024-03-02', 'Mechanical Keyboard RGB', 1),
    ('chris.evans@example.com', '2024-03-02', '4K Webcam Pro', 1),
    ('scarlett.johansson@example.com', '2024-03-05', 'Noise Cancelling Earbuds', 1),
    ('scarlett.johansson@example.com', '2024-03-05', 'Bluetooth Speaker', 1),
    ('robert.downey@example.com', '2024-03-08', 'Gaming Chair Pro', 1),
    ('robert.downey@example.com', '2024-03-08', 'Mechanical Keyboard RGB', 1),
    ('robert.downey@example.com', '2024-03-08', '4K Webcam Pro', 1),
    ('robert.downey@example.com', '2024-03-08', 'Noise Cancelling Earbuds', 1),
    ('mark.ruffalo@example.com', '2024-03-10', 'Portable Monitor 15"', 1),
    ('mark.ruffalo@example.com', '2024-03-10', 'Docking Station USB-C', 1),
    ('chris.hemsworth@example.com', '2024-03-12', 'Docking Station USB-C', 1),
    ('chris.hemsworth@example.com', '2024-03-12', 'Bluetooth Speaker', 1),
    ('tom.holland@example.com', '2024-03-15', 'Gaming Chair Pro', 1),
    ('tom.holland@example.com', '2024-03-15', 'Mechanical Keyboard RGB', 1),
    ('zendaya@example.com', '2024-03-18', '4K Webcam Pro', 1),
    ('zendaya@example.com', '2024-03-18', 'Bluetooth Speaker', 1),
    ('timothee.chalamet@example.com', '2024-03-20', 'Bluetooth Speaker', 1),
    ('timothee.chalamet@example.com', '2024-03-20', 'External SSD 1TB', 1)
)
ON CONFLICT DO NOTHING;

-- Add more support tickets with detailed information
INSERT INTO support_tickets (customer_id, order_id, subject, description, status, priority, assigned_to, created_at, updated_at, resolved_at)
SELECT 
    c.id,
    o.id,
    subject,
    description,
    status,
    priority,
    assigned_to,
    created_at,
    updated_at,
    resolved_at
FROM (VALUES
    ('emma.watson@example.com', '2023-11-18', 'Gaming chair assembly issue', 'I received my gaming chair but the assembly instructions are unclear. Can someone help?', 'resolved', 'medium', 'support_agent_1', '2023-11-20 10:00:00', '2023-11-20 14:00:00', '2023-11-20 14:00:00'),
    ('chris.evans@example.com', '2023-11-22', 'Keyboard key not working', 'The "A" key on my mechanical keyboard is not responding properly.', 'resolved', 'high', 'support_agent_2', '2023-11-24 09:00:00', '2023-11-24 11:00:00', '2023-11-24 11:00:00'),
    ('scarlett.johansson@example.com', '2023-11-25', 'Earbuds connectivity', 'My earbuds keep disconnecting from my phone. This is very frustrating.', 'open', 'high', 'support_agent_1', '2023-11-27 14:00:00', '2023-11-27 14:00:00', NULL),
    ('robert.downey@example.com', '2023-11-28', 'Webcam quality poor', 'The 4K webcam video quality is not as good as advertised.', 'in_progress', 'medium', 'support_agent_2', '2023-11-30 10:00:00', '2023-12-01 09:00:00', NULL),
    ('mark.ruffalo@example.com', '2023-11-30', 'Monitor not turning on', 'My portable monitor arrived but it won''t turn on. I tried different cables.', 'resolved', 'urgent', 'support_agent_1', '2023-12-02 08:00:00', '2023-12-02 12:00:00', '2023-12-02 12:00:00'),
    ('chris.hemsworth@example.com', '2023-12-03', 'Docking station ports', 'The docking station USB ports are not working properly.', 'resolved', 'medium', 'support_agent_2', '2023-12-05 11:00:00', '2023-12-05 15:00:00', '2023-12-05 15:00:00'),
    ('tom.holland@example.com', '2023-12-05', 'RGB lighting issue', 'The RGB lighting on my gaming chair is flickering.', 'open', 'low', NULL, '2023-12-07 13:00:00', '2023-12-07 13:00:00', NULL),
    ('zendaya@example.com', '2023-12-08', 'Webcam microphone', 'The webcam microphone is picking up too much background noise.', 'in_progress', 'medium', 'support_agent_1', '2023-12-10 09:00:00', '2023-12-10 14:00:00', NULL),
    ('timothee.chalamet@example.com', '2023-12-10', 'Speaker volume', 'The Bluetooth speaker volume is too low even at maximum.', 'resolved', 'low', 'support_agent_2', '2023-12-12 10:00:00', '2023-12-12 11:00:00', '2023-12-12 11:00:00'),
    ('florence.pugh@example.com', '2023-12-12', 'Monitor resolution', 'The portable monitor resolution seems lower than expected.', 'open', 'medium', NULL, '2023-12-14 15:00:00', '2023-12-14 15:00:00', NULL),
    ('paul.rudd@example.com', '2023-12-15', 'Earbuds battery life', 'The earbuds battery doesn''t last as long as advertised.', 'resolved', 'low', 'support_agent_1', '2023-12-17 11:00:00', '2023-12-17 12:00:00', '2023-12-17 12:00:00'),
    ('benedict.cumberbatch@example.com', '2023-12-18', 'Gaming chair comfort', 'The gaming chair is not as comfortable as I expected.', 'open', 'low', NULL, '2023-12-20 09:00:00', '2023-12-20 09:00:00', NULL),
    ('elizabeth.olsen@example.com', '2023-12-20', 'Keyboard switches', 'I want to exchange my keyboard for one with different switches.', 'in_progress', 'medium', 'support_agent_2', '2023-12-22 14:00:00', '2023-12-23 10:00:00', NULL),
    ('jeremy.renner@example.com', '2023-12-22', 'Webcam software', 'The webcam software is not compatible with my operating system.', 'resolved', 'high', 'support_agent_1', '2023-12-24 10:00:00', '2023-12-24 16:00:00', '2023-12-24 16:00:00'),
    ('samuel.jackson@example.com', '2023-12-24', 'SSD speed', 'The external SSD transfer speed is slower than advertised.', 'open', 'medium', NULL, '2023-12-26 11:00:00', '2023-12-26 11:00:00', NULL),
    ('don.cheadle@example.com', '2023-12-26', 'Monitor stand adjustment', 'The monitor stand is difficult to adjust.', 'resolved', 'low', 'support_agent_2', '2023-12-28 09:00:00', '2023-12-28 10:00:00', '2023-12-28 10:00:00'),
    ('anthony.mackie@example.com', '2023-12-28', 'Earbuds fit', 'The earbuds don''t fit well in my ears.', 'open', 'low', NULL, '2023-12-30 13:00:00', '2023-12-30 13:00:00', NULL),
    ('sebastian.stan@example.com', '2023-12-30', 'Monitor compatibility', 'Will this monitor work with my MacBook?', 'resolved', 'low', 'support_agent_1', '2024-01-02 10:00:00', '2024-01-02 11:00:00', '2024-01-02 11:00:00'),
    ('paul.bettany@example.com', '2024-01-03', 'Docking station heat', 'The docking station gets very hot during use.', 'in_progress', 'medium', 'support_agent_2', '2024-01-05 14:00:00', '2024-01-06 09:00:00', NULL),
    ('karen.gillan@example.com', '2024-01-05', 'Gaming setup question', 'I want to know if these products work well together for gaming.', 'resolved', 'low', 'support_agent_1', '2024-01-07 11:00:00', '2024-01-07 12:00:00', '2024-01-07 12:00:00'),
    ('emma.watson@example.com', '2024-01-08', 'Monitor warranty', 'What is the warranty period for the portable monitor?', 'resolved', 'low', 'support_agent_2', '2024-01-10 09:00:00', '2024-01-10 10:00:00', '2024-01-10 10:00:00'),
    ('chris.evans@example.com', '2024-01-10', 'Webcam privacy', 'Does the webcam have a privacy shutter?', 'resolved', 'low', 'support_agent_1', '2024-01-12 14:00:00', '2024-01-12 15:00:00', '2024-01-12 15:00:00'),
    ('scarlett.johansson@example.com', '2024-01-12', 'Product bundle discount', 'Can I get a discount for buying multiple products?', 'open', 'low', NULL, '2024-01-14 10:00:00', '2024-01-14 10:00:00', NULL),
    ('robert.downey@example.com', '2024-01-15', 'Docking station ports', 'How many devices can I connect to the docking station?', 'resolved', 'low', 'support_agent_2', '2024-01-17 11:00:00', '2024-01-17 12:00:00', '2024-01-17 12:00:00'),
    ('mark.ruffalo@example.com', '2024-01-18', 'Gaming chair weight limit', 'What is the weight limit for the gaming chair?', 'resolved', 'low', 'support_agent_1', '2024-01-20 09:00:00', '2024-01-20 10:00:00', '2024-01-20 10:00:00'),
    ('chris.hemsworth@example.com', '2024-01-20', 'Earbuds water resistance', 'Are the earbuds water resistant?', 'resolved', 'low', 'support_agent_2', '2024-01-22 14:00:00', '2024-01-22 15:00:00', '2024-01-22 15:00:00'),
    ('tom.holland@example.com', '2024-01-22', 'Keyboard customization', 'Can I customize the RGB lighting on the keyboard?', 'resolved', 'low', 'support_agent_1', '2024-01-24 10:00:00', '2024-01-24 11:00:00', '2024-01-24 11:00:00'),
    ('zendaya@example.com', '2024-01-25', 'Speaker battery', 'How long does the speaker battery last?', 'resolved', 'low', 'support_agent_2', '2024-01-27 09:00:00', '2024-01-27 10:00:00', '2024-01-27 10:00:00'),
    ('timothee.chalamet@example.com', '2024-01-28', 'Monitor setup', 'I need help setting up dual monitors with the portable monitor.', 'in_progress', 'medium', 'support_agent_1', '2024-01-30 11:00:00', '2024-01-31 09:00:00', NULL),
    ('florence.pugh@example.com', '2024-02-01', 'Gaming chair delivery', 'When will my gaming chair be delivered?', 'open', 'medium', NULL, '2024-02-03 10:00:00', '2024-02-03 10:00:00', NULL),
    ('paul.rudd@example.com', '2024-02-03', 'Keyboard keycap replacement', 'I want to replace some keycaps on my keyboard.', 'open', 'low', NULL, '2024-02-05 14:00:00', '2024-02-05 14:00:00', NULL),
    ('benedict.cumberbatch@example.com', '2024-02-05', 'Webcam and speaker combo', 'Can I use the webcam and speaker together for video calls?', 'resolved', 'low', 'support_agent_2', '2024-02-07 09:00:00', '2024-02-07 10:00:00', '2024-02-07 10:00:00'),
    ('elizabeth.olsen@example.com', '2024-02-08', 'Earbuds case', 'The earbuds charging case is not charging properly.', 'in_progress', 'high', 'support_agent_1', '2024-02-10 11:00:00', '2024-02-11 09:00:00', NULL),
    ('jeremy.renner@example.com', '2024-02-10', 'Gaming setup complete', 'I''m having issues with my complete gaming setup.', 'open', 'high', NULL, '2024-02-12 15:00:00', '2024-02-12 15:00:00', NULL),
    ('samuel.jackson@example.com', '2024-02-12', 'SSD compatibility', 'Is the SSD compatible with PlayStation 5?', 'resolved', 'low', 'support_agent_2', '2024-02-14 10:00:00', '2024-02-14 11:00:00', '2024-02-14 11:00:00'),
    ('don.cheadle@example.com', '2024-02-15', 'Monitor color accuracy', 'The monitor colors seem off. How do I calibrate it?', 'open', 'medium', NULL, '2024-02-17 13:00:00', '2024-02-17 13:00:00', NULL),
    ('anthony.mackie@example.com', '2024-02-18', 'Earbuds and speaker', 'Can I connect both earbuds and speaker to the same device?', 'resolved', 'low', 'support_agent_1', '2024-02-20 09:00:00', '2024-02-20 10:00:00', '2024-02-20 10:00:00'),
    ('sebastian.stan@example.com', '2024-02-20', 'Gaming chair lumbar support', 'The lumbar support on my gaming chair is not adjustable enough.', 'open', 'medium', NULL, '2024-02-22 14:00:00', '2024-02-22 14:00:00', NULL),
    ('paul.bettany@example.com', '2024-02-22', 'Docking station and monitor', 'Can I connect the docking station to the portable monitor?', 'resolved', 'low', 'support_agent_2', '2024-02-24 10:00:00', '2024-02-24 11:00:00', '2024-02-24 11:00:00'),
    ('karen.gillan@example.com', '2024-02-25', 'Complete setup issue', 'Multiple products from my order are not working together.', 'in_progress', 'urgent', 'support_agent_1', '2024-02-27 08:00:00', '2024-02-28 09:00:00', NULL),
    ('emma.watson@example.com', '2024-02-28', 'Webcam and speaker', 'The webcam microphone and speaker are causing feedback.', 'open', 'medium', NULL, '2024-03-02 11:00:00', '2024-03-02 11:00:00', NULL),
    ('chris.evans@example.com', '2024-03-02', 'Gaming setup optimization', 'I need help optimizing my gaming setup for best performance.', 'open', 'medium', NULL, '2024-03-04 14:00:00', '2024-03-04 14:00:00', NULL),
    ('scarlett.johansson@example.com', '2024-03-05', 'Earbuds and speaker', 'Which is better for video calls - earbuds or speaker?', 'resolved', 'low', 'support_agent_2', '2024-03-07 10:00:00', '2024-03-07 11:00:00', '2024-03-07 11:00:00'),
    ('robert.downey@example.com', '2024-03-08', 'Complete gaming setup', 'I ordered a complete gaming setup but some items are missing.', 'in_progress', 'urgent', 'support_agent_1', '2024-03-10 09:00:00', '2024-03-11 08:00:00', NULL),
    ('mark.ruffalo@example.com', '2024-03-10', 'Monitor and docking', 'The monitor is not displaying when connected through the docking station.', 'open', 'high', NULL, '2024-03-12 13:00:00', '2024-03-12 13:00:00', NULL),
    ('chris.hemsworth@example.com', '2024-03-12', 'Docking station and speaker', 'Can I use the docking station and speaker simultaneously?', 'resolved', 'low', 'support_agent_2', '2024-03-14 10:00:00', '2024-03-14 11:00:00', '2024-03-14 11:00:00'),
    ('tom.holland@example.com', '2024-03-15', 'Gaming chair and keyboard', 'My gaming chair and keyboard RGB lighting are not syncing.', 'open', 'low', NULL, '2024-03-17 14:00:00', '2024-03-17 14:00:00', NULL),
    ('zendaya@example.com', '2024-03-18', 'Webcam quality', 'The webcam quality is poor in low light conditions.', 'open', 'medium', NULL, '2024-03-20 09:00:00', '2024-03-20 09:00:00', NULL),
    ('timothee.chalamet@example.com', '2024-03-20', 'SSD and speaker', 'Can I store music on the SSD and play it through the speaker?', 'resolved', 'low', 'support_agent_1', '2024-03-22 11:00:00', '2024-03-22 12:00:00', '2024-03-22 12:00:00')
) AS new_tickets(email, order_date, subject, description, status, priority, assigned_to, created_at, updated_at, resolved_at)
JOIN customers c ON c.email = new_tickets.email
LEFT JOIN orders o ON o.customer_id = c.id AND o.order_date::date = new_tickets.order_date::date
ON CONFLICT DO NOTHING;

-- Display summary
SELECT 'Analytics Data Added' as summary;
SELECT 'Total customers' as metric, COUNT(*) as count FROM customers;
SELECT 'Total products' as metric, COUNT(*) as count FROM products;
SELECT 'Total orders' as metric, COUNT(*) as count FROM orders;
SELECT 'Total order items' as metric, COUNT(*) as count FROM order_items;
SELECT 'Total support tickets' as metric, COUNT(*) as count FROM support_tickets;

-- Show orders by month
SELECT 
    TO_CHAR(order_date, 'YYYY-MM') as month,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM orders
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY month;

-- Show orders by status
SELECT 
    status,
    COUNT(*) as count,
    SUM(total_amount) as total_revenue
FROM orders
GROUP BY status
ORDER BY count DESC;

