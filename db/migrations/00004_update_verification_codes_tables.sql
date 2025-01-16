-- Drop existing verification codes policies
drop policy if exists "Users can view their own verification codes" on verification_codes;

-- New verification codes policies
create policy "Allow select for verification"
    on verification_codes for select
    using (
        -- Allow selecting unverified codes
        (not verified and created_at > now() - interval '1 hour')
        or
        -- Allow users to view their own verified codes
        (verified and user_id = auth.uid())
    );

create policy "Allow insert during registration"
    on verification_codes for insert
    with check (
        -- Ensure email is provided and code is not already verified
        email is not null 
        and not verified
        and expires_at > now()
    );

-- Optional: cleanup policy if you want to allow deletion of expired codes
create policy "Allow delete expired codes"
    on verification_codes for delete
    using (expires_at < now());