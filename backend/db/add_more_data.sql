-- Add More Sample Data to Customer Support Database
-- This script adds significantly more sample data to expand the database

-- Add 25 more customers
INSERT INTO customers (email, first_name, last_name, phone, status) VALUES
    ('alice.johnson@example.com', 'Alice', 'Johnson', '+1-555-0301', 'active'),
    ('bob.smith@example.com', 'Bob', 'Smith', '+1-555-0302', 'active'),
    ('charlie.brown@example.com', 'Charlie', 'Brown', '+1-555-0303', 'active'),
    ('diana.prince@example.com', 'Diana', 'Prince', '+1-555-0304', 'active'),
    ('edward.norton@example.com', 'Edward', 'Norton', '+1-555-0305', 'active'),
    ('fiona.apple@example.com', 'Fiona', 'Apple', '+1-555-0306', 'active'),
    ('george.lucas@example.com', 'George', 'Lucas', '+1-555-0307', 'active'),
    ('hannah.montana@example.com', 'Hannah', 'Montana', '+1-555-0308', 'active'),
    ('isaac.newton@example.com', 'Isaac', 'Newton', '+1-555-0309', 'active'),
    ('julia.roberts@example.com', 'Julia', 'Roberts', '+1-555-0310', 'active'),
    ('kevin.hart@example.com', 'Kevin', 'Hart', '+1-555-0311', 'active'),
    ('lisa.simpson@example.com', 'Lisa', 'Simpson', '+1-555-0312', 'active'),
    ('mike.tyson@example.com', 'Mike', 'Tyson', '+1-555-0313', 'active'),
    ('nancy.drew@example.com', 'Nancy', 'Drew', '+1-555-0314', 'active'),
    ('oliver.twist@example.com', 'Oliver', 'Twist', '+1-555-0315', 'active'),
    ('patricia.highsmith@example.com', 'Patricia', 'Highsmith', '+1-555-0316', 'active'),
    ('quentin.tarantino@example.com', 'Quentin', 'Tarantino', '+1-555-0317', 'active'),
    ('rachel.green@example.com', 'Rachel', 'Green', '+1-555-0318', 'active'),
    ('steve.jobs@example.com', 'Steve', 'Jobs', '+1-555-0319', 'active'),
    ('tina.fey@example.com', 'Tina', 'Fey', '+1-555-0320', 'active'),
    ('ursula.leguin@example.com', 'Ursula', 'LeGuin', '+1-555-0321', 'active'),
    ('victor.hugo@example.com', 'Victor', 'Hugo', '+1-555-0322', 'active'),
    ('wendy.darling@example.com', 'Wendy', 'Darling', '+1-555-0323', 'active'),
    ('xavier.musk@example.com', 'Xavier', 'Musk', '+1-555-0324', 'inactive'),
    ('yara.shahidi@example.com', 'Yara', 'Shahidi', '+1-555-0325', 'active')
ON CONFLICT (email) DO NOTHING;

-- Add 20 more products
INSERT INTO products (name, description, price, stock_quantity, category) VALUES
    ('Mechanical Keyboard', 'RGB mechanical keyboard with Cherry MX switches', 129.99, 85, 'Gaming'),
    ('Monitor 27" 4K', '27-inch 4K UHD monitor with HDR', 349.99, 45, 'Displays'),
    ('Graphics Card RTX 4060', 'NVIDIA RTX 4060 8GB graphics card', 299.99, 30, 'Components'),
    ('CPU Cooler AIO', '240mm AIO liquid CPU cooler', 119.99, 65, 'Components'),
    ('Motherboard B550', 'AMD B550 ATX motherboard', 149.99, 50, 'Components'),
    ('Case Mid Tower', 'RGB mid-tower case with tempered glass', 89.99, 75, 'Components'),
    ('PSU 750W Gold', '750W 80+ Gold modular power supply', 109.99, 55, 'Components'),
    ('Microphone USB', 'USB condenser microphone for streaming', 79.99, 90, 'Audio'),
    ('Streaming Deck', '15-key streaming control deck', 149.99, 40, 'Accessories'),
    ('Ring Light', '18-inch LED ring light with stand', 49.99, 120, 'Accessories'),
    ('Green Screen', '6x9ft collapsible green screen backdrop', 39.99, 80, 'Accessories'),
    ('Laptop Stand', 'Adjustable aluminum laptop stand', 29.99, 150, 'Accessories'),
    ('Monitor Arm', 'Dual monitor mount arm', 79.99, 60, 'Accessories'),
    ('Cable Management', 'Cable management kit with clips', 19.99, 200, 'Accessories'),
    ('Desk Mat', 'Large gaming desk mat 36x18 inches', 24.99, 100, 'Accessories'),
    ('Webcam 4K', '4K UHD webcam with HDR', 199.99, 35, 'Accessories'),
    ('Speaker System', '2.1 stereo speaker system', 89.99, 70, 'Audio'),
    ('Soundbar', '40-inch soundbar with subwoofer', 179.99, 40, 'Audio'),
    ('VR Headset', 'Virtual reality headset with controllers', 399.99, 25, 'Gaming'),
    ('Game Controller', 'Wireless gaming controller for PC', 59.99, 95, 'Gaming')
ON CONFLICT DO NOTHING;

-- Add 40 more orders with various dates and statuses
INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address)
SELECT 
    c.id,
    new_orders.order_date::timestamp,
    new_orders.total_amount,
    new_orders.status,
    new_orders.shipping_address
FROM (VALUES
    ('alice.johnson@example.com', '2024-04-01 09:00:00', 129.99, 'delivered', '123 Main St, New York, NY 10001'),
    ('bob.smith@example.com', '2024-04-02 10:15:00', 349.99, 'shipped', '456 Oak Ave, Los Angeles, CA 90001'),
    ('charlie.brown@example.com', '2024-04-03 11:30:00', 299.99, 'processing', '789 Pine Rd, Chicago, IL 60601'),
    ('diana.prince@example.com', '2024-04-04 12:45:00', 119.99, 'delivered', '321 Elm St, Houston, TX 77001'),
    ('edward.norton@example.com', '2024-04-05 13:00:00', 149.99, 'pending', '654 Maple Dr, Phoenix, AZ 85001'),
    ('fiona.apple@example.com', '2024-04-06 14:15:00', 89.99, 'shipped', '987 Cedar Ln, Philadelphia, PA 19101'),
    ('george.lucas@example.com', '2024-04-07 15:30:00', 109.99, 'delivered', '147 Birch Way, San Antonio, TX 78201'),
    ('hannah.montana@example.com', '2024-04-08 16:45:00', 79.99, 'processing', '258 Spruce Ct, San Diego, CA 92101'),
    ('isaac.newton@example.com', '2024-04-09 08:00:00', 149.99, 'delivered', '369 Willow St, Dallas, TX 75201'),
    ('julia.roberts@example.com', '2024-04-10 09:15:00', 49.99, 'shipped', '741 Ash Ave, San Jose, CA 95101'),
    ('kevin.hart@example.com', '2024-04-11 10:30:00', 39.99, 'delivered', '852 Poplar Rd, Austin, TX 78701'),
    ('lisa.simpson@example.com', '2024-04-12 11:45:00', 29.99, 'processing', '963 Fir Dr, Jacksonville, FL 32201'),
    ('mike.tyson@example.com', '2024-04-13 12:00:00', 79.99, 'delivered', '159 Hemlock Ln, Fort Worth, TX 76101'),
    ('nancy.drew@example.com', '2024-04-14 13:15:00', 19.99, 'shipped', '357 Cypress Way, Columbus, OH 43201'),
    ('oliver.twist@example.com', '2024-04-15 14:30:00', 24.99, 'delivered', '468 Redwood St, Charlotte, NC 28201'),
    ('patricia.highsmith@example.com', '2024-04-16 15:45:00', 199.99, 'processing', '579 Sequoia Ave, San Francisco, CA 94101'),
    ('quentin.tarantino@example.com', '2024-04-17 16:00:00', 89.99, 'delivered', '680 Magnolia Rd, Indianapolis, IN 46201'),
    ('rachel.green@example.com', '2024-04-18 08:15:00', 179.99, 'shipped', '791 Dogwood Dr, Seattle, WA 98101'),
    ('steve.jobs@example.com', '2024-04-19 09:30:00', 399.99, 'delivered', '802 Cherry Ct, Denver, CO 80201'),
    ('tina.fey@example.com', '2024-04-20 10:45:00', 59.99, 'processing', '913 Walnut Ln, Washington, DC 20001'),
    ('ursula.leguin@example.com', '2024-04-21 11:00:00', 129.99, 'delivered', '124 Chestnut Way, Boston, MA 02101'),
    ('victor.hugo@example.com', '2024-04-22 12:15:00', 349.99, 'shipped', '235 Hickory St, El Paso, TX 79901'),
    ('wendy.darling@example.com', '2024-04-23 13:30:00', 299.99, 'delivered', '346 Sycamore Ave, Nashville, TN 37201'),
    ('yara.shahidi@example.com', '2024-04-24 14:45:00', 119.99, 'processing', '457 Alder Rd, Detroit, MI 48201'),
    ('alice.johnson@example.com', '2024-04-25 15:00:00', 149.99, 'delivered', '123 Main St, New York, NY 10001'),
    ('bob.smith@example.com', '2024-04-26 08:15:00', 89.99, 'shipped', '456 Oak Ave, Los Angeles, CA 90001'),
    ('charlie.brown@example.com', '2024-04-27 09:30:00', 109.99, 'delivered', '789 Pine Rd, Chicago, IL 60601'),
    ('diana.prince@example.com', '2024-04-28 10:45:00', 79.99, 'processing', '321 Elm St, Houston, TX 77001'),
    ('edward.norton@example.com', '2024-04-29 11:00:00', 149.99, 'delivered', '654 Maple Dr, Phoenix, AZ 85001'),
    ('fiona.apple@example.com', '2024-04-30 12:15:00', 49.99, 'shipped', '987 Cedar Ln, Philadelphia, PA 19101'),
    ('george.lucas@example.com', '2024-05-01 13:30:00', 39.99, 'delivered', '147 Birch Way, San Antonio, TX 78201'),
    ('hannah.montana@example.com', '2024-05-02 14:45:00', 29.99, 'processing', '258 Spruce Ct, San Diego, CA 92101'),
    ('isaac.newton@example.com', '2024-05-03 15:00:00', 79.99, 'delivered', '369 Willow St, Dallas, TX 75201'),
    ('julia.roberts@example.com', '2024-05-04 08:15:00', 19.99, 'shipped', '741 Ash Ave, San Jose, CA 95101'),
    ('kevin.hart@example.com', '2024-05-05 09:30:00', 24.99, 'delivered', '852 Poplar Rd, Austin, TX 78701'),
    ('lisa.simpson@example.com', '2024-05-06 10:45:00', 199.99, 'processing', '963 Fir Dr, Jacksonville, FL 32201'),
    ('mike.tyson@example.com', '2024-05-07 11:00:00', 89.99, 'delivered', '159 Hemlock Ln, Fort Worth, TX 76101'),
    ('nancy.drew@example.com', '2024-05-08 12:15:00', 179.99, 'shipped', '357 Cypress Way, Columbus, OH 43201'),
    ('oliver.twist@example.com', '2024-05-09 13:30:00', 399.99, 'delivered', '468 Redwood St, Charlotte, NC 28201'),
    ('patricia.highsmith@example.com', '2024-05-10 14:45:00', 59.99, 'processing', '579 Sequoia Ave, San Francisco, CA 94101')
) AS new_orders(email, order_date, total_amount, status, shipping_address)
JOIN customers c ON c.email = new_orders.email
WHERE NOT EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.id 
    AND DATE(o.order_date) = DATE(new_orders.order_date::timestamp)
    AND ABS(o.total_amount - new_orders.total_amount) < 0.01
);

-- Add order items for the new orders
-- This will match products to orders based on order dates and amounts
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    CASE 
        WHEN o.total_amount >= p.price * 2 THEN 2
        ELSE 1
    END as quantity,
    p.price,
    CASE 
        WHEN o.total_amount >= p.price * 2 THEN p.price * 2
        ELSE p.price
    END as subtotal
FROM orders o
JOIN customers c ON o.customer_id = c.id
CROSS JOIN products p
WHERE o.order_date >= '2024-04-01'::timestamp
  AND o.order_date < '2024-05-11'::timestamp
  AND ABS(o.total_amount - p.price) < 5.00
  AND NOT EXISTS (
      SELECT 1 FROM order_items oi 
      WHERE oi.order_id = o.id 
      AND oi.product_id = p.id
  )
LIMIT 50;

-- Add more order items for orders that don't have items yet
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
SELECT 
    o.id,
    p.id,
    1,
    p.price,
    p.price
FROM orders o
CROSS JOIN products p
WHERE o.id NOT IN (SELECT DISTINCT order_id FROM order_items WHERE order_id IS NOT NULL)
  AND p.id = (
      SELECT id FROM products 
      WHERE price <= o.total_amount 
      ORDER BY ABS(price - o.total_amount) 
      LIMIT 1
  )
LIMIT 20;

-- Add 25 more support tickets
INSERT INTO support_tickets (customer_id, order_id, subject, description, status, priority, assigned_to, created_at)
SELECT 
    c.id,
    o.id,
    new_tickets.subject,
    new_tickets.description,
    new_tickets.status,
    new_tickets.priority,
    new_tickets.assigned_to,
    new_tickets.created_at::timestamp
FROM (VALUES
    ('alice.johnson@example.com', '2024-04-01', 'Keyboard keys not responding', 'Some keys on my mechanical keyboard are not working properly.', 'open', 'medium', 'support_agent_1', '2024-04-05 10:00:00'),
    ('bob.smith@example.com', '2024-04-02', 'Monitor dead pixels', 'My new monitor has several dead pixels in the center.', 'in_progress', 'high', 'support_agent_2', '2024-04-06 11:00:00'),
    ('charlie.brown@example.com', '2024-04-03', 'Graphics card overheating', 'My graphics card is overheating during gaming sessions.', 'open', 'high', 'support_agent_1', '2024-04-07 12:00:00'),
    ('diana.prince@example.com', '2024-04-04', 'CPU cooler noise', 'The AIO cooler is making loud noise.', 'resolved', 'medium', 'support_agent_2', '2024-04-08 13:00:00'),
    ('edward.norton@example.com', '2024-04-05', 'Motherboard compatibility', 'Will this motherboard work with my CPU?', 'resolved', 'low', NULL, '2024-04-09 14:00:00'),
    ('fiona.apple@example.com', '2024-04-06', 'Case fan not working', 'One of the case fans stopped spinning.', 'open', 'medium', 'support_agent_1', '2024-04-10 15:00:00'),
    ('george.lucas@example.com', '2024-04-07', 'PSU wattage question', 'Is 750W enough for my build?', 'resolved', 'low', 'support_agent_2', '2024-04-11 16:00:00'),
    ('hannah.montana@example.com', '2024-04-08', 'Microphone static', 'My USB microphone has static noise.', 'in_progress', 'medium', 'support_agent_1', '2024-04-12 09:00:00'),
    ('isaac.newton@example.com', '2024-04-09', 'Streaming deck buttons', 'Some buttons on my streaming deck are not responding.', 'open', 'medium', NULL, '2024-04-13 10:00:00'),
    ('julia.roberts@example.com', '2024-04-10', 'Ring light brightness', 'The ring light is not bright enough.', 'resolved', 'low', 'support_agent_2', '2024-04-14 11:00:00'),
    ('kevin.hart@example.com', '2024-04-11', 'Green screen wrinkles', 'My green screen arrived with wrinkles.', 'open', 'low', 'support_agent_1', '2024-04-15 12:00:00'),
    ('lisa.simpson@example.com', '2024-04-12', 'Laptop stand adjustment', 'The laptop stand is not adjusting properly.', 'in_progress', 'low', 'support_agent_2', '2024-04-16 13:00:00'),
    ('mike.tyson@example.com', '2024-04-13', 'Monitor arm installation', 'Need help installing the monitor arm.', 'resolved', 'low', NULL, '2024-04-17 14:00:00'),
    ('nancy.drew@example.com', '2024-04-14', 'Cable management tips', 'Looking for tips on cable management.', 'resolved', 'low', 'support_agent_1', '2024-04-18 15:00:00'),
    ('oliver.twist@example.com', '2024-04-15', 'Desk mat cleaning', 'How do I clean my gaming desk mat?', 'resolved', 'low', 'support_agent_2', '2024-04-19 16:00:00'),
    ('patricia.highsmith@example.com', '2024-04-16', 'Webcam focus issue', 'My 4K webcam is not focusing correctly.', 'open', 'medium', 'support_agent_1', '2024-04-20 09:00:00'),
    ('quentin.tarantino@example.com', '2024-04-17', 'Speaker system setup', 'Need help setting up my speaker system.', 'in_progress', 'medium', 'support_agent_2', '2024-04-21 10:00:00'),
    ('rachel.green@example.com', '2024-04-18', 'Soundbar connection', 'Having trouble connecting my soundbar.', 'open', 'medium', NULL, '2024-04-22 11:00:00'),
    ('steve.jobs@example.com', '2024-04-19', 'VR headset tracking', 'VR headset tracking is not working properly.', 'in_progress', 'high', 'support_agent_1', '2024-04-23 12:00:00'),
    ('tina.fey@example.com', '2024-04-20', 'Game controller drift', 'My game controller has stick drift.', 'open', 'medium', 'support_agent_2', '2024-04-24 13:00:00'),
    ('ursula.leguin@example.com', '2024-04-21', 'Keyboard RGB not working', 'The RGB lighting on my keyboard stopped working.', 'in_progress', 'low', 'support_agent_1', '2024-04-25 14:00:00'),
    ('victor.hugo@example.com', '2024-04-22', 'Monitor color accuracy', 'The monitor colors look washed out.', 'open', 'medium', 'support_agent_2', '2024-04-26 15:00:00'),
    ('wendy.darling@example.com', '2024-04-23', 'Graphics card driver', 'Need help updating graphics card drivers.', 'resolved', 'low', NULL, '2024-04-27 16:00:00'),
    ('yara.shahidi@example.com', '2024-04-24', 'CPU cooler leak', 'My AIO cooler appears to be leaking.', 'open', 'urgent', 'support_agent_1', '2024-04-28 09:00:00'),
    ('alice.johnson@example.com', '2024-04-25', 'Motherboard BIOS update', 'How do I update my motherboard BIOS?', 'resolved', 'low', 'support_agent_2', '2024-04-29 10:00:00')
) AS new_tickets(email, order_date, subject, description, status, priority, assigned_to, created_at)
JOIN customers c ON c.email = new_tickets.email
LEFT JOIN orders o ON o.customer_id = c.id AND DATE(o.order_date) = DATE(new_tickets.order_date::timestamp)
WHERE NOT EXISTS (
    SELECT 1 FROM support_tickets st 
    WHERE st.customer_id = c.id 
    AND st.subject = new_tickets.subject 
    AND DATE(st.created_at) = DATE(new_tickets.created_at::timestamp)
);

-- Add ticket messages for the new tickets
INSERT INTO ticket_messages (ticket_id, sender_type, message, created_at)
SELECT 
    t.id,
    new_messages.sender_type,
    new_messages.message,
    new_messages.created_at::timestamp
FROM (VALUES
    ('alice.johnson@example.com', '2024-04-05 10:00:00', 'customer', 'Some keys on my mechanical keyboard are not working properly.', '2024-04-05 10:00:00'),
    ('alice.johnson@example.com', '2024-04-05 10:00:00', 'agent', 'I''m sorry to hear about the issue. Let''s troubleshoot this. Which specific keys are not responding?', '2024-04-05 10:30:00'),
    ('bob.smith@example.com', '2024-04-06 11:00:00', 'customer', 'My new monitor has several dead pixels in the center.', '2024-04-06 11:00:00'),
    ('bob.smith@example.com', '2024-04-06 11:00:00', 'agent', 'I apologize for the inconvenience. Dead pixels are covered under warranty. We can arrange a replacement.', '2024-04-06 11:30:00'),
    ('charlie.brown@example.com', '2024-04-07 12:00:00', 'customer', 'My graphics card is overheating during gaming sessions.', '2024-04-07 12:00:00'),
    ('charlie.brown@example.com', '2024-04-07 12:00:00', 'agent', 'Overheating can be caused by several factors. Let''s check your case airflow and thermal paste application.', '2024-04-07 12:30:00'),
    ('diana.prince@example.com', '2024-04-08 13:00:00', 'customer', 'The AIO cooler is making loud noise.', '2024-04-08 13:00:00'),
    ('diana.prince@example.com', '2024-04-08 13:00:00', 'agent', 'Loud noise from an AIO cooler usually indicates a pump issue or air bubbles. Let''s troubleshoot this step by step.', '2024-04-08 13:30:00'),
    ('edward.norton@example.com', '2024-04-09 14:00:00', 'customer', 'Will this motherboard work with my CPU?', '2024-04-09 14:00:00'),
    ('edward.norton@example.com', '2024-04-09 14:00:00', 'agent', 'Yes, the B550 motherboard is compatible with AMD Ryzen processors. What CPU model do you have?', '2024-04-09 14:30:00'),
    ('fiona.apple@example.com', '2024-04-10 15:00:00', 'customer', 'One of the case fans stopped spinning.', '2024-04-10 15:00:00'),
    ('george.lucas@example.com', '2024-04-11 16:00:00', 'customer', 'Is 750W enough for my build?', '2024-04-11 16:00:00'),
    ('george.lucas@example.com', '2024-04-11 16:00:00', 'agent', '750W should be sufficient for most builds. What components are you using? I can help you calculate the exact power requirements.', '2024-04-11 16:30:00'),
    ('hannah.montana@example.com', '2024-04-12 09:00:00', 'customer', 'My USB microphone has static noise.', '2024-04-12 09:00:00'),
    ('isaac.newton@example.com', '2024-04-13 10:00:00', 'customer', 'Some buttons on my streaming deck are not responding.', '2024-04-13 10:00:00'),
    ('julia.roberts@example.com', '2024-04-14 11:00:00', 'customer', 'The ring light is not bright enough.', '2024-04-14 11:00:00'),
    ('julia.roberts@example.com', '2024-04-14 11:00:00', 'agent', 'The ring light has adjustable brightness settings. Have you tried adjusting the brightness dial?', '2024-04-14 11:30:00'),
    ('kevin.hart@example.com', '2024-04-15 12:00:00', 'customer', 'My green screen arrived with wrinkles.', '2024-04-15 12:00:00'),
    ('lisa.simpson@example.com', '2024-04-16 13:00:00', 'customer', 'The laptop stand is not adjusting properly.', '2024-04-16 13:00:00'),
    ('mike.tyson@example.com', '2024-04-17 14:00:00', 'customer', 'Need help installing the monitor arm.', '2024-04-17 14:00:00'),
    ('mike.tyson@example.com', '2024-04-17 14:00:00', 'agent', 'I''d be happy to help! The monitor arm comes with installation instructions. Are you mounting it to a desk or wall?', '2024-04-17 14:30:00'),
    ('nancy.drew@example.com', '2024-04-18 15:00:00', 'customer', 'Looking for tips on cable management.', '2024-04-18 15:00:00'),
    ('nancy.drew@example.com', '2024-04-18 15:00:00', 'agent', 'Great question! I recommend using cable clips, zip ties, and routing cables behind your desk. The cable management kit includes everything you need.', '2024-04-18 15:30:00'),
    ('oliver.twist@example.com', '2024-04-19 16:00:00', 'customer', 'How do I clean my gaming desk mat?', '2024-04-19 16:00:00'),
    ('oliver.twist@example.com', '2024-04-19 16:00:00', 'agent', 'You can clean the desk mat with a damp cloth and mild soap. Avoid using harsh chemicals. Let it air dry completely before use.', '2024-04-19 16:30:00'),
    ('patricia.highsmith@example.com', '2024-04-20 09:00:00', 'customer', 'My 4K webcam is not focusing correctly.', '2024-04-20 09:00:00'),
    ('quentin.tarantino@example.com', '2024-04-21 10:00:00', 'customer', 'Need help setting up my speaker system.', '2024-04-21 10:00:00'),
    ('rachel.green@example.com', '2024-04-22 11:00:00', 'customer', 'Having trouble connecting my soundbar.', '2024-04-22 11:00:00'),
    ('steve.jobs@example.com', '2024-04-23 12:00:00', 'customer', 'VR headset tracking is not working properly.', '2024-04-23 12:00:00'),
    ('tina.fey@example.com', '2024-04-24 13:00:00', 'customer', 'My game controller has stick drift.', '2024-04-24 13:00:00'),
    ('ursula.leguin@example.com', '2024-04-25 14:00:00', 'customer', 'The RGB lighting on my keyboard stopped working.', '2024-04-25 14:00:00'),
    ('victor.hugo@example.com', '2024-04-26 15:00:00', 'customer', 'The monitor colors look washed out.', '2024-04-26 15:00:00'),
    ('wendy.darling@example.com', '2024-04-27 16:00:00', 'customer', 'Need help updating graphics card drivers.', '2024-04-27 16:00:00'),
    ('wendy.darling@example.com', '2024-04-27 16:00:00', 'agent', 'You can download the latest drivers from NVIDIA''s website. I can provide you with a direct link if needed.', '2024-04-27 16:30:00'),
    ('yara.shahidi@example.com', '2024-04-28 09:00:00', 'customer', 'My AIO cooler appears to be leaking.', '2024-04-28 09:00:00'),
    ('yara.shahidi@example.com', '2024-04-28 09:00:00', 'agent', 'This is a serious issue. Please stop using the cooler immediately and unplug your system. We will send a replacement right away.', '2024-04-28 09:30:00'),
    ('alice.johnson@example.com', '2024-04-29 10:00:00', 'customer', 'How do I update my motherboard BIOS?', '2024-04-29 10:00:00'),
    ('alice.johnson@example.com', '2024-04-29 10:00:00', 'agent', 'BIOS updates should be done carefully. I recommend downloading the BIOS file from the manufacturer''s website and following their instructions precisely.', '2024-04-29 10:30:00')
) AS new_messages(email, order_date, sender_type, message, created_at)
JOIN customers c ON c.email = new_messages.email
LEFT JOIN orders o ON o.customer_id = c.id AND (new_messages.order_date IS NULL OR DATE(o.order_date) = DATE(new_messages.order_date::timestamp))
LEFT JOIN support_tickets t ON t.customer_id = c.id AND (o.id IS NULL OR t.order_id = o.id) AND DATE(t.created_at) = DATE(new_messages.created_at::timestamp)
WHERE t.id IS NOT NULL
ON CONFLICT DO NOTHING;

-- Display summary of added data
SELECT 'Total customers' as summary, COUNT(*) as count FROM customers;
SELECT 'Total products' as summary, COUNT(*) as count FROM products;
SELECT 'Total orders' as summary, COUNT(*) as count FROM orders;
SELECT 'Total order items' as summary, COUNT(*) as count FROM order_items;
SELECT 'Total support tickets' as summary, COUNT(*) as count FROM support_tickets;
SELECT 'Total ticket messages' as summary, COUNT(*) as count FROM ticket_messages;

