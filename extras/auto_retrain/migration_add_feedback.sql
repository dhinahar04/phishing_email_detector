-- Database Migration: Add User Feedback Support
-- This adds columns to track user confirmations/corrections of predictions

-- Add user_feedback column to emails table
ALTER TABLE emails
ADD COLUMN user_feedback VARCHAR(20),  -- 'confirmed', 'corrected', NULL
ADD COLUMN user_confirmed_class BOOLEAN,  -- User's confirmed classification
ADD COLUMN feedback_date TIMESTAMP;  -- When feedback was provided

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_emails_user_feedback ON emails(user_feedback);
CREATE INDEX IF NOT EXISTS idx_emails_feedback_date ON emails(feedback_date);

-- Add comment
COMMENT ON COLUMN emails.user_feedback IS 'User feedback status: confirmed (agreed with prediction), corrected (disagreed), NULL (no feedback)';
COMMENT ON COLUMN emails.user_confirmed_class IS 'User-confirmed classification: TRUE=phishing, FALSE=legitimate';
COMMENT ON COLUMN emails.feedback_date IS 'Timestamp when user provided feedback';
