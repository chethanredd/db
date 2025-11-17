-- ===============================================
-- DATABASE AND SCHEMA SETUP
-- ===============================================

CREATE DATABASE IF NOT EXISTS shopscaledb;
USE shopscaledb;

-- ===============================================
-- TABLE CREATION (DDL)
-- ===============================================

-- 1. ADDRESSES Table
CREATE TABLE IF NOT EXISTS addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    address_type ENUM('shipping', 'billing', 'both') NOT NULL DEFAULT 'both',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_postal_code (postal_code)
);

-- 2. CUSTOMERS Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    date_of_birth DATE,
    gender ENUM('M', 'F', 'Other') DEFAULT 'Other',
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    shipping_address_id INT,
    billing_address_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL,
    FOREIGN KEY (billing_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phone_number),
    INDEX idx_registration_date (registration_date)
);

-- 3. CATEGORIES Table
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    INDEX idx_category_name (category_name),
    INDEX idx_parent_category (parent_category_id)
);

-- 4. PRODUCTS Table (UPDATED WITH IMAGE COLUMN)
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    cost_price DECIMAL(10, 2) CHECK (cost_price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    sku VARCHAR(100) UNIQUE NOT NULL,
    brand VARCHAR(100),
    weight DECIMAL(8, 2),
    dimensions VARCHAR(100),
    color VARCHAR(50),
    size VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,
    image VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_name (product_name),
    INDEX idx_sku (sku),
    INDEX idx_brand (brand),
    INDEX idx_price (price),
    INDEX idx_stock_quantity (stock_quantity),
    INDEX idx_featured (featured)
);

-- 5. PRODUCT_CATEGORIES Junction Table
CREATE TABLE IF NOT EXISTS product_categories (
    product_id INT,
    category_id INT,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- 6. SHOPPING_CART Table
CREATE TABLE IF NOT EXISTS shopping_cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    UNIQUE KEY unique_customer_cart (customer_id),
    INDEX idx_customer_id (customer_id)
);

-- 7. CART_ITEMS Table
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES shopping_cart(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_product (cart_id, product_id),
    INDEX idx_cart_id (cart_id),
    INDEX idx_product_id (product_id)
);

-- 8. ORDERS Table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'returned') DEFAULT 'pending',
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    shipping_amount DECIMAL(8, 2) DEFAULT 0.00,
    tax_amount DECIMAL(8, 2) DEFAULT 0.00,
    discount_amount DECIMAL(8, 2) DEFAULT 0.00,
    shipping_address_id INT,
    billing_address_id INT,
    tracking_number VARCHAR(100),
    estimated_delivery DATE,
    actual_delivery_date TIMESTAMP NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL,
    FOREIGN KEY (billing_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL,
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date),
    INDEX idx_order_status (order_status),
    INDEX idx_total_amount (total_amount)
);

-- 9. ORDER_ITEMS Table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(12, 2) NOT NULL CHECK (total_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);

-- 10. PAYMENTS Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method ENUM('credit_card', 'debit_card', 'upi', 'net_banking', 'wallet', 'cod') NOT NULL,
    payment_status ENUM('pending', 'processing', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    payment_amount DECIMAL(12, 2) NOT NULL CHECK (payment_amount >= 0),
    transaction_id VARCHAR(100) UNIQUE,
    payment_gateway VARCHAR(50),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    refund_amount DECIMAL(12, 2) DEFAULT 0.00,
    refund_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_payment_status (payment_status),
    INDEX idx_payment_date (payment_date),
    INDEX idx_transaction_id (transaction_id)
);

-- 11. REVIEWS Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_id INT,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(255),
    review_text TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    UNIQUE KEY unique_customer_product_review (customer_id, product_id, order_id),
    INDEX idx_product_id (product_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_rating (rating),
    INDEX idx_review_date (review_date)
);

-- ===============================================
-- DATA INSERTION (DML)
-- ===============================================

-- Sample addresses
INSERT IGNORE INTO addresses (street_address, city, state, postal_code, country, address_type) VALUES
('123 MG Road', 'Bengaluru', 'Karnataka', '560001', 'India', 'both'),
('456 Brigade Road', 'Bengaluru', 'Karnataka', '560025', 'India', 'shipping'),
('789 Koramangala', 'Bengaluru', 'Karnataka', '560034', 'India', 'billing'),
('321 Whitefield', 'Bengaluru', 'Karnataka', '560066', 'India', 'both'),
('654 Jayanagar', 'Bengaluru', 'Karnataka', '560011', 'India', 'both'),
('987 HSR Layout', 'Bengaluru', 'Karnataka', '560102', 'India', 'shipping'),
('147 Indiranagar', 'Bengaluru', 'Karnataka', '560038', 'India', 'both'),
('258 Malleshwaram', 'Bengaluru', 'Karnataka', '560003', 'India', 'billing'),
('369 Electronic City', 'Bengaluru', 'Karnataka', '560100', 'India', 'both'),
('741 Rajajinagar', 'Bengaluru', 'Karnataka', '560010', 'India', 'shipping');

-- Sample customers (with bcrypt hashed passwords - password is "password123" for all)
INSERT IGNORE INTO customers (first_name, last_name, email, password_hash, phone_number, date_of_birth, gender, shipping_address_id, billing_address_id) VALUES
('Rajesh', 'Kumar', 'rajesh.kumar@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543210', '1990-05-15', 'M', 1, 1),
('Priya', 'Sharma', 'priya.sharma@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543211', '1992-08-22', 'F', 2, 3),
('Amit', 'Singh', 'amit.singh@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543212', '1988-12-10', 'M', 4, 4),
('Sneha', 'Patel', 'sneha.patel@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543213', '1995-03-18', 'F', 5, 5),
('Vikram', 'Reddy', 'vikram.reddy@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543214', '1987-11-25', 'M', 6, 1),
('Anjali', 'Gupta', 'anjali.gupta@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543215', '1993-07-30', 'F', 7, 8),
('Rohit', 'Verma', 'rohit.verma@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543216', '1991-09-12', 'M', 9, 9),
('Kavya', 'Nair', 'kavya.nair@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543217', '1994-04-08', 'F', 10, 3),
('Arjun', 'Joshi', 'arjun.joshi@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543218', '1989-01-20', 'M', 1, 4),
('Ritu', 'Agarwal', 'ritu.agarwal@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543219', '1996-06-14', 'F', 2, 5);

-- Admin user for admin panel access
INSERT IGNORE INTO customers (first_name, last_name, email, password_hash, phone_number) 
VALUES ('Admin', 'User', 'admin@shopscale.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S', '9876543200');

-- Sample categories
INSERT IGNORE INTO categories (category_name, description, parent_category_id) VALUES
('Electronics', 'Electronic devices and gadgets', NULL),
('Clothing', 'Fashion and apparel', NULL),
('Books', 'Books and literature', NULL),
('Home & Kitchen', 'Home appliances and kitchen items', NULL),
('Sports', 'Sports and fitness equipment', NULL),
('Smartphones', 'Mobile phones and accessories', 1),
('Laptops', 'Laptops and computers', 1),
('Mens Clothing', 'Clothing for men', 2),
('Womens Clothing', 'Clothing for women', 2),
('Fiction Books', 'Fictional literature', 3);

-- Sample products WITH IMAGES
INSERT IGNORE INTO products (product_name, description, price, cost_price, stock_quantity, sku, brand, weight, color, size, featured, image) VALUES
('iPhone 15 Pro', 'Latest iPhone with A17 Pro chip', 129900.00, 100000.00, 50, 'APPLE-IP15-PRO-001', 'Apple', 0.187, 'Natural Titanium', '6.1 inch', TRUE, 'https://images.unsplash.com/photo-1696446702248-474074b6fe58?w=400'),
('Samsung Galaxy S24', 'Flagship Android smartphone', 79999.00, 60000.00, 75, 'SAMSUNG-GS24-001', 'Samsung', 0.168, 'Phantom Black', '6.2 inch', TRUE, 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400'),
('MacBook Air M3', 'Ultra-thin laptop with M3 chip', 114900.00, 90000.00, 30, 'APPLE-MBA-M3-001', 'Apple', 1.24, 'Midnight', '13 inch', TRUE, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400'),
('Dell XPS 13', 'Premium ultrabook', 89999.00, 70000.00, 25, 'DELL-XPS13-001', 'Dell', 1.19, 'Platinum Silver', '13.4 inch', FALSE, 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400'),
('Levis 501 Jeans', 'Classic straight fit jeans', 4999.00, 3000.00, 100, 'LEVIS-501-001', 'Levis', 0.5, 'Dark Blue', '32W x 34L', FALSE, 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'),
('Nike Air Max 270', 'Comfortable running shoes', 12995.00, 8000.00, 80, 'NIKE-AM270-001', 'Nike', 0.8, 'White/Black', 'US 9', TRUE, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
('The Alchemist', 'Bestselling novel by Paulo Coelho', 399.00, 250.00, 200, 'BOOK-ALCH-001', 'HarperCollins', 0.2, 'N/A', 'Paperback', FALSE, 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'),
('Instant Pot Duo', '7-in-1 pressure cooker', 8999.00, 6000.00, 40, 'IP-DUO-001', 'Instant Pot', 5.7, 'Stainless Steel', '6 Quart', FALSE, 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=400'),
('Yoga Mat Premium', 'Non-slip exercise mat', 1499.00, 800.00, 150, 'YOGA-MAT-001', 'Manduka', 2.5, 'Purple', '6ft x 2ft', FALSE, 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400'),
('Wireless Earbuds Pro', 'Noise cancelling earbuds', 15999.00, 10000.00, 60, 'AUDIO-WE-PRO-001', 'Sony', 0.05, 'Black', 'One Size', FALSE, 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400');

-- Product-category relationships
INSERT IGNORE INTO product_categories (product_id, category_id) VALUES
(1, 1), (1, 6),
(2, 1), (2, 6),
(3, 1), (3, 7),
(4, 1), (4, 7),
(5, 2), (5, 8),
(6, 5),
(7, 3), (7, 10),
(8, 4),
(9, 5),
(10, 1);

-- Shopping carts
INSERT IGNORE INTO shopping_cart (customer_id) VALUES
(1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- Cart items
INSERT IGNORE INTO cart_items (cart_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 7, 2),
(2, 5, 1),
(2, 6, 1),
(3, 3, 1),
(4, 2, 1),
(4, 9, 1),
(5, 8, 1),
(6, 10, 2),
(7, 4, 1);

-- Sample orders
INSERT IGNORE INTO orders (customer_id, order_status, total_amount, shipping_amount, tax_amount, discount_amount, shipping_address_id, billing_address_id, tracking_number) VALUES
(1, 'delivered', 130798.00, 0.00, 898.00, 0.00, 1, 1, 'TRK001234567'),
(2, 'shipped', 18494.00, 500.00, 999.00, 0.00, 2, 3, 'TRK001234568'),
(3, 'processing', 114900.00, 0.00, 0.00, 0.00, 4, 4, NULL),
(4, 'confirmed', 81494.00, 500.00, 995.00, 0.00, 5, 5, NULL),
(5, 'delivered', 8999.00, 200.00, 0.00, 0.00, 6, 1, 'TRK001234569'),
(6, 'pending', 31998.00, 0.00, 0.00, 0.00, 7, 8, NULL),
(7, 'cancelled', 89999.00, 0.00, 0.00, 0.00, 9, 9, NULL),
(8, 'delivered', 399.00, 50.00, 0.00, 0.00, 10, 3, 'TRK001234570'),
(9, 'shipped', 12995.00, 300.00, 0.00, 0.00, 1, 4, 'TRK001234571'),
(10, 'processing', 5499.00, 500.00, 0.00, 0.00, 2, 5, NULL);

-- Order items
INSERT IGNORE INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 129900.00, 129900.00),
(2, 5, 1, 4999.00, 4999.00),
(2, 6, 1, 12995.00, 12995.00),
(3, 3, 1, 114900.00, 114900.00),
(4, 2, 1, 79999.00, 79999.00),
(4, 9, 1, 1499.00, 1499.00),
(5, 8, 1, 8999.00, 8999.00),
(6, 10, 2, 15999.00, 31998.00),
(7, 4, 1, 89999.00, 89999.00),
(8, 7, 1, 399.00, 399.00),
(9, 6, 1, 12995.00, 12995.00),
(10, 5, 1, 4999.00, 4999.00);

-- Sample payments
INSERT IGNORE INTO payments (order_id, payment_method, payment_status, payment_amount, transaction_id, payment_gateway) VALUES
(1, 'upi', 'completed', 130798.00, 'UPI123456789', 'PhonePe'),
(2, 'credit_card', 'completed', 18494.00, 'CC987654321', 'Razorpay'),
(3, 'net_banking', 'processing', 114900.00, 'NB456789123', 'Payu'),
(4, 'debit_card', 'completed', 81494.00, 'DC789123456', 'CCAvenue'),
(5, 'cod', 'completed', 8999.00, NULL, NULL),
(6, 'wallet', 'pending', 31998.00, 'WAL321654987', 'Paytm'),
(7, 'credit_card', 'refunded', 89999.00, 'CC654987321', 'Razorpay'),
(8, 'upi', 'completed', 399.00, 'UPI987654123', 'GPay'),
(9, 'debit_card', 'completed', 12995.00, 'DC123987456', 'Stripe'),
(10, 'net_banking', 'processing', 5499.00, 'NB789456123', 'Instamojo');

-- Sample reviews
INSERT IGNORE INTO reviews (product_id, customer_id, order_id, rating, review_title, review_text, is_verified) VALUES
(1, 1, 1, 5, 'Excellent phone!', 'The iPhone 15 Pro is amazing. Great camera and performance.', TRUE),
(5, 2, 2, 4, 'Good quality jeans', 'Comfortable fit and good material. Worth the price.', TRUE),
(6, 2, 2, 5, 'Love these shoes!', 'Super comfortable for running. Highly recommended.', TRUE),
(2, 4, 4, 4, 'Great smartphone', 'Samsung Galaxy S24 has excellent features and camera quality.', TRUE),
(9, 4, 4, 5, 'Perfect yoga mat', 'Non-slip surface is excellent. Great for daily practice.', TRUE),
(8, 5, 5, 5, 'Must-have kitchen appliance', 'Instant Pot is a game changer. Saves so much time cooking.', TRUE),
(7, 8, 8, 5, 'Inspiring read', 'The Alchemist is a beautiful story. Highly recommended.', TRUE),
(6, 9, 9, 4, 'Comfortable running shoes', 'Good cushioning and support. Great for daily workouts.', TRUE),
(3, 3, 3, 5, 'Amazing laptop', 'MacBook Air M3 is incredibly fast and lightweight.', FALSE),
(10, 6, 6, 3, 'Average earbuds', 'Sound quality is okay but expected better noise cancellation.', FALSE);

-- ===============================================
-- ADDITIONAL PERFORMANCE INDEXES (FIXED)
-- ===============================================

-- Remove problematic DROP INDEX statements and just create the indexes
-- If indexes already exist, they will cause errors but won't break the entire script

CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_products_price_stock ON products(price, stock_quantity);
CREATE INDEX idx_order_items_order_product ON order_items(order_id, product_id);
CREATE INDEX idx_reviews_product_rating ON reviews(product_id, rating);
CREATE INDEX idx_customers_email_active ON customers(email, is_active);
CREATE INDEX idx_products_active_featured ON products(is_active, featured);
CREATE INDEX idx_orders_status_date ON orders(order_status, order_date);
CREATE INDEX idx_reviews_product_date_composite ON reviews(product_id, review_date);

-- ===============================================
-- TRIGGERS, FUNCTIONS, AND PROCEDURES (FIXED)
-- ===============================================

-- Drop existing triggers, functions, and procedures
DROP TRIGGER IF EXISTS trg_update_stock_after_order;
DROP TRIGGER IF EXISTS trg_refund_after_order_cancel;
DROP FUNCTION IF EXISTS get_customer_total_spent;
DROP FUNCTION IF EXISTS calculate_order_tax;
DROP PROCEDURE IF EXISTS get_customer_order_summary;
DROP PROCEDURE IF EXISTS generate_sales_report;

-- 1. Stock update trigger
DELIMITER $$

CREATE TRIGGER trg_update_stock_after_order
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END $$

DELIMITER ;

-- 2. Refund trigger (FIXED DELIMITER)
DELIMITER $$

CREATE TRIGGER trg_refund_after_order_cancel
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.order_status = 'cancelled' AND OLD.order_status != 'cancelled' THEN
        -- Check if payment record exists
        IF (SELECT COUNT(*) FROM payments WHERE order_id = NEW.order_id) = 0 THEN
            -- Insert refund record
            INSERT INTO payments (
                order_id, payment_method, payment_status, payment_amount, 
                transaction_id, payment_gateway, refund_amount, refund_date
            ) VALUES (
                NEW.order_id,
                'cod',
                'refunded',
                NEW.total_amount,
                CONCAT('REFUND_', NEW.order_id, '_', UNIX_TIMESTAMP()),
                'System',
                NEW.total_amount,
                NOW()
            );
        ELSE
            -- Update existing payment record
            UPDATE payments 
            SET payment_status = 'refunded',
                refund_amount = NEW.total_amount,
                refund_date = NOW()
            WHERE order_id = NEW.order_id;
        END IF;
    END IF;
END $$

DELIMITER ;

-- 3. Customer total spent function (FIXED DELIMITER)
DELIMITER $$

CREATE FUNCTION get_customer_total_spent(p_customer_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_spent DECIMAL(12,2);
    SELECT IFNULL(SUM(total_amount), 0)
    INTO total_spent
    FROM orders
    WHERE customer_id = p_customer_id
      AND order_status IN ('delivered', 'completed', 'confirmed', 'shipped');
    RETURN total_spent;
END $$

DELIMITER ;

-- 4. Order tax calculation function (FIXED DELIMITER)
DELIMITER $$

CREATE FUNCTION calculate_order_tax(p_order_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_tax DECIMAL(12,2);
    SELECT IFNULL(SUM(oi.unit_price * oi.quantity * 0.18), 0)
    INTO total_tax
    FROM order_items oi
    WHERE oi.order_id = p_order_id;
    RETURN total_tax;
END $$

DELIMITER ;

-- 5. Customer order summary procedure (FIXED DELIMITER)
DELIMITER $$

CREATE PROCEDURE get_customer_order_summary(IN p_customer_id INT)
BEGIN
    SELECT 
        o.order_id,
        o.order_date,
        o.order_status,
        p.product_name,
        oi.quantity,
        oi.unit_price,
        COALESCE(pay.payment_method, 'pending') as payment_method,
        COALESCE(pay.payment_status, 'pending') as payment_status,
        o.total_amount
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN payments pay ON o.order_id = pay.order_id
    WHERE o.customer_id = p_customer_id
    ORDER BY o.order_date DESC;
END $$

DELIMITER ;

-- 6. Sales report procedure (FIXED DELIMITER)
DELIMITER $$

CREATE PROCEDURE generate_sales_report(IN start_date DATE, IN end_date DATE)
BEGIN
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS total_sales,
        COALESCE(SUM(oi.quantity), 0) AS total_items_sold,
        AVG(o.total_amount) as avg_order_value
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_date BETWEEN start_date AND end_date
    AND o.order_status IN ('delivered', 'completed', 'confirmed', 'shipped');
END $$

DELIMITER ;

-- ===============================================
-- VERIFICATION QUERIES
-- ===============================================

-- Test functions and procedures
SELECT 'Testing Database Components...' AS status;

-- Test functions
SELECT get_customer_total_spent(1) AS customer_1_total_spent;
SELECT calculate_order_tax(1) AS order_1_tax;

-- Test procedures
CALL get_customer_order_summary(1);
CALL generate_sales_report('2024-01-01', '2024-12-31');

-- Check triggers
SHOW TRIGGERS;

-- Verify product images and data
SELECT product_id, product_name, price, stock_quantity, featured, image 
FROM products 
ORDER BY product_id;

-- Verify admin user
SELECT customer_id, first_name, last_name, email 
FROM customers 
WHERE email = 'admin@shopscale.com';

SELECT 'Database setup completed successfully!' AS final_status;


USE shopscaledb;

-- Update all passwords to use a working bcrypt hash for "password123"
UPDATE customers SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S' WHERE email = 'admin@shopscale.com';
UPDATE customers SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S' WHERE email = 'rajesh.kumar@email.com';
UPDATE customers SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S' WHERE email = 'priya.sharma@email.com';
UPDATE customers SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S' WHERE email = 'amit.singh@email.com';
UPDATE customers SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8UKZbL7o.S' WHERE email = 'sneha.patel@email.com';

-- Verify the updates
SELECT email, password_hash FROM customers WHERE email IN ('admin@shopscale.com', 'rajesh.kumar@email.com');