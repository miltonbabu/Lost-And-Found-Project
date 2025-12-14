-- Lost and Found Management System Database Schema
-- SQLite database schema file

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',  -- 'admin' or 'user'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create lost_items table to store reported lost items
CREATE TABLE IF NOT EXISTS lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    lost_date DATE NOT NULL,
    location VARCHAR(200) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    image_filename VARCHAR(255),
    status VARCHAR(20) DEFAULT 'unclaimed',  -- unclaimed, claimed, returned
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create found_items table to store reported found items
CREATE TABLE IF NOT EXISTS found_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    found_date DATE NOT NULL,
    location VARCHAR(200) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    image_filename VARCHAR(255),
    status VARCHAR(20) DEFAULT 'unclaimed',  -- unclaimed, claimed, returned
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create claims table to track item claims and returns
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type VARCHAR(10) NOT NULL,  -- 'lost' or 'found'
    item_id INTEGER NOT NULL,
    claimant_name VARCHAR(100) NOT NULL,
    claimant_email VARCHAR(100),
    claimant_phone VARCHAR(20),
    claim_description TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES lost_items(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES found_items(id) ON DELETE CASCADE
);

-- Insert sample data for testing purposes (optional)
INSERT INTO lost_items (item_name, category, description, lost_date, location, contact_name, contact_email, contact_phone, status) VALUES
('Wallet', 'Electronics', 'Black leather wallet with cards and cash', '2024-12-01', 'Library', 'John Doe', 'john@example.com', '555-0101', 'unclaimed'),
('Phone', 'Electronics', 'iPhone 12 in blue case', '2024-12-02', 'Cafeteria', 'Jane Smith', 'jane@example.com', '555-0102', 'unclaimed');

INSERT INTO found_items (item_name, category, description, found_date, location, contact_name, contact_email, contact_phone, status) VALUES
('Umbrella', 'Clothing', 'Black umbrella with wooden handle', '2024-12-01', 'Main Entrance', 'Mike Johnson', 'mike@example.com', '555-0103', 'unclaimed'),
('Keys', 'Accessories', 'Set of 3 keys with red keychain', '2024-12-02', 'Parking Lot', 'Sarah Wilson', 'sarah@example.com', '555-0104', 'unclaimed');

-- Insert default users (passwords are hashed versions of 'password123' and 'admin123')
INSERT INTO users (username, password, email, full_name, role) VALUES
('admin', 'admin123_hash', 'admin@lostandfound.com', 'System Administrator', 'admin'),
('user', 'user123_hash', 'user@lostandfound.com', 'Regular User', 'user');