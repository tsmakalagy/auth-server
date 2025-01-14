-- Enable RLS
alter table users enable row level security;
alter table verification_codes enable row level security;
alter table user_sessions enable row level security;
alter table login_attempts enable row level security;

-- Users policies
create policy "Users can view their own data"
    on users for select
    using (auth.uid() = id);

-- Verification codes policies
create policy "Users can view their own verification codes"
    on verification_codes for select
    using (user_id = auth.uid());

create policy "Allow insert for anyone"
    on verification_codes for insert
    with check (true);

-- Sessions policies
create policy "Users can view their own sessions"
    on user_sessions for select
    using (user_id = auth.uid());

create policy "Users can update their own sessions"
    on user_sessions for update
    using (user_id = auth.uid());

-- Login attempts policies
create policy "Allow insert for anyone"
    on login_attempts for insert
    with check (true);