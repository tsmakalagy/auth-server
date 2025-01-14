-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Users table
create table users (
    id uuid default uuid_generate_v4() primary key,
    email text unique,
    phone_number text unique,
    name text,
    auth_type text not null check (auth_type in ('email', 'phone')),
    email_verified boolean default false,
    phone_verified boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Verification codes
create table verification_codes (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references users(id),
    email text,
    phone text,
    code text not null,
    type text not null check (type in ('email', 'phone')),
    verified boolean default false,
    expires_at timestamp with time zone not null,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- User sessions
create table user_sessions (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references users(id) not null,
    device_info jsonb,
    is_active boolean default true,
    last_activity timestamp with time zone,
    started_at timestamp with time zone default timezone('utc'::text, now()),
    ended_at timestamp with time zone
);

-- Login attempts for rate limiting
create table login_attempts (
    id uuid default uuid_generate_v4() primary key,
    identifier text not null, -- email or phone
    ip_address text not null,
    success boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Function to update updated_at column
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql;

-- Trigger for users table
create trigger update_users_updated_at
    before update on users
    for each row
    execute function update_updated_at_column();