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

-- Users policies
CREATE POLICY "Enable insert during registration" ON users
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can view their own data" ON users
    FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE
    USING (auth.uid() = id);

-- Verification codes policies
CREATE POLICY "Allow select for verification" ON verification_codes
    FOR SELECT
    USING (
        (NOT verified AND created_at > now() - interval '1 hour')
        OR (verified AND user_id = auth.uid())
    );

CREATE POLICY "Allow insert during registration" ON verification_codes
    FOR INSERT
    WITH CHECK (
        code IS NOT NULL
        AND type IN ('email', 'phone')
        AND expires_at > now()
    );

-- User sessions policies
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their own sessions" ON user_sessions
    FOR UPDATE
    USING (user_id = auth.uid());

CREATE POLICY "Allow insert own sessions" ON user_sessions
    FOR INSERT
    WITH CHECK (true);

-- Login attempts policies
CREATE POLICY "Enable insert for login attempts" ON login_attempts
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Enable select for rate limiting" ON login_attempts
    FOR SELECT
    USING (true);

-- Refresh tokens policies
CREATE POLICY "Users can view their own tokens" ON refresh_tokens
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Allow insert refresh tokens" ON refresh_tokens
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow update own tokens" ON refresh_tokens
    FOR UPDATE
    USING (user_id = auth.uid());

-- Cleanup policies
CREATE POLICY "Allow delete expired verification codes" ON verification_codes
    FOR DELETE
    USING (expires_at < now());

CREATE POLICY "Allow delete expired sessions" ON user_sessions
    FOR DELETE
    USING (ended_at < now() - interval '30 days');

CREATE POLICY "Allow delete old login attempts" ON login_attempts
    FOR DELETE
    USING (created_at < now() - interval '24 hours');