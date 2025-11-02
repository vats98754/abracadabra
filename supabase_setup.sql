-- Supabase Database Setup for Omi Song Recognition
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- song_info table: stores song metadata
CREATE TABLE IF NOT EXISTS song_info (
    artist TEXT,
    album TEXT,
    title TEXT,
    song_id TEXT
);

-- hashes table: stores audio fingerprint hashes
-- IMPORTANT: time_offset must be REAL/DOUBLE PRECISION (not INTEGER)
-- because it stores floating-point time values in seconds (e.g., 1.23456)
CREATE TABLE IF NOT EXISTS hashes (
    fingerprint_hash BIGINT NOT NULL,
    time_offset DOUBLE PRECISION NOT NULL,
    song_id TEXT NOT NULL
);

-- Indexes for fast fingerprint lookup (critical for performance)
CREATE INDEX IF NOT EXISTS idx_fingerprint_hash ON hashes(fingerprint_hash);

-- Grant permissions (if needed for RLS policies)
-- ALTER TABLE song_info ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE hashes ENABLE ROW LEVEL SECURITY;

-- Optional: Create a policy to allow all operations (for service_role key)
-- CREATE POLICY "Allow all for service role" ON song_info FOR ALL USING (true);
-- CREATE POLICY "Allow all for service role" ON hashes FOR ALL USING (true);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Supabase tables created successfully!';
    RAISE NOTICE 'Tables: song_info, hashes';
    RAISE NOTICE 'Index: idx_fingerprint_hash';
END $$;
