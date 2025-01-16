-- Update verification_codes table if needed
alter table verification_codes 
add column if not exists name text,
add column if not exists verified_at timestamptz,