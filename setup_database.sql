-- Setup Gaprio Agent Database
CREATE DATABASE IF NOT EXISTS gaprio_agent_dev;
USE gaprio_agent_dev;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User connections table
CREATE TABLE IF NOT EXISTS user_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    provider ENUM('google', 'asana') NOT NULL,
    provider_user_id VARCHAR(255),
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    metadata JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert sample data
INSERT INTO users (email, full_name) VALUES
('test@example.com', 'Test User'),
('admin@example.com', 'Admin User');

INSERT INTO user_connections (user_id, provider, access_token) VALUES
(1, 'asana', 'pat_sample_asana_token'),
(1, 'google', 'sample_google_token');

SELECT '✅ Database setup complete!' as message;