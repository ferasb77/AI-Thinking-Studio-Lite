-- AI Thinking Studio - Studio Administrator dashboard migration
-- Run once in the existing project's Supabase SQL Editor.

ALTER TABLE public.expeditions
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

-- Preserve only existing completions that satisfy the new strict definition.
UPDATE public.expeditions AS expedition
SET status = 'in_progress'
WHERE expedition.status = 'complete'
  AND EXISTS (
      SELECT 1
      FROM unnest(ARRAY[
          'mirror_output',
          'human_output',
          'possibility_output',
          'battlefield_output',
          'future_output',
          'final_reflection'
      ]) AS required(key)
      WHERE NOT EXISTS (
          SELECT 1
          FROM public.expedition_data AS data
          WHERE data.expedition_id = expedition.id
            AND data.key = required.key
            AND NULLIF(BTRIM(data.value #>> '{}'), '') IS NOT NULL
      )
  );

UPDATE public.expeditions
SET completed_at = updated_at
WHERE status = 'complete'
  AND completed_at IS NULL;

CREATE OR REPLACE FUNCTION public.enforce_expedition_completion()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = ''
AS $$
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
$$;

DROP TRIGGER IF EXISTS validate_expedition_completion
ON public.expeditions;

CREATE TRIGGER validate_expedition_completion
    BEFORE UPDATE OF status ON public.expeditions
    FOR EACH ROW
    EXECUTE FUNCTION public.enforce_expedition_completion();

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

REVOKE ALL ON FUNCTION public.get_user_session_stats() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_user_session_stats() FROM anon;
GRANT EXECUTE ON FUNCTION public.get_user_session_stats() TO authenticated;

UPDATE auth.users
SET raw_app_meta_data = COALESCE(raw_app_meta_data, '{}'::JSONB)
    || '{"studio_role":"admin"}'::JSONB
WHERE email = 'info@enablemygrowth.com';
