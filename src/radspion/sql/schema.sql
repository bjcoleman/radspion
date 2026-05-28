-- Radspion SQLite schema (simplified v2)
-- See docs/design/03-database-schema.md
--
-- Listing rule (V1): each mission exposes exactly one of open | unlock_code | requires_complete.
-- Never combine redeemable unlock codes (mission_unlock_codes) with automatic listing (mission_list_requires).
-- Unlock-code missions omit mission_list_requires; V1/sample also omit mission_complete_requires as the dependent mission_id.

PRAGMA foreign_keys = ON;

BEGIN;

-- ---------------------------------------------------------------------------
-- Users (agents)
-- ---------------------------------------------------------------------------

CREATE TABLE users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    email               TEXT NOT NULL UNIQUE,
    google_subject_id   TEXT NOT NULL UNIQUE,
    display_name        TEXT NOT NULL,
    is_operator         INTEGER NOT NULL DEFAULT 0 CHECK (is_operator IN (0, 1))
);

-- Signup gate: valid code required before first Google OAuth (any Google account).
-- Compare trimmed input to stored code; matching is case-sensitive.
-- Rotate or revoke by UPDATE/DELETE; not tied to groups or missions.
CREATE TABLE registration_access_codes (
    code    TEXT NOT NULL PRIMARY KEY
);

-- ---------------------------------------------------------------------------
-- Groups (roster only)
-- ---------------------------------------------------------------------------

CREATE TABLE groups (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE
);

CREATE TABLE group_members (
    group_id    INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, user_id)
);

-- ---------------------------------------------------------------------------
-- Missions (one group per mission)
-- ---------------------------------------------------------------------------

CREATE TABLE missions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slug            TEXT NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    brief_path      TEXT NOT NULL,
    debrief_path    TEXT NOT NULL,
    group_id        INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    access_rule     TEXT NOT NULL CHECK (access_rule IN ('open', 'unlock_code', 'requires_complete')),
    completion_code TEXT NOT NULL
);

CREATE INDEX idx_missions_group_id ON missions (group_id);

-- Unlock secret when access_rule = unlock_code (1:1)
CREATE TABLE mission_unlock_codes (
    mission_id      INTEGER PRIMARY KEY REFERENCES missions (id) ON DELETE CASCADE,
    unlock_code     TEXT NOT NULL
);

-- Listing: mission appears after required missions are completed
CREATE TABLE mission_list_requires (
    mission_id              INTEGER NOT NULL REFERENCES missions (id) ON DELETE CASCADE,
    required_mission_id     INTEGER NOT NULL REFERENCES missions (id) ON DELETE CASCADE,
    PRIMARY KEY (mission_id, required_mission_id),
    CHECK (mission_id <> required_mission_id)
);

-- Completion: submit completion_code only after required missions are completed
CREATE TABLE mission_complete_requires (
    mission_id              INTEGER NOT NULL REFERENCES missions (id) ON DELETE CASCADE,
    required_mission_id     INTEGER NOT NULL REFERENCES missions (id) ON DELETE CASCADE,
    PRIMARY KEY (mission_id, required_mission_id),
    CHECK (mission_id <> required_mission_id)
);

-- ---------------------------------------------------------------------------
-- Per-agent progress
-- ---------------------------------------------------------------------------

CREATE TABLE agent_mission_status (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    mission_id  INTEGER NOT NULL REFERENCES missions (id) ON DELETE CASCADE,
    status      TEXT NOT NULL CHECK (status IN ('active', 'completed')),
    UNIQUE (user_id, mission_id)
);

CREATE INDEX idx_agent_mission_status_user ON agent_mission_status (user_id);

COMMIT;
