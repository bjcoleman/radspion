-- Default system seed: Orientation group + basic-training (open mission for all new agents).
-- Prerequisite: src/radspion/sql/schema.sql

PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO groups (id, name) VALUES
    (1, 'Orientation');

INSERT INTO missions (id, slug, title, brief_path, debrief_path, group_id, access_rule, completion_code) VALUES
    (1, 'basic-training', 'Welcome to Radspion',
     'content/missions/basic-training/brief.md', 'content/missions/basic-training/debrief.md',
     1, 'open', 'WELCOME-AGENT-OK');

COMMIT;
