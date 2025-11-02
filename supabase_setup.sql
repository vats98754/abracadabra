-- Supabase Database Setup for Omi Song Recognition
-- Run this SQL in your Supabase SQL Editor to create the required tables
--
-- This schema matches abracadabra's SQLite structure:
--   SQLite "hash" table → Supabase "fingerprints" table
--   SQLite "song_info" table → Supabase "songs" table

-- Songs table: stores song metadata (matches song_info table)
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    song_id TEXT UNIQUE NOT NULL,
    artist TEXT,
    album TEXT,
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Fingerprints table: stores audio fingerprint hashes (matches hash table)
-- IMPORTANT: time_offset must be REAL/DOUBLE PRECISION (not INTEGER)
-- because it stores floating-point time values in seconds (e.g., 1.23456)
CREATE TABLE IF NOT EXISTS fingerprints (
    id SERIAL PRIMARY KEY,
    hash BIGINT NOT NULL,
    time_offset DOUBLE PRECISION NOT NULL,
    song_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

-- Indexes for fast fingerprint lookup (critical for performance)
CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON fingerprints(hash);
CREATE INDEX IF NOT EXISTS idx_fingerprints_song_id ON fingerprints(song_id);

-- Grant permissions (if needed for RLS policies)
-- ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE fingerprints ENABLE ROW LEVEL SECURITY;

-- Optional: Create a policy to allow all operations (for service_role key)
-- CREATE POLICY "Allow all for service role" ON songs FOR ALL USING (true);
-- CREATE POLICY "Allow all for service role" ON fingerprints FOR ALL USING (true);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Supabase tables created successfully!';
    RAISE NOTICE 'Tables: songs, fingerprints';
    RAISE NOTICE 'Indexes: idx_fingerprints_hash, idx_fingerprints_song_id';
END $$;
