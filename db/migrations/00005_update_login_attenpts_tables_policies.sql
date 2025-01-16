-- First, remove any existing policies on login_attempts
DROP POLICY IF EXISTS "Allow insert for anyone" ON login_attempts;

-- Create new policies for login_attempts
CREATE POLICY "Enable insert for all users" ON login_attempts
    FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Enable select for authenticated users" ON login_attempts
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Add policy for cleanup if needed
CREATE POLICY "Allow delete old attempts" ON login_attempts
    FOR DELETE
    USING (created_at < now() - interval '24 hours');

ALTER TABLE verification_codes 
    ADD COLUMN if not exists attempt_type text DEFAULT 'email'

-- Enable RLS if not already enabled
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;