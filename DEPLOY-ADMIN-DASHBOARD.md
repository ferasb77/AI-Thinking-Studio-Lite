# Deploy the Studio Administrator Dashboard

## 1. Update the database

1. Open the existing AI Thinking Studio project in Supabase.
2. Open **SQL Editor** and create a new query.
3. Copy the complete contents of `supabase_admin_dashboard_migration.sql`.
4. Run the query once.
5. Create another query and run the complete contents of
   `supabase_password_change_migration.sql` once.
6. Create a third query and run the complete contents of
   `supabase_profile_onboarding_migration.sql` once.
7. Confirm that all three queries complete without an error.

The migration assigns the Studio Administrator role to
`info@enablemygrowth.com`. It also adds the strict completion rule and the
administrator-only statistics function.

The password migration flags every account created afterward for a mandatory
first-login password change. It also flags existing provisioned accounts that
have never signed in; established users are left unchanged.

The profile migration requires first-time users to provide their full name,
international phone number, and company or organization before entering the
Studio. Established users are not blocked, and every user can later update the
information through **My Profile**.

## 2. Deploy the application

Replace the deployed application with the files from this revised project.
Keep the deployment's existing `.env` values or secrets; they are not included
in this archive.

The changed application files are:

- `app.py`
- `core/auth.py`
- `core/db.py`
- `core/supabase_client.py`

## 3. Refresh administrator access

1. Sign out of AI Thinking Studio.
2. Sign back in as `info@enablemygrowth.com`.
3. Select **Studio Overview** in the sidebar.

Signing in again is required because Supabase places the application role in a
new access token.

## 4. Verify the result

- The administrator can see registered users and aggregate session counts.
- A normal participant cannot see **Studio Overview**.
- **Save Reflection** saves only the reflection.
- **Complete Thinking Session** remains disabled until all five rooms and a
  non-empty final reflection are complete.
- The dashboard contains no session titles, challenge descriptions, room
  outputs, or reflections.
- Create a test participant in Supabase with a temporary password. On first
  login, the participant must see **Create Your Private Password** and must not
  be able to enter the Studio first.
- After changing it, sign in with the new password and confirm that the Studio
  opens the required profile page.
- Complete the full name, international phone number, and organization fields;
  confirm that the Studio opens only after all three are valid.
- Select **Change Password** in the sidebar and verify the voluntary flow.
- Select **My Profile** and verify that profile changes are saved.
- In **Studio Overview**, verify that name, email, phone, company, and session
  counts appear without exposing Thinking Session content.

## Supabase password policy

In **Authentication → Providers → Email**, configure the project to require a
minimum password length of 12 and uppercase, lowercase, numeric, and symbol
characters. The application applies the same rules in its interface; matching
Supabase settings ensures the rule also applies at the authentication service.

## Completion definition

A Thinking Session counts as complete only when all of these fields contain
non-empty data:

1. Mirror Room
2. Human Room
3. Possibility Room
4. Challenge Room
5. Future Room
6. Final Reflection

Existing sessions previously marked complete are rechecked during migration.
Any that do not meet this definition return to **In Progress**.
