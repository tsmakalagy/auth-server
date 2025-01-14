## Migrations

Migrations are numbered SQL files that should be run in order:

1. `00001_create_base_tables.sql` - Creates initial tables
2. `00002_create_policies.sql` - Sets up RLS policies

## How to Apply

1. Go to Supabase Dashboard
2. Go to SQL Editor
3. Copy and paste each migration file in order
4. Run each script

## Tables

### users
- Main users table
- Stores basic user information
- Supports both email and phone authentication

### verification_codes
- Stores OTP codes for verification
- Handles both email and phone verification
- Includes expiry timing

### user_sessions
- Tracks user login sessions
- Stores device information
- Manages session lifecycle

### login_attempts
- Tracks authentication attempts
- Used for rate limiting
- Stores IP addresses for security

## Security

- Row Level Security (RLS) is enabled on all tables
- Policies ensure users can only access their own data
- Authentication is handled through Supabase Auth

## Database Setup

The project uses Supabase as its database. To set up the database:

1. Create a new Supabase project
2. Copy your project URL and anon/public key
3. Create a `.env` file with:
   ```env
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key