# Database Schema Comparison

This document shows how the Supabase PostgreSQL schema exactly matches abracadabra's original SQLite schema.

---

## SQLite Schema (Original)

From `abracadabra/storage.py:27-28`:

```sql
CREATE TABLE IF NOT EXISTS hash (
    hash int,
    offset real,
    song_id text
);

CREATE TABLE IF NOT EXISTS song_info (
    artist text,
    album text,
    title text,
    song_id text
);

CREATE INDEX IF NOT EXISTS idx_hash ON hash (hash);
```

### Data Structure

From `abracadabra/fingerprint.py:139-146`, the fingerprint data structure is:

```python
hashes.append((
    hash_point_pair(anchor, target),  # hash: integer
    anchor[1],                         # time offset: FLOAT (seconds, e.g., 1.23456)
    str(song_id)                       # song_id: string
))
```

---

## Supabase Schema (PostgreSQL)

From `supabase_setup.sql`:

```sql
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    song_id TEXT UNIQUE NOT NULL,
    artist TEXT,
    album TEXT,
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fingerprints (
    id SERIAL PRIMARY KEY,
    hash BIGINT NOT NULL,
    time_offset DOUBLE PRECISION NOT NULL,  -- ✅ CRITICAL: Must be floating-point!
    song_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON fingerprints(hash);
CREATE INDEX IF NOT EXISTS idx_fingerprints_song_id ON fingerprints(song_id);
```

---

## Field Mapping

### Table: `hash` (SQLite) → `fingerprints` (Supabase)

| SQLite Field | SQLite Type | Supabase Field | Supabase Type | Notes |
|--------------|-------------|----------------|---------------|-------|
| `hash` | `int` | `hash` | `BIGINT` | ✅ Match (BIGINT can hold larger integers) |
| `offset` | `real` | `time_offset` | `DOUBLE PRECISION` | ✅ Match (both floating-point) |
| `song_id` | `text` | `song_id` | `TEXT` | ✅ Match |
| - | - | `id` | `SERIAL PRIMARY KEY` | Supabase auto-increment ID |
| - | - | `created_at` | `TIMESTAMP` | Supabase timestamp for tracking |

### Table: `song_info` (SQLite) → `songs` (Supabase)

| SQLite Field | SQLite Type | Supabase Field | Supabase Type | Notes |
|--------------|-------------|----------------|---------------|-------|
| `artist` | `text` | `artist` | `TEXT` | ✅ Match |
| `album` | `text` | `album` | `TEXT` | ✅ Match |
| `title` | `text` | `title` | `TEXT` | ✅ Match |
| `song_id` | `text` | `song_id` | `TEXT UNIQUE NOT NULL` | ✅ Match (with uniqueness constraint) |
| - | - | `id` | `SERIAL PRIMARY KEY` | Supabase auto-increment ID |
| - | - | `created_at` | `TIMESTAMP` | Supabase timestamp for tracking |

---

## Critical Data Type Details

### Why `DOUBLE PRECISION` for `time_offset`?

The time offset values come from the audio spectrogram's time axis. These are **floating-point values** representing seconds, for example:
- `0.0`
- `1.23456`
- `2.71828`
- `12.98765`

If we used `INTEGER`, we would lose all precision and the fingerprint matching algorithm would **completely fail** because:
1. All time offsets would be rounded to whole seconds (0, 1, 2, 3...)
2. The algorithm relies on precise time differences between fingerprint hashes
3. Without decimal precision, different audio clips would generate identical (colliding) fingerprints

### SQLite `real` vs PostgreSQL `DOUBLE PRECISION`

Both are 64-bit floating-point types:
- SQLite `real`: IEEE 754 double-precision floating-point
- PostgreSQL `DOUBLE PRECISION`: IEEE 754 double-precision floating-point

They are functionally equivalent.

---

## Indexes

Both schemas have the same critical index for fast fingerprint lookup:

| SQLite | Supabase |
|--------|----------|
| `CREATE INDEX idx_hash ON hash (hash)` | `CREATE INDEX idx_fingerprints_hash ON fingerprints(hash)` |

This index is **critical for performance**. Without it, fingerprint matching would require full table scans and be extremely slow.

The Supabase schema adds an additional index:
- `idx_fingerprints_song_id`: Speeds up deletion and lookup by song

---

## Additional Supabase Features

The Supabase schema includes some PostgreSQL-specific enhancements:

1. **Primary Keys**: Auto-incrementing `id` field for each row
2. **Foreign Key Constraint**: Ensures referential integrity between `fingerprints` and `songs`
3. **Timestamps**: Tracks when records were created
4. **Unique Constraint**: Prevents duplicate `song_id` entries
5. **Cascading Delete**: When a song is deleted, all its fingerprints are automatically deleted

These features don't change the core functionality but provide better data integrity and tracking.

---

## Summary

✅ **The schemas are fully compatible!**

The Supabase schema correctly replicates abracadabra's SQLite structure with:
- Correct field types (especially `DOUBLE PRECISION` for time offsets)
- Same data organization
- Same indexing strategy
- Additional PostgreSQL features for data integrity

The fingerprint matching algorithm will work identically on both databases.
