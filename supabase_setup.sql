-- ============================================================
-- AI Thinking Studio™ — Workshop Edition — Supabase Setup Script
-- Run this once in your Supabase SQL Editor
-- Project: https://etzizmgdgjgvigncbijq.supabase.co
-- ============================================================

-- ── Table: expeditions ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS expeditions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL DEFAULT 'Untitled Expedition',
    status      TEXT NOT NULL DEFAULT 'in_progress'
                    CHECK (status IN ('in_progress', 'complete')),
    completed_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Table: expedition_data ───────────────────────────────────
-- Stores all room outputs and setup data as key/value pairs.
-- value is JSONB to support both strings and structured data.
CREATE TABLE IF NOT EXISTS expedition_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expedition_id   UUID NOT NULL REFERENCES expeditions(id) ON DELETE CASCADE,
    key             TEXT NOT NULL,
    value           JSONB,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (expedition_id, key)
);

-- ── Table: user_security_state ─────────────────────────────
-- Newly provisioned accounts must replace their temporary password before
-- entering the Studio. Passwords themselves remain exclusively in Auth.
CREATE TABLE IF NOT EXISTS user_security_state (
    user_id                 UUID PRIMARY KEY
                                REFERENCES auth.users(id) ON DELETE CASCADE,
    must_change_password    BOOLEAN NOT NULL DEFAULT TRUE,
    password_changed_at     TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_expeditions_user_id
    ON expeditions(user_id);

CREATE INDEX IF NOT EXISTS idx_expedition_data_expedition_id
    ON expedition_data(expedition_id);

-- ── Updated_at trigger ───────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER expeditions_updated_at
    BEFORE UPDATE ON expeditions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER expedition_data_updated_at
    BEFORE UPDATE ON expedition_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- A session can become complete only after all five rooms and the final
-- reflection contain non-empty participant data.
CREATE OR REPLACE FUNCTION enforce_expedition_completion()
RETURNS TRIGGER AS $$
DECLARE
    required_key TEXT;
BEGIN
    IF NEW.status = 'complete' AND OLD.status IS DISTINCT FROM 'complete' THEN
        FOREACH required_key IN ARRAY ARRAY[
            'mirror_output',
            'human_output',
            'possibility_output',
            'battlefield_output',
            'future_output',
            'final_reflection'
        ]
        LOOP
            IF NOT EXISTS (
                SELECT 1
                FROM public.expedition_data AS data
                WHERE data.expedition_id = NEW.id
                  AND data.key = required_key
                  AND NULLIF(BTRIM(data.value #>> '{}'), '') IS NOT NULL
            ) THEN
                RAISE EXCEPTION 'Thinking Session is not ready for completion';
            END IF;
        END LOOP;
        NEW.completed_at = NOW();
    ELSIF NEW.status = 'in_progress' THEN
        NEW.completed_at = NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = '';

CREATE TRIGGER validate_expedition_completion
    BEFORE UPDATE OF status ON expeditions
    FOR EACH ROW EXECUTE FUNCTION enforce_expedition_completion();

-- ── Row Level Security ───────────────────────────────────────
ALTER TABLE expeditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE expedition_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_security_state ENABLE ROW LEVEL SECURITY;

-- Users can only see and modify their own expeditions
CREATE POLICY "users_own_expeditions" ON expeditions
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can only see and modify data belonging to their expeditions
CREATE POLICY "users_own_expedition_data" ON expedition_data
    FOR ALL
    USING (
        expedition_id IN (
            SELECT id FROM expeditions WHERE user_id = auth.uid()
        )
    )
    WITH CHECK (
        expedition_id IN (
            SELECT id FROM expeditions WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "users_read_own_security_state" ON user_security_state
    FOR SELECT
    TO authenticated
    USING ((SELECT auth.uid()) = user_id);

REVOKE ALL ON TABLE user_security_state FROM anon;
REVOKE INSERT, UPDATE, DELETE ON TABLE user_security_state FROM authenticated;
GRANT SELECT ON TABLE user_security_state TO authenticated;

-- Existing accounts that have never signed in remain subject to the first-login
-- password change. Established accounts retain their current passwords.
INSERT INTO user_security_state (
    user_id,
    must_change_password,
    password_changed_at
)
SELECT
    id,
    CASE
        WHEN last_sign_in_at IS NULL
             AND email <> 'info@enablemygrowth.com'
        THEN TRUE
        ELSE FALSE
    END,
    CASE WHEN last_sign_in_at IS NULL THEN NULL ELSE NOW() END
FROM auth.users
ON CONFLICT (user_id) DO NOTHING;

CREATE OR REPLACE FUNCTION handle_new_user_security_state()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.user_security_state (user_id, must_change_password)
    VALUES (NEW.id, TRUE)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION handle_new_user_security_state() FROM PUBLIC;
REVOKE ALL ON FUNCTION handle_new_user_security_state()
FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION handle_new_user_security_state()
TO supabase_auth_admin;

CREATE TRIGGER create_user_security_state
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user_security_state();

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
    SET must_change_password = FALSE,
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

-- Administrator-only aggregate reporting. The function exposes counts and
-- account emails, never Thinking Session titles or participant content.
CREATE OR REPLACE FUNCTION public.get_user_session_stats()
RETURNS TABLE (
    user_id UUID,
    email TEXT,
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
        COUNT(expeditions.id),
        COUNT(expeditions.id) FILTER (
            WHERE expeditions.status = 'complete'
        ),
        COUNT(expeditions.id) FILTER (
            WHERE expeditions.status = 'in_progress'
        ),
        MAX(expeditions.completed_at)
    FROM auth.users AS users
    LEFT JOIN public.expeditions AS expeditions
        ON expeditions.user_id = users.id
    GROUP BY users.id, users.email
    ORDER BY users.email;
END;
$$;

REVOKE EXECUTE ON FUNCTION public.get_user_session_stats() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.get_user_session_stats() TO authenticated;

-- Initial Studio Administrator.
UPDATE auth.users
SET raw_app_meta_data = COALESCE(raw_app_meta_data, '{}'::JSONB)
    || '{"studio_role":"admin"}'::JSONB
WHERE email = 'info@enablemygrowth.com';

-- ============================================================
-- Done. Tables, indexes, RLS policies all created.
-- ============================================================
