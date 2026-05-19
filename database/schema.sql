-- ============================================================
--  AGRI PLATFORM - MySQL Workbench Schema
--  Run this entire file in MySQL Workbench to set up the DB
-- ============================================================

CREATE DATABASE IF NOT EXISTS agri_platform;
USE agri_platform;

-- USERS
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer','buyer','rental','govt') NOT NULL DEFAULT 'farmer',
    phone VARCHAR(15),
    location VARCHAR(100),
    state VARCHAR(50),
    land_size_acres DECIMAL(10,2) DEFAULT 0,
    category VARCHAR(50) COMMENT 'SC/ST/OBC/General',
    profile_pic VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CROP LISTINGS
CREATE TABLE IF NOT EXISTS listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    quantity_kg DECIMAL(10,2) NOT NULL,
    price_per_kg DECIMAL(10,2) NOT NULL,
    description TEXT,
    harvest_date DATE,
    quality_grade ENUM('A','B','C') DEFAULT 'B',
    status ENUM('active','sold','expired') DEFAULT 'active',
    image_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- AUCTION BIDS
CREATE TABLE IF NOT EXISTS bids (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending','accepted','rejected') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id INT,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity_kg DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    payment_method ENUM('cash','upi','bank_transfer') DEFAULT 'cash',
    status ENUM('pending','completed','cancelled') DEFAULT 'pending',
    blockchain_hash VARCHAR(255) COMMENT 'For tamper-proof receipts',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(id),
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (seller_id) REFERENCES users(id)
);

-- EQUIPMENT
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    eq_type ENUM('tractor','harvester','sprayer','CRM','plough','seeder','other') NOT NULL,
    rate_per_hr DECIMAL(10,2) NOT NULL,
    location VARCHAR(100),
    description TEXT,
    gps_lat DECIMAL(9,6),
    gps_lng DECIMAL(9,6),
    health_status ENUM('good','maintenance_needed','under_repair') DEFAULT 'good',
    availability_status ENUM('available','rented','maintenance') DEFAULT 'available',
    image_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- RENTALS
CREATE TABLE IF NOT EXISTS rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    renter_id INT NOT NULL,
    rental_date DATE NOT NULL,
    hours INT NOT NULL,
    total_cost DECIMAL(10,2),
    status ENUM('confirmed','ongoing','completed','cancelled') DEFAULT 'confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (renter_id) REFERENCES users(id)
);

-- GOVT SCHEMES
CREATE TABLE IF NOT EXISTS govt_schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scheme_name VARCHAR(200) NOT NULL,
    description TEXT,
    eligibility TEXT,
    benefits TEXT,
    applicable_states VARCHAR(500) COMMENT 'comma-separated states or ALL',
    applicable_crops VARCHAR(500),
    min_land_acres DECIMAL(10,2) DEFAULT 0,
    category VARCHAR(100) COMMENT 'SC/ST/OBC/All',
    application_url VARCHAR(255),
    deadline DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- CROP PRICE HISTORY (for ML training)
CREATE TABLE IF NOT EXISTS price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    price_per_kg DECIMAL(10,2) NOT NULL,
    market_location VARCHAR(100),
    recorded_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- COMMUNITY FORUM
CREATE TABLE IF NOT EXISTS forum_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category ENUM('tips','weather','market','help','equipment') DEFAULT 'tips',
    upvotes INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- FORUM REPLIES
CREATE TABLE IF NOT EXISTS forum_replies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    type ENUM('bid','sale','scheme','system','weather') DEFAULT 'system',
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- WEATHER ALERTS
CREATE TABLE IF NOT EXISTS weather_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(100),
    alert_type VARCHAR(50),
    message TEXT,
    severity ENUM('low','medium','high') DEFAULT 'medium',
    valid_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────
-- SEED DATA
-- ──────────────────────────────────

INSERT INTO govt_schemes (scheme_name, description, eligibility, benefits, applicable_states, applicable_crops, min_land_acres, category, application_url, deadline) VALUES
('PM-KISAN', 'Pradhan Mantri Kisan Samman Nidhi - Direct income support to farmers', 'Small and marginal farmers with less than 5 acres land', '₹6000 per year in 3 installments', 'ALL', 'ALL', 0, 'All', 'https://pmkisan.gov.in', '2025-03-31'),
('PMFBY', 'Pradhan Mantri Fasal Bima Yojana - Crop insurance scheme', 'All farmers including sharecroppers', 'Crop insurance at 1.5-2% premium for Kharif/Rabi crops', 'ALL', 'ALL', 0, 'All', 'https://pmfby.gov.in', '2025-07-31'),
('KCC', 'Kisan Credit Card - Affordable loans for farmers', 'All farmers with land ownership proof', 'Loan up to ₹3 lakh at 4-7% interest rate', 'ALL', 'ALL', 0, 'All', 'https://www.rbi.org.in', '2025-12-31'),
('RKVY', 'Rashtriya Krishi Vikas Yojana - Agriculture development fund', 'State governments and farmer groups', 'Grants for agriculture infrastructure development', 'ALL', 'ALL', 0, 'All', 'https://rkvy.nic.in', '2025-09-30'),
('eNAM', 'Electronic National Agriculture Market - Online trading platform', 'All farmers registered with APMC', 'Access to pan-India market, transparent price discovery', 'ALL', 'ALL', 0, 'All', 'https://enam.gov.in', NULL),
('SMAM', 'Sub-Mission on Agricultural Mechanization - Equipment subsidy', 'Small and marginal farmers', '25-50% subsidy on agricultural machinery', 'ALL', 'ALL', 0, 'All', 'https://agrimachinery.nic.in', '2025-08-31');

INSERT INTO price_history (crop_name, price_per_kg, market_location, recorded_date) VALUES
('Tomato', 28.5, 'Chennai', CURDATE()),
('Rice', 25.0, 'Chennai', CURDATE()),
('Wheat', 22.0, 'Delhi', CURDATE()),
('Onion', 18.5, 'Mumbai', CURDATE()),
('Potato', 15.0, 'Kolkata', CURDATE()),
('Sugarcane', 3.5, 'UP', CURDATE()),
('Cotton', 65.0, 'Gujarat', CURDATE()),
('Soybean', 45.0, 'MP', CURDATE()),
('Maize', 19.0, 'Karnataka', CURDATE()),
('Groundnut', 55.0, 'Andhra Pradesh', CURDATE()),
('Tomato', 30.0, 'Chennai', DATE_SUB(CURDATE(), INTERVAL 1 DAY)),
('Rice', 24.5, 'Chennai', DATE_SUB(CURDATE(), INTERVAL 1 DAY)),
('Wheat', 21.5, 'Delhi', DATE_SUB(CURDATE(), INTERVAL 1 DAY)),
('Onion', 17.0, 'Mumbai', DATE_SUB(CURDATE(), INTERVAL 1 DAY)),
('Tomato', 27.0, 'Chennai', DATE_SUB(CURDATE(), INTERVAL 2 DAY)),
('Rice', 25.5, 'Chennai', DATE_SUB(CURDATE(), INTERVAL 2 DAY));

-- Demo government user
INSERT INTO users (name, email, password, role, phone, location, state) VALUES
('Govt Admin', 'govt@agri.com', '$2b$12$demohashedpassword', 'govt', '1800-180-1551', 'New Delhi', 'Delhi');

-- ──────────────────────────────────
-- INDEXES FOR PERFORMANCE
-- ──────────────────────────────────
CREATE INDEX idx_listings_crop ON listings(crop_name);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_transactions_buyer ON transactions(buyer_id);
CREATE INDEX idx_transactions_seller ON transactions(seller_id);
CREATE INDEX idx_price_history_crop ON price_history(crop_name);
CREATE INDEX idx_equipment_status ON equipment(availability_status);
