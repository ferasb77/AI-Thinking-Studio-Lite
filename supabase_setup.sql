-- ============================================================
-- AI Thinking Studio™ Lite — Supabase Setup Script
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

-- ── Row Level Security ───────────────────────────────────────
ALTER TABLE expeditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE expedition_data ENABLE ROW LEVEL SECURITY;

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

-- ============================================================
-- Done. Tables, indexes, RLS policies all created.
-- ============================================================
