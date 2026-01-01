-- Total Energies Fuel Management System Database Schema
-- This script initializes the database with fuel management tables and sample data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Fuel Types Table
CREATE TABLE IF NOT EXISTS fuel_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    unit_price_per_liter DECIMAL(10, 4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuel Stations Table
CREATE TABLE IF NOT EXISTS fuel_stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(20),
    email VARCHAR(255),
    manager_name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Station Fuel Inventory Table
CREATE TABLE IF NOT EXISTS station_fuel_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID NOT NULL REFERENCES fuel_stations(id) ON DELETE CASCADE,
    fuel_type_id UUID NOT NULL REFERENCES fuel_types(id) ON DELETE CASCADE,
    current_stock_liters DECIMAL(12, 2) NOT NULL DEFAULT 0,
    min_stock_level DECIMAL(12, 2) NOT NULL DEFAULT 0,
    max_capacity_liters DECIMAL(12, 2) NOT NULL,
    last_refill_date TIMESTAMP,
    last_refill_quantity DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(station_id, fuel_type_id)
);

-- Vehicles/Fleet Table
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_registration VARCHAR(50) NOT NULL UNIQUE,
    vehicle_type VARCHAR(50) NOT NULL,
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    fuel_type_id UUID NOT NULL REFERENCES fuel_types(id),
    tank_capacity_liters DECIMAL(8, 2),
    current_fuel_level_percent DECIMAL(5, 2) DEFAULT 0,
    odometer_reading INTEGER DEFAULT 0,
    assigned_driver VARCHAR(200),
    department VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'retired')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuel Cards Table
CREATE TABLE IF NOT EXISTS fuel_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_number VARCHAR(50) NOT NULL UNIQUE,
    card_holder_name VARCHAR(200) NOT NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    department VARCHAR(100),
    credit_limit DECIMAL(10, 2),
    current_balance DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'expired', 'cancelled')),
    expiry_date DATE,
    issued_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuel Transactions Table
CREATE TABLE IF NOT EXISTS fuel_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_number VARCHAR(100) NOT NULL UNIQUE,
    station_id UUID NOT NULL REFERENCES fuel_stations(id),
    fuel_type_id UUID NOT NULL REFERENCES fuel_types(id),
    fuel_card_id UUID REFERENCES fuel_cards(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    quantity_liters DECIMAL(10, 3) NOT NULL,
    unit_price DECIMAL(10, 4) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    odometer_reading INTEGER,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(20) DEFAULT 'purchase' CHECK (transaction_type IN ('purchase', 'refill', 'transfer', 'adjustment')),
    payment_method VARCHAR(50) DEFAULT 'fuel_card' CHECK (payment_method IN ('fuel_card', 'cash', 'credit_card', 'invoice')),
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuel Refills Table (for station inventory)
CREATE TABLE IF NOT EXISTS fuel_refills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    refill_number VARCHAR(100) NOT NULL UNIQUE,
    station_id UUID NOT NULL REFERENCES fuel_stations(id),
    fuel_type_id UUID NOT NULL REFERENCES fuel_types(id),
    supplier_name VARCHAR(255),
    quantity_liters DECIMAL(12, 2) NOT NULL,
    unit_price DECIMAL(10, 4) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    delivery_date TIMESTAMP NOT NULL,
    delivery_truck_number VARCHAR(50),
    driver_name VARCHAR(200),
    quality_certificate_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('scheduled', 'in_transit', 'delivered', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuel Consumption Reports Table
CREATE TABLE IF NOT EXISTS fuel_consumption_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_date DATE NOT NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    department VARCHAR(100),
    total_consumption_liters DECIMAL(10, 3) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    average_price_per_liter DECIMAL(10, 4) NOT NULL,
    distance_km INTEGER,
    fuel_efficiency_km_per_liter DECIMAL(8, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, vehicle_id)
);

-- Support Tickets Table (for fuel management issues)
CREATE TABLE IF NOT EXISTS fuel_support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    station_id UUID REFERENCES fuel_stations(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    fuel_card_id UUID REFERENCES fuel_cards(id) ON DELETE SET NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) CHECK (category IN ('station_issue', 'vehicle_issue', 'card_issue', 'transaction_issue', 'inventory_issue', 'other')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_fuel_stations_status ON fuel_stations(status);
CREATE INDEX IF NOT EXISTS idx_fuel_stations_city ON fuel_stations(city);
CREATE INDEX IF NOT EXISTS idx_fuel_stations_country ON fuel_stations(country);
CREATE INDEX IF NOT EXISTS idx_station_fuel_inventory_station ON station_fuel_inventory(station_id);
CREATE INDEX IF NOT EXISTS idx_station_fuel_inventory_fuel_type ON station_fuel_inventory(fuel_type_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_registration ON vehicles(vehicle_registration);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_department ON vehicles(department);
CREATE INDEX IF NOT EXISTS idx_fuel_cards_number ON fuel_cards(card_number);
CREATE INDEX IF NOT EXISTS idx_fuel_cards_status ON fuel_cards(status);
CREATE INDEX IF NOT EXISTS idx_fuel_cards_vehicle ON fuel_cards(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_fuel_transactions_station ON fuel_transactions(station_id);
CREATE INDEX IF NOT EXISTS idx_fuel_transactions_date ON fuel_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fuel_transactions_card ON fuel_transactions(fuel_card_id);
CREATE INDEX IF NOT EXISTS idx_fuel_transactions_vehicle ON fuel_transactions(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_fuel_transactions_type ON fuel_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_fuel_refills_station ON fuel_refills(station_id);
CREATE INDEX IF NOT EXISTS idx_fuel_refills_date ON fuel_refills(delivery_date);
CREATE INDEX IF NOT EXISTS idx_fuel_consumption_reports_date ON fuel_consumption_reports(report_date);
CREATE INDEX IF NOT EXISTS idx_fuel_consumption_reports_vehicle ON fuel_consumption_reports(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_fuel_support_tickets_status ON fuel_support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_fuel_support_tickets_priority ON fuel_support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_fuel_support_tickets_station ON fuel_support_tickets(station_id);

-- Insert sample fuel types
INSERT INTO fuel_types (id, name, code, description, unit_price_per_liter) VALUES
    ('f1000000-0000-0000-0000-000000000001'::uuid, 'Unleaded 95', 'UL95', 'Premium unleaded gasoline 95 octane', 1.459),
    ('f1000000-0000-0000-0000-000000000002'::uuid, 'Unleaded 98', 'UL98', 'Super premium unleaded gasoline 98 octane', 1.589),
    ('f1000000-0000-0000-0000-000000000003'::uuid, 'Diesel', 'DIESEL', 'Standard diesel fuel', 1.389),
    ('f1000000-0000-0000-0000-000000000004'::uuid, 'Premium Diesel', 'DIESEL_PRE', 'Premium diesel with additives', 1.459),
    ('f1000000-0000-0000-0000-000000000005'::uuid, 'LPG', 'LPG', 'Liquefied Petroleum Gas', 0.789),
    ('f1000000-0000-0000-0000-000000000006'::uuid, 'AdBlue', 'ADBLUE', 'Diesel exhaust fluid', 0.899)
ON CONFLICT (code) DO NOTHING;

-- Insert sample fuel stations
INSERT INTO fuel_stations (id, station_code, name, address, city, country, latitude, longitude, phone, email, manager_name, status) VALUES
    ('a2000000-0000-0000-0000-000000000001'::uuid, 'TE-PAR-001', 'Total Energies Paris Centre', '123 Avenue des Champs-Élysées', 'Paris', 'France', 48.8566, 2.3522, '+33-1-2345-6789', 'paris.centre@totalenergies.com', 'Jean Dupont', 'active'),
    ('a2000000-0000-0000-0000-000000000002'::uuid, 'TE-LYO-002', 'Total Energies Lyon Nord', '456 Rue de la République', 'Lyon', 'France', 45.7640, 4.8357, '+33-4-1234-5678', 'lyon.nord@totalenergies.com', 'Marie Martin', 'active'),
    ('a2000000-0000-0000-0000-000000000003'::uuid, 'TE-MAR-003', 'Total Energies Marseille Port', '789 Boulevard du Port', 'Marseille', 'France', 43.2965, 5.3698, '+33-4-9876-5432', 'marseille.port@totalenergies.com', 'Pierre Bernard', 'active'),
    ('a2000000-0000-0000-0000-000000000004'::uuid, 'TE-TOU-004', 'Total Energies Toulouse Sud', '321 Route de Toulouse', 'Toulouse', 'France', 43.6047, 1.4442, '+33-5-1111-2222', 'toulouse.sud@totalenergies.com', 'Sophie Laurent', 'active'),
    ('a2000000-0000-0000-0000-000000000005'::uuid, 'TE-NIC-005', 'Total Energies Nice Côte', '654 Promenade des Anglais', 'Nice', 'France', 43.7102, 7.2620, '+33-4-3333-4444', 'nice.cote@totalenergies.com', 'Antoine Moreau', 'active'),
    ('a2000000-0000-0000-0000-000000000006'::uuid, 'TE-BOR-006', 'Total Energies Bordeaux Ouest', '987 Avenue de la Libération', 'Bordeaux', 'France', 44.8378, -0.5792, '+33-5-5555-6666', 'bordeaux.ouest@totalenergies.com', 'Claire Dubois', 'active'),
    ('a2000000-0000-0000-0000-000000000007'::uuid, 'TE-LIL-007', 'Total Energies Lille Nord', '147 Rue de Lille', 'Lille', 'France', 50.6292, 3.0573, '+33-3-7777-8888', 'lille.nord@totalenergies.com', 'Thomas Petit', 'active'),
    ('a2000000-0000-0000-0000-000000000008'::uuid, 'TE-STR-008', 'Total Energies Strasbourg Est', '258 Avenue de Strasbourg', 'Strasbourg', 'France', 48.5734, 7.7521, '+33-3-9999-0000', 'strasbourg.est@totalenergies.com', 'Isabelle Roux', 'active')
ON CONFLICT (station_code) DO NOTHING;

-- Insert station fuel inventory
INSERT INTO station_fuel_inventory (station_id, fuel_type_id, current_stock_liters, min_stock_level, max_capacity_liters, last_refill_date, last_refill_quantity) VALUES
    ('a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 45000.00, 10000.00, 100000.00, '2024-03-15 08:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000002'::uuid, 25000.00, 5000.00, 50000.00, '2024-03-14 10:00:00', 30000.00),
    ('a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 60000.00, 15000.00, 120000.00, '2024-03-16 09:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000002'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 38000.00, 10000.00, 100000.00, '2024-03-14 07:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000002'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 55000.00, 15000.00, 120000.00, '2024-03-15 11:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 42000.00, 10000.00, 100000.00, '2024-03-13 14:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 58000.00, 15000.00, 120000.00, '2024-03-14 16:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000005'::uuid, 15000.00, 3000.00, 30000.00, '2024-03-12 10:00:00', 20000.00),
    ('a2000000-0000-0000-0000-000000000004'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 35000.00, 10000.00, 100000.00, '2024-03-15 09:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000004'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 52000.00, 15000.00, 120000.00, '2024-03-16 08:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000005'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 48000.00, 10000.00, 100000.00, '2024-03-14 12:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000005'::uuid, 'f1000000-0000-0000-0000-000000000002'::uuid, 28000.00, 5000.00, 50000.00, '2024-03-13 15:00:00', 30000.00),
    ('a2000000-0000-0000-0000-000000000005'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 62000.00, 15000.00, 120000.00, '2024-03-15 13:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000006'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 40000.00, 10000.00, 100000.00, '2024-03-13 11:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000006'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 56000.00, 15000.00, 120000.00, '2024-03-14 10:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000007'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 33000.00, 10000.00, 100000.00, '2024-03-12 08:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000007'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 50000.00, 15000.00, 120000.00, '2024-03-13 09:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000008'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 37000.00, 10000.00, 100000.00, '2024-03-14 07:00:00', 50000.00),
    ('a2000000-0000-0000-0000-000000000008'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 54000.00, 15000.00, 120000.00, '2024-03-15 10:00:00', 70000.00),
    ('a2000000-0000-0000-0000-000000000008'::uuid, 'f1000000-0000-0000-0000-000000000004'::uuid, 22000.00, 5000.00, 50000.00, '2024-03-13 11:00:00', 30000.00)
ON CONFLICT (station_id, fuel_type_id) DO NOTHING;

-- Insert sample vehicles
INSERT INTO vehicles (id, vehicle_registration, vehicle_type, make, model, year, fuel_type_id, tank_capacity_liters, current_fuel_level_percent, odometer_reading, assigned_driver, department, status) VALUES
    ('a3000000-0000-0000-0000-000000000001'::uuid, 'FR-123-AB', 'Delivery Van', 'Renault', 'Master', 2022, 'f1000000-0000-0000-0000-000000000003'::uuid, 80.00, 65.50, 45230, 'Marc Lefebvre', 'Logistics', 'active'),
    ('a3000000-0000-0000-0000-000000000002'::uuid, 'FR-456-CD', 'Company Car', 'Peugeot', '308', 2023, 'f1000000-0000-0000-0000-000000000001'::uuid, 50.00, 42.00, 12350, 'Sophie Martin', 'Sales', 'active'),
    ('a3000000-0000-0000-0000-000000000003'::uuid, 'FR-789-EF', 'Truck', 'Mercedes', 'Actros', 2021, 'f1000000-0000-0000-0000-000000000003'::uuid, 400.00, 78.25, 125680, 'Jean-Pierre Durand', 'Transport', 'active'),
    ('a3000000-0000-0000-0000-000000000004'::uuid, 'FR-321-GH', 'Company Car', 'Citroën', 'C5', 2023, 'f1000000-0000-0000-0000-000000000001'::uuid, 55.00, 88.00, 8750, 'Marie Dubois', 'Management', 'active'),
    ('a3000000-0000-0000-0000-000000000005'::uuid, 'FR-654-IJ', 'Delivery Van', 'Ford', 'Transit', 2022, 'f1000000-0000-0000-0000-000000000003'::uuid, 75.00, 35.00, 38920, 'Pierre Moreau', 'Logistics', 'active'),
    ('a3000000-0000-0000-0000-000000000006'::uuid, 'FR-987-KL', 'Company Car', 'Volkswagen', 'Golf', 2023, 'f1000000-0000-0000-0000-000000000002'::uuid, 50.00, 92.50, 15200, 'Thomas Bernard', 'Sales', 'active'),
    ('a3000000-0000-0000-0000-000000000007'::uuid, 'FR-147-MN', 'Truck', 'Volvo', 'FH', 2020, 'f1000000-0000-0000-0000-000000000003'::uuid, 500.00, 45.00, 198450, 'Antoine Petit', 'Transport', 'active'),
    ('a3000000-0000-0000-0000-000000000008'::uuid, 'FR-258-OP', 'Company Car', 'BMW', '320d', 2023, 'f1000000-0000-0000-0000-000000000004'::uuid, 57.00, 70.00, 11200, 'Claire Roux', 'Management', 'active'),
    ('a3000000-0000-0000-0000-000000000009'::uuid, 'FR-369-QR', 'Delivery Van', 'Peugeot', 'Partner', 2022, 'f1000000-0000-0000-0000-000000000003'::uuid, 60.00, 55.00, 42150, 'Isabelle Laurent', 'Logistics', 'active'),
    ('a3000000-0000-0000-0000-000000000010'::uuid, 'FR-741-ST', 'Company Car', 'Audi', 'A4', 2023, 'f1000000-0000-0000-0000-000000000001'::uuid, 58.00, 80.00, 9800, 'Nicolas Martin', 'Sales', 'active')
ON CONFLICT (vehicle_registration) DO NOTHING;

-- Insert sample fuel cards
INSERT INTO fuel_cards (id, card_number, card_holder_name, vehicle_id, department, credit_limit, current_balance, status, expiry_date, issued_date) VALUES
    ('a4000000-0000-0000-0000-000000000001'::uuid, 'TE-1234-5678-9012', 'Marc Lefebvre', 'a3000000-0000-0000-0000-000000000001'::uuid, 'Logistics', 2000.00, 1250.50, 'active', '2025-12-31', '2023-01-15'),
    ('a4000000-0000-0000-0000-000000000002'::uuid, 'TE-2345-6789-0123', 'Sophie Martin', 'a3000000-0000-0000-0000-000000000002'::uuid, 'Sales', 1500.00, 980.25, 'active', '2025-12-31', '2023-02-20'),
    ('a4000000-0000-0000-0000-000000000003'::uuid, 'TE-3456-7890-1234', 'Jean-Pierre Durand', 'a3000000-0000-0000-0000-000000000003'::uuid, 'Transport', 5000.00, 3200.75, 'active', '2025-12-31', '2023-01-10'),
    ('a4000000-0000-0000-0000-000000000004'::uuid, 'TE-4567-8901-2345', 'Marie Dubois', 'a3000000-0000-0000-0000-000000000004'::uuid, 'Management', 2000.00, 1450.00, 'active', '2025-12-31', '2023-03-05'),
    ('a4000000-0000-0000-0000-000000000005'::uuid, 'TE-5678-9012-3456', 'Pierre Moreau', 'a3000000-0000-0000-0000-000000000005'::uuid, 'Logistics', 2000.00, 1100.00, 'active', '2025-12-31', '2023-02-15'),
    ('a4000000-0000-0000-0000-000000000006'::uuid, 'TE-6789-0123-4567', 'Thomas Bernard', 'a3000000-0000-0000-0000-000000000006'::uuid, 'Sales', 1500.00, 750.50, 'active', '2025-12-31', '2023-03-20'),
    ('a4000000-0000-0000-0000-000000000007'::uuid, 'TE-7890-1234-5678', 'Antoine Petit', 'a3000000-0000-0000-0000-000000000007'::uuid, 'Transport', 5000.00, 2800.25, 'active', '2025-12-31', '2023-01-25'),
    ('a4000000-0000-0000-0000-000000000008'::uuid, 'TE-8901-2345-6789', 'Claire Roux', 'a3000000-0000-0000-0000-000000000008'::uuid, 'Management', 2000.00, 1650.00, 'active', '2025-12-31', '2023-04-10'),
    ('a4000000-0000-0000-0000-000000000009'::uuid, 'TE-9012-3456-7890', 'Isabelle Laurent', 'a3000000-0000-0000-0000-000000000009'::uuid, 'Logistics', 2000.00, 1320.75, 'active', '2025-12-31', '2023-02-28'),
    ('a4000000-0000-0000-0000-000000000010'::uuid, 'TE-0123-4567-8901', 'Nicolas Martin', 'a3000000-0000-0000-0000-000000000010'::uuid, 'Sales', 1500.00, 890.00, 'active', '2025-12-31', '2023-03-15')
ON CONFLICT (card_number) DO NOTHING;

-- Insert sample fuel transactions
INSERT INTO fuel_transactions (id, transaction_number, station_id, fuel_type_id, fuel_card_id, vehicle_id, quantity_liters, unit_price, total_amount, odometer_reading, transaction_date, transaction_type, payment_method, status) VALUES
    ('a5000000-0000-0000-0000-000000000001'::uuid, 'TXN-2024-001', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000001'::uuid, 'a3000000-0000-0000-0000-000000000001'::uuid, 45.50, 1.389, 63.20, 45120, '2024-03-15 08:30:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000002'::uuid, 'TXN-2024-002', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'a4000000-0000-0000-0000-000000000002'::uuid, 'a3000000-0000-0000-0000-000000000002'::uuid, 35.00, 1.459, 51.07, 12300, '2024-03-15 09:15:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000003'::uuid, 'TXN-2024-003', 'a2000000-0000-0000-0000-000000000002'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000003'::uuid, 'a3000000-0000-0000-0000-000000000003'::uuid, 280.00, 1.389, 388.92, 125500, '2024-03-15 10:00:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000004'::uuid, 'TXN-2024-004', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'a4000000-0000-0000-0000-000000000004'::uuid, 'a3000000-0000-0000-0000-000000000004'::uuid, 25.00, 1.459, 36.48, 8700, '2024-03-15 11:20:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000005'::uuid, 'TXN-2024-005', 'a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000005'::uuid, 'a3000000-0000-0000-0000-000000000005'::uuid, 50.00, 1.389, 69.45, 38850, '2024-03-15 14:30:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000006'::uuid, 'TXN-2024-006', 'a2000000-0000-0000-0000-000000000005'::uuid, 'f1000000-0000-0000-0000-000000000002'::uuid, 'a4000000-0000-0000-0000-000000000006'::uuid, 'a3000000-0000-0000-0000-000000000006'::uuid, 30.00, 1.589, 47.67, 15150, '2024-03-15 16:45:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000007'::uuid, 'TXN-2024-007', 'a2000000-0000-0000-0000-000000000002'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000007'::uuid, 'a3000000-0000-0000-0000-000000000007'::uuid, 350.00, 1.389, 486.15, 198200, '2024-03-16 07:00:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000008'::uuid, 'TXN-2024-008', 'a2000000-0000-0000-0000-000000000008'::uuid, 'f1000000-0000-0000-0000-000000000004'::uuid, 'a4000000-0000-0000-0000-000000000008'::uuid, 'a3000000-0000-0000-0000-000000000008'::uuid, 40.00, 1.459, 58.36, 11150, '2024-03-16 09:30:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000009'::uuid, 'TXN-2024-009', 'a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000009'::uuid, 'a3000000-0000-0000-0000-000000000009'::uuid, 42.00, 1.389, 58.34, 42080, '2024-03-16 12:15:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000010'::uuid, 'TXN-2024-010', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'a4000000-0000-0000-0000-000000000010'::uuid, 'a3000000-0000-0000-0000-000000000010'::uuid, 38.00, 1.459, 55.44, 9750, '2024-03-16 15:20:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000011'::uuid, 'TXN-2024-011', 'a2000000-0000-0000-0000-000000000004'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000001'::uuid, 'a3000000-0000-0000-0000-000000000001'::uuid, 48.00, 1.389, 66.67, 45280, '2024-03-17 08:45:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000012'::uuid, 'TXN-2024-012', 'a2000000-0000-0000-0000-000000000005'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'a4000000-0000-0000-0000-000000000002'::uuid, 'a3000000-0000-0000-0000-000000000002'::uuid, 32.00, 1.459, 46.69, 12350, '2024-03-17 10:30:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000013'::uuid, 'TXN-2024-013', 'a2000000-0000-0000-0000-000000000006'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000003'::uuid, 'a3000000-0000-0000-0000-000000000003'::uuid, 300.00, 1.389, 416.70, 125800, '2024-03-17 11:15:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000014'::uuid, 'TXN-2024-014', 'a2000000-0000-0000-0000-000000000007'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'a4000000-0000-0000-0000-000000000004'::uuid, 'a3000000-0000-0000-0000-000000000004'::uuid, 28.00, 1.459, 40.85, 8780, '2024-03-17 13:00:00', 'purchase', 'fuel_card', 'completed'),
    ('a5000000-0000-0000-0000-000000000015'::uuid, 'TXN-2024-015', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'a4000000-0000-0000-0000-000000000005'::uuid, 'a3000000-0000-0000-0000-000000000005'::uuid, 52.00, 1.389, 72.23, 38950, '2024-03-17 15:45:00', 'purchase', 'fuel_card', 'completed')
ON CONFLICT (transaction_number) DO NOTHING;

-- Insert sample fuel refills
INSERT INTO fuel_refills (id, refill_number, station_id, fuel_type_id, supplier_name, quantity_liters, unit_price, total_amount, delivery_date, delivery_truck_number, driver_name, quality_certificate_number, status) VALUES
    ('a6000000-0000-0000-0000-000000000001'::uuid, 'REF-2024-001', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'Total Energies Refinery', 50000.00, 1.350, 67500.00, '2024-03-15 08:00:00', 'TRUCK-001', 'François Leroy', 'QC-2024-001', 'completed'),
    ('a6000000-0000-0000-0000-000000000002'::uuid, 'REF-2024-002', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000002'::uuid, 'Total Energies Refinery', 30000.00, 1.480, 44400.00, '2024-03-14 10:00:00', 'TRUCK-002', 'Michel Dubois', 'QC-2024-002', 'completed'),
    ('a6000000-0000-0000-0000-000000000003'::uuid, 'REF-2024-003', 'a2000000-0000-0000-0000-000000000001'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'Total Energies Refinery', 70000.00, 1.280, 89600.00, '2024-03-16 09:00:00', 'TRUCK-003', 'Pierre Martin', 'QC-2024-003', 'completed'),
    ('a6000000-0000-0000-0000-000000000004'::uuid, 'REF-2024-004', 'a2000000-0000-0000-0000-000000000002'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'Total Energies Refinery', 50000.00, 1.350, 67500.00, '2024-03-14 07:00:00', 'TRUCK-001', 'François Leroy', 'QC-2024-004', 'completed'),
    ('a6000000-0000-0000-0000-000000000005'::uuid, 'REF-2024-005', 'a2000000-0000-0000-0000-000000000002'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'Total Energies Refinery', 70000.00, 1.280, 89600.00, '2024-03-15 11:00:00', 'TRUCK-003', 'Pierre Martin', 'QC-2024-005', 'completed'),
    ('a6000000-0000-0000-0000-000000000006'::uuid, 'REF-2024-006', 'a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000001'::uuid, 'Total Energies Refinery', 50000.00, 1.350, 67500.00, '2024-03-13 14:00:00', 'TRUCK-001', 'François Leroy', 'QC-2024-006', 'completed'),
    ('a6000000-0000-0000-0000-000000000007'::uuid, 'REF-2024-007', 'a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000003'::uuid, 'Total Energies Refinery', 70000.00, 1.280, 89600.00, '2024-03-14 16:00:00', 'TRUCK-003', 'Pierre Martin', 'QC-2024-007', 'completed'),
    ('a6000000-0000-0000-0000-000000000008'::uuid, 'REF-2024-008', 'a2000000-0000-0000-0000-000000000003'::uuid, 'f1000000-0000-0000-0000-000000000005'::uuid, 'LPG Supplier Co.', 20000.00, 0.750, 15000.00, '2024-03-12 10:00:00', 'TRUCK-LPG-001', 'Jacques Moreau', 'QC-LPG-2024-001', 'completed')
ON CONFLICT (refill_number) DO NOTHING;

-- Insert sample fuel consumption reports
INSERT INTO fuel_consumption_reports (report_date, vehicle_id, department, total_consumption_liters, total_cost, average_price_per_liter, distance_km, fuel_efficiency_km_per_liter) VALUES
    ('2024-03-15', 'a3000000-0000-0000-0000-000000000001'::uuid, 'Logistics', 45.50, 63.20, 1.389, 150, 3.30),
    ('2024-03-15', 'a3000000-0000-0000-0000-000000000002'::uuid, 'Sales', 35.00, 51.07, 1.459, 200, 5.71),
    ('2024-03-15', 'a3000000-0000-0000-0000-000000000003'::uuid, 'Transport', 280.00, 388.92, 1.389, 800, 2.86),
    ('2024-03-15', 'a3000000-0000-0000-0000-000000000004'::uuid, 'Management', 25.00, 36.48, 1.459, 180, 7.20),
    ('2024-03-15', 'a3000000-0000-0000-0000-000000000005'::uuid, 'Logistics', 50.00, 69.45, 1.389, 170, 3.40),
    ('2024-03-16', 'a3000000-0000-0000-0000-000000000007'::uuid, 'Transport', 350.00, 486.15, 1.389, 1000, 2.86),
    ('2024-03-16', 'a3000000-0000-0000-0000-000000000008'::uuid, 'Management', 40.00, 58.36, 1.459, 250, 6.25),
    ('2024-03-16', 'a3000000-0000-0000-0000-000000000009'::uuid, 'Logistics', 42.00, 58.34, 1.389, 140, 3.33),
    ('2024-03-17', 'a3000000-0000-0000-0000-000000000001'::uuid, 'Logistics', 48.00, 66.67, 1.389, 160, 3.33),
    ('2024-03-17', 'a3000000-0000-0000-0000-000000000003'::uuid, 'Transport', 300.00, 416.70, 1.389, 850, 2.83)
ON CONFLICT (report_date, vehicle_id) DO NOTHING;

-- Insert sample support tickets
INSERT INTO fuel_support_tickets (id, ticket_number, station_id, vehicle_id, fuel_card_id, subject, description, category, status, priority, assigned_to, created_at) VALUES
    ('a7000000-0000-0000-0000-000000000001'::uuid, 'TICKET-2024-001', 'a2000000-0000-0000-0000-000000000001'::uuid, NULL, NULL, 'Fuel pump malfunction', 'Pump #3 at Paris Centre station is not dispensing fuel properly. Customers reporting issues.', 'station_issue', 'open', 'high', 'support_agent_1', '2024-03-15 10:00:00'),
    ('a7000000-0000-0000-0000-000000000002'::uuid, 'TICKET-2024-002', NULL, 'a3000000-0000-0000-0000-000000000002'::uuid, NULL, 'Vehicle fuel efficiency issue', 'Vehicle FR-456-CD showing lower than expected fuel efficiency. Need inspection.', 'vehicle_issue', 'in_progress', 'medium', 'support_agent_2', '2024-03-14 14:30:00'),
    ('a7000000-0000-0000-0000-000000000003'::uuid, 'TICKET-2024-003', NULL, NULL, 'a4000000-0000-0000-0000-000000000003'::uuid, 'Fuel card declined', 'Fuel card TE-3456-7890-1234 was declined at station. Card shows active status.', 'card_issue', 'open', 'urgent', 'support_agent_1', '2024-03-16 08:15:00'),
    ('a7000000-0000-0000-0000-000000000004'::uuid, 'TICKET-2024-004', 'a2000000-0000-0000-0000-000000000002'::uuid, NULL, NULL, 'Low fuel inventory alert', 'Diesel inventory at Lyon Nord station is below minimum threshold. Refill needed urgently.', 'inventory_issue', 'open', 'high', 'support_agent_2', '2024-03-16 09:00:00'),
    ('a7000000-0000-0000-0000-000000000005'::uuid, 'TICKET-2024-005', NULL, NULL, 'a4000000-0000-0000-0000-000000000005'::uuid, 'Transaction discrepancy', 'Transaction amount on fuel card statement does not match receipt from station.', 'transaction_issue', 'in_progress', 'medium', 'support_agent_1', '2024-03-15 16:20:00')
ON CONFLICT (ticket_number) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW fuel_transaction_summary AS
SELECT 
    ft.id as transaction_id,
    ft.transaction_number,
    ft.transaction_date,
    fs.name as station_name,
    fs.city as station_city,
    ftyp.name as fuel_type_name,
    ftyp.code as fuel_type_code,
    v.vehicle_registration,
    v.vehicle_type,
    fc.card_number,
    fc.card_holder_name,
    ft.quantity_liters,
    ft.unit_price,
    ft.total_amount,
    ft.payment_method,
    ft.status
FROM fuel_transactions ft
JOIN fuel_stations fs ON ft.station_id = fs.id
JOIN fuel_types ftyp ON ft.fuel_type_id = ftyp.id
LEFT JOIN vehicles v ON ft.vehicle_id = v.id
LEFT JOIN fuel_cards fc ON ft.fuel_card_id = fc.id;

CREATE OR REPLACE VIEW station_inventory_status AS
SELECT 
    fs.station_code,
    fs.name as station_name,
    fs.city,
    ft.name as fuel_type_name,
    sfi.current_stock_liters,
    sfi.min_stock_level,
    sfi.max_capacity_liters,
    ROUND((sfi.current_stock_liters / sfi.max_capacity_liters * 100)::numeric, 2) as stock_percentage,
    CASE 
        WHEN sfi.current_stock_liters < sfi.min_stock_level THEN 'LOW'
        WHEN sfi.current_stock_liters < (sfi.min_stock_level * 1.5) THEN 'WARNING'
        ELSE 'OK'
    END as stock_status,
    sfi.last_refill_date,
    sfi.last_refill_quantity
FROM station_fuel_inventory sfi
JOIN fuel_stations fs ON sfi.station_id = fs.id
JOIN fuel_types ft ON sfi.fuel_type_id = ft.id;

CREATE OR REPLACE VIEW vehicle_fuel_summary AS
SELECT 
    v.vehicle_registration,
    v.vehicle_type,
    v.department,
    v.assigned_driver,
    ftyp.name as fuel_type_name,
    COUNT(ft.id) as total_transactions,
    SUM(ft.quantity_liters) as total_fuel_liters,
    SUM(ft.total_amount) as total_cost,
    AVG(ft.unit_price) as avg_price_per_liter,
    MAX(ft.transaction_date) as last_fuel_date
FROM vehicles v
LEFT JOIN fuel_transactions ft ON v.id = ft.vehicle_id
LEFT JOIN fuel_types ftyp ON ft.fuel_type_id = ftyp.id
GROUP BY v.id, v.vehicle_registration, v.vehicle_type, v.department, v.assigned_driver, ftyp.name;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
