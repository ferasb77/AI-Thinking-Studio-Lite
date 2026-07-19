-- AI Thinking Studio - required first-login profile onboarding
-- Run once after the password-change migration.

CREATE TABLE IF NOT EXISTS public.profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    phone_number TEXT,
    company_name TEXT,
    profile_completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT profiles_full_name_valid CHECK (
        full_name IS NULL OR LENGTH(BTRIM(full_name)) >= 2
    ),
    CONSTRAINT profiles_phone_valid CHECK (
        phone_number IS NULL OR phone_number ~ '^\+[1-9][0-9]{7,14}$'
    ),
    CONSTRAINT profiles_company_valid CHECK (
        company_name IS NULL OR LENGTH(BTRIM(company_name)) >= 2
    )
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "users_read_own_profile" ON public.profiles;
DROP POLICY IF EXISTS "users_create_own_profile" ON public.profiles;
DROP POLICY IF EXISTS "users_update_own_profile" ON public.profiles;

CREATE POLICY "users_read_own_profile"
ON public.profiles
FOR SELECT
TO authenticated
USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "users_create_own_profile"
ON public.profiles
FOR INSERT
TO authenticated
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "users_update_own_profile"
ON public.profiles
FOR UPDATE
TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);

REVOKE ALL ON TABLE public.profiles FROM anon;
REVOKE DELETE ON TABLE public.profiles FROM authenticated;
GRANT SELECT, INSERT, UPDATE ON TABLE public.profiles TO authenticated;

CREATE OR REPLACE FUNCTION public.set_profile_completion()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
    NEW.full_name = BTRIM(NEW.full_name);
    NEW.phone_number = BTRIM(NEW.phone_number);
    NEW.company_name = BTRIM(NEW.company_name);
    NEW.updated_at = NOW();

    IF NULLIF(NEW.full_name, '') IS NOT NULL
       AND NULLIF(NEW.phone_number, '') IS NOT NULL
       AND NULLIF(NEW.company_name, '') IS NOT NULL THEN
        IF TG_OP = 'INSERT' THEN
            NEW.profile_completed_at = COALESCE(
                NEW.profile_completed_at,
                NOW()
            );
        ELSE
            NEW.profile_completed_at = COALESCE(
                NEW.profile_completed_at,
                OLD.profile_completed_at,
                NOW()
            );
        END IF;
    ELSE
        NEW.profile_completed_at = NULL;
    END IF;

    RETURN NEW;
END;
$$;

-- Existing users who have already signed in are not blocked. Existing users
-- who have never signed in must complete any missing profile information.
INSERT INTO public.profiles (
    user_id,
    full_name,
    phone_number,
    company_name,
    profile_completed_at
)
SELECT
    users.id,
    NULLIF(BTRIM(users.raw_user_meta_data ->> 'full_name'), ''),
    NULLIF(BTRIM(users.raw_user_meta_data ->> 'phone_number'), ''),
    NULLIF(BTRIM(users.raw_user_meta_data ->> 'company_name'), ''),
    CASE
        WHEN users.last_sign_in_at IS NOT NULL
             OR users.email = 'info@enablemygrowth.com'
        THEN NOW()
        ELSE NULL
    END
FROM auth.users AS users
ON CONFLICT (user_id) DO NOTHING;

DROP TRIGGER IF EXISTS validate_profile_completion ON public.profiles;

CREATE TRIGGER validate_profile_completion
    BEFORE INSERT OR UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.set_profile_completion();

CREATE OR REPLACE FUNCTION public.handle_new_user_profile()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.profiles (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.handle_new_user_profile() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.handle_new_user_profile()
FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user_profile()
TO supabase_auth_admin;

DROP TRIGGER IF EXISTS create_user_profile ON auth.users;

CREATE TRIGGER create_user_profile
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_profile();

-- Extend the administrator overview with the profile fields. Thinking Session
-- titles and content remain excluded.
DROP FUNCTION IF EXISTS public.get_user_session_stats();

CREATE FUNCTION public.get_user_session_stats()
RETURNS TABLE (
    user_id UUID,
    email TEXT,
    full_name TEXT,
    phone_number TEXT,
    company_name TEXT,
    total_sessions BIGINT,
    completed_sessions BIGINT,
    in_progress_sessions BIGINT,
    last_completed_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    IF COALESCE(
        auth.jwt() -> 'app_metadata' ->> 'studio_role',
        ''
    ) <> 'admin' THEN
        RAISE EXCEPTION 'Studio Administrator access is required'
            USING ERRCODE = '42501';
    END IF;

    RETURN QUERY
    SELECT
        users.id,
        users.email::TEXT,
        profiles.full_name,
        profiles.phone_number,
        profiles.company_name,
        COUNT(expeditions.id),
        COUNT(expeditions.id) FILTER (
            WHERE expeditions.status = 'complete'
        ),
        COUNT(expeditions.id) FILTER (
            WHERE expeditions.status = 'in_progress'
        ),
        MAX(expeditions.completed_at)
    FROM auth.users AS users
    LEFT JOIN public.profiles AS profiles
        ON profiles.user_id = users.id
    LEFT JOIN public.expeditions AS expeditions
        ON expeditions.user_id = users.id
    GROUP BY
        users.id,
        users.email,
        profiles.full_name,
        profiles.phone_number,
        profiles.company_name
    ORDER BY users.email;
END;
$$;

REVOKE ALL ON FUNCTION public.get_user_session_stats() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_user_session_stats() FROM anon;
GRANT EXECUTE ON FUNCTION public.get_user_session_stats() TO authenticated;
