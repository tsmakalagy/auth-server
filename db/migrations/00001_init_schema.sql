-- 000001_init_schema.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    email text UNIQUE,
    phone_number text UNIQUE,
    name text,
    auth_type text NOT NULL DEFAULT 'email' CHECK (auth_type IN ('email', 'phone')),
    email_verified boolean DEFAULT false,
    phone_verified boolean DEFAULT false,
    created_at timestamptz DEFAULT timezone('utc'::text, now()),
    updated_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- Verification codes table
CREATE TABLE verification_codes (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id),
    email text,
    phone text,
    code text NOT NULL,
    type text NOT NULL CHECK (type IN ('email', 'phone')),
    name text, -- Store name during registration
    verified boolean DEFAULT false,
    verified_at timestamptz,
    expires_at timestamptz NOT NULL,
    created_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- User sessions table
CREATE TABLE user_sessions (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) NOT NULL,
    device_info jsonb,
    is_active boolean DEFAULT true,
    last_activity timestamptz,
    started_at timestamptz DEFAULT timezone('utc'::text, now()),
    ended_at timestamptz
);

-- Login attempts table
CREATE TABLE login_attempts (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    identifier text NOT NULL, -- email or phone
    ip_address text NOT NULL,
    success boolean DEFAULT false,
    attempt_type text DEFAULT 'email' CHECK (attempt_type IN ('email', 'phone')),
    created_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) NOT NULL,
    token text NOT NULL,
    is_revoked boolean DEFAULT false,
    expires_at timestamptz NOT NULL,
    created_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- First, drop all existing policies
DO $$ 
BEGIN
  -- login_attempts
  DROP POLICY IF EXISTS "Allow cleanup of old attempts" ON login_attempts;
  DROP POLICY IF EXISTS "Allow delete old login attempts" ON login_attempts;
  DROP POLICY IF EXISTS "anon_insert_login_attempts" ON login_attempts;
  DROP POLICY IF EXISTS "anon_select_login_attempts" ON login_attempts;

  -- refresh_tokens
  DROP POLICY IF EXISTS "Allow insert refresh tokens" ON refresh_tokens;
  DROP POLICY IF EXISTS "Allow update own tokens" ON refresh_tokens;
  DROP POLICY IF EXISTS "Users can view their own tokens" ON refresh_tokens;

  -- user_sessions
  DROP POLICY IF EXISTS "Allow delete expired sessions" ON user_sessions;
  DROP POLICY IF EXISTS "Allow insert own sessions" ON user_sessions;
  DROP POLICY IF EXISTS "anon_insert_sessions" ON user_sessions;
  DROP POLICY IF EXISTS "Users can update their own sessions" ON user_sessions;
  DROP POLICY IF EXISTS "Users can view their own sessions" ON user_sessions;

  -- users
  DROP POLICY IF EXISTS "Allow anonymous insert" ON users;
  DROP POLICY IF EXISTS "Allow authenticated update" ON users;
  DROP POLICY IF EXISTS "anon_select_users" ON users;

  -- verification_codes
  DROP POLICY IF EXISTS "Allow delete expired verification codes" ON verification_codes;
  DROP POLICY IF EXISTS "Allow insert during registration" ON verification_codes;
  DROP POLICY IF EXISTS "anon_update_codes" ON verification_codes;
  DROP POLICY IF EXISTS "anon_verify_codes" ON verification_codes;
END $$;

-- Create new standardized policies

-- Login Attempts policies
CREATE POLICY "login_attempts_all_access" ON login_attempts
    FOR ALL 
    TO authenticated, anon
    USING (true)
    WITH CHECK (true);

-- Refresh Tokens policies
CREATE POLICY "refresh_tokens_all_access" ON refresh_tokens
    FOR ALL
    TO authenticated, anon
    USING (true)
    WITH CHECK (true);

-- User Sessions policies
CREATE POLICY "user_sessions_all_access" ON user_sessions
    FOR ALL
    TO authenticated, anon
    USING (true)
    WITH CHECK (true);

-- Users policies
CREATE POLICY "users_all_access" ON users
    FOR ALL
    TO authenticated, anon
    USING (true)
    WITH CHECK (true);

-- Verification Codes policies
CREATE POLICY "verification_codes_all_access" ON verification_codes
    FOR ALL
    TO authenticated, anon
    USING (true)
    WITH CHECK (true);

-- Grant necessary permissions to anon role
GRANT ALL ON login_attempts TO anon;
GRANT ALL ON refresh_tokens TO anon;
GRANT ALL ON user_sessions TO anon;
GRANT ALL ON users TO anon;
GRANT ALL ON verification_codes TO anon;

-- Enable RLS on all tables
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_codes ENABLE ROW LEVEL SECURITY;