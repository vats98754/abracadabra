-- Supabase Database Setup for Omi Song Recognition
-- Run this SQL in your Supabase SQL Editor to create the required tables
--
-- This schema uses the EXACT same names as abracadabra's SQLite structure

-- song_info table: stores song metadata (EXACT MATCH to SQLite)
CREATE TABLE IF NOT EXISTS song_info (
    artist TEXT,
    album TEXT,
    title TEXT,
    song_id TEXT
);

-- hash table: stores audio fingerprint hashes (EXACT MATCH to SQLite)
-- IMPORTANT: offset must be REAL/DOUBLE PRECISION (not INTEGER)
-- because it stores floating-point time values in seconds (e.g., 1.23456)
CREATE TABLE IF NOT EXISTS hash (
    hash BIGINT NOT NULL,
    offset DOUBLE PRECISION NOT NULL,
    song_id TEXT NOT NULL
);

-- Indexes for fast fingerprint lookup (critical for performance)
CREATE INDEX IF NOT EXISTS idx_hash ON hash(hash);

-- Grant permissions (if needed for RLS policies)
-- ALTER TABLE song_info ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE hash ENABLE ROW LEVEL SECURITY;

-- Optional: Create a policy to allow all operations (for service_role key)
-- CREATE POLICY "Allow all for service role" ON song_info FOR ALL USING (true);
-- CREATE POLICY "Allow all for service role" ON hash FOR ALL USING (true);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Supabase tables created successfully!';
    RAISE NOTICE 'Tables: song_info, hash';
    RAISE NOTICE 'Index: idx_hash';
END $$;
