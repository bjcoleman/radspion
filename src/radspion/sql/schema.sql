-- Radspion SQLite schema (simplified v2)
-- See docs/design/03-database-schema.md
--
-- Listing rule (V1): each mission exposes exactly one of open | clearance_code | requires_complete.
-- Never combine clearance codes (mission_clearance_codes) with automatic listing (mission_list_requires).

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

-- ---------------------------------------------------------------------------
-- Groups (story arcs — organization only, not access control)
-- ---------------------------------------------------------------------------

CREATE TABLE groups (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------------
-- Missions (one story-arc group per mission)
-- ---------------------------------------------------------------------------

CREATE TABLE missions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slug              TEXT NOT NULL UNIQUE,
    title             TEXT NOT NULL,
    brief_markdown    TEXT NOT NULL,
    debrief_markdown  TEXT NOT NULL,
    group_id          INTEGER NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    access_rule     TEXT NOT NULL CHECK (access_rule IN ('open', 'clearance_code', 'requires_complete')),
    completion_code TEXT NOT NULL
);

CREATE INDEX idx_missions_group_id ON missions (group_id);

-- Clearance code when access_rule = clearance_code (one row per mission; values may repeat)
CREATE TABLE mission_clearance_codes (
    mission_id      INTEGER PRIMARY KEY REFERENCES missions (id) ON DELETE CASCADE,
    clearance_code  TEXT NOT NULL
);

-- Listing: mission appears after required missions are completed
CREATE TABLE mission_list_requires (
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
