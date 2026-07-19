# Deploy the Studio Administrator Dashboard

## 1. Update the database

1. Open the existing AI Thinking Studio project in Supabase.
2. Open **SQL Editor** and create a new query.
3. Copy the complete contents of `supabase_admin_dashboard_migration.sql`.
4. Run the query once.
5. Confirm that the query completes without an error.

The migration assigns the Studio Administrator role to
`info@enablemygrowth.com`. It also adds the strict completion rule and the
administrator-only statistics function.

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
