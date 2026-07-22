-- AI Thinking Studio - first-login and voluntary password changes
-- Run once after supabase_admin_dashboard_migration.sql.

CREATE TABLE IF NOT EXISTS public.user_security_state (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    must_change_password BOOLEAN NOT NULL DEFAULT TRUE,
    password_changed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.user_security_state ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "users_read_own_security_state"
ON public.user_security_state;

CREATE POLICY "users_read_own_security_state"
ON public.user_security_state
FOR SELECT
TO authenticated
USING ((SELECT auth.uid()) = user_id);

REVOKE ALL ON TABLE public.user_security_state FROM anon;
REVOKE INSERT, UPDATE, DELETE ON TABLE public.user_security_state
FROM authenticated;
GRANT SELECT ON TABLE public.user_security_state TO authenticated;

-- Existing accounts that have never signed in are still at their first-login
-- point. Established accounts retain their current passwords.
INSERT INTO public.user_security_state (
    user_id,
    must_change_password,
    password_changed_at
)
SELECT
    users.id,
    CASE
        WHEN users.last_sign_in_at IS NULL
             AND users.email <> 'info@enablemygrowth.com'
        THEN TRUE
        ELSE FALSE
    END,
    CASE
        WHEN users.last_sign_in_at IS NULL THEN NULL
        ELSE NOW()
    END
FROM auth.users AS users
ON CONFLICT (user_id) DO NOTHING;

-- Every account provisioned after this migration receives a temporary-password
-- flag automatically.
CREATE OR REPLACE FUNCTION public.handle_new_user_security_state()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.user_security_state (
        user_id,
        must_change_password
    )
    VALUES (NEW.id, TRUE)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.handle_new_user_security_state() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.handle_new_user_security_state()
FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user_security_state()
TO supabase_auth_admin;

DROP TRIGGER IF EXISTS create_user_security_state ON auth.users;

CREATE TRIGGER create_user_security_state
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_security_state();

-- Called only after Supabase Auth has accepted the user's new password.
CREATE OR REPLACE FUNCTION public.complete_my_password_change()
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    IF auth.uid() IS NULL THEN
        RAISE EXCEPTION 'Authentication is required'
            USING ERRCODE = '42501';
    END IF;

    UPDATE public.user_security_state
    SET
        must_change_password = FALSE,
        password_changed_at = NOW()
    WHERE user_id = auth.uid();

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account security state was not found';
    END IF;
END;
$$;

REVOKE ALL ON FUNCTION public.complete_my_password_change() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.complete_my_password_change() FROM anon;
GRANT EXECUTE ON FUNCTION public.complete_my_password_change()
TO authenticated;

-- Invited users choose their permanent password while accepting the
-- invitation, so they must not be required to change it again afterward.
-- Supabase populates invited_at after the initial auth.users insert, which is
-- why this requires a separate AFTER UPDATE trigger.
CREATE OR REPLACE FUNCTION public.handle_user_invited()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    UPDATE public.user_security_state
    SET must_change_password = FALSE
    WHERE user_id = NEW.id
      AND must_change_password = TRUE
      AND password_changed_at IS NULL;

    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.handle_user_invited() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.handle_user_invited() FROM anon;
REVOKE ALL ON FUNCTION public.handle_user_invited() FROM authenticated;

DROP TRIGGER IF EXISTS mark_user_security_state_invited ON auth.users;

CREATE TRIGGER mark_user_security_state_invited
AFTER UPDATE OF invited_at ON auth.users
FOR EACH ROW
WHEN (OLD.invited_at IS NULL AND NEW.invited_at IS NOT NULL)
EXECUTE FUNCTION public.handle_user_invited();

-- Correct invited accounts created before this trigger existed.
UPDATE public.user_security_state AS security_state
SET must_change_password = FALSE
FROM auth.users AS auth_user
WHERE auth_user.id = security_state.user_id
  AND auth_user.invited_at IS NOT NULL
  AND security_state.must_change_password = TRUE
  AND security_state.password_changed_at IS NULL;
