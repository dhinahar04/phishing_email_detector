-- Phishing Email Detection System - Database Schema

-- Emails table
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    is_phishing BOOLEAN,
    confidence_score FLOAT,
    sender VARCHAR(255),
    subject TEXT,
    body TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IOCs (Indicators of Compromise) table
CREATE TABLE IF NOT EXISTS iocs (
    id SERIAL PRIMARY KEY,
    email_id INTEGER REFERENCES emails(id) ON DELETE CASCADE,
    ioc_type VARCHAR(50) NOT NULL,
    ioc_value TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'low',
    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis logs table
CREATE TABLE IF NOT EXISTS analysis_logs (
    id SERIAL PRIMARY KEY,
    email_id INTEGER REFERENCES emails(id) ON DELETE CASCADE,
    analysis_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_end TIMESTAMP,
    status VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    email_id INTEGER REFERENCES emails(id) ON DELETE CASCADE,
    predicted_class VARCHAR(50),
    probability FLOAT,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status);
CREATE INDEX IF NOT EXISTS idx_emails_upload_date ON emails(upload_date);
CREATE INDEX IF NOT EXISTS idx_iocs_email_id ON iocs(email_id);
CREATE INDEX IF NOT EXISTS idx_iocs_type ON iocs(ioc_type);
CREATE INDEX IF NOT EXISTS idx_iocs_value ON iocs(ioc_value);
