-- Testing Storyline seed (dev/test only — not for production).
-- Requires schema.sql, seed_orientation.sql.
-- See docs/design/05-testing-storyline.md

PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO groups (name) VALUES ('Testing Storyline');

INSERT INTO users (id, email, google_subject_id, display_name) VALUES
    (1, 'alice@moravian.edu', 'google-alice', 'Alice'),
    (2, 'bob@moravian.edu', 'google-bob', 'Bob'),
    (3, 'charlie@moravian.edu', 'google-charlie', 'Charlie'),
    (4, 'diana@moravian.edu', 'google-diana', 'Diana');

INSERT INTO missions (slug, title, brief_path, debrief_path, group_id, access_rule, completion_code) VALUES
    ('es-alpha', 'ES: Alpha',
     'content/missions/es-alpha/brief.md', 'content/missions/es-alpha/debrief.md',
     (SELECT id FROM groups WHERE name = 'Testing Storyline'),
     'unlock_code', 'COMPLETE es-alpha'),
    ('es-beta', 'ES: Beta',
     'content/missions/es-beta/brief.md', 'content/missions/es-beta/debrief.md',
     (SELECT id FROM groups WHERE name = 'Testing Storyline'),
     'unlock_code', 'COMPLETE es-beta'),
    ('es-hidden', 'ES: Hidden',
     'content/missions/es-hidden/brief.md', 'content/missions/es-hidden/debrief.md',
     (SELECT id FROM groups WHERE name = 'Testing Storyline'),
     'unlock_code', 'COMPLETE es-hidden'),
    ('es-gamma', 'ES: Gamma',
     'content/missions/es-gamma/brief.md', 'content/missions/es-gamma/debrief.md',
     (SELECT id FROM groups WHERE name = 'Testing Storyline'),
     'requires_complete', 'COMPLETE es-gamma'),
    ('es-delta', 'ES: Delta',
     'content/missions/es-delta/brief.md', 'content/missions/es-delta/debrief.md',
     (SELECT id FROM groups WHERE name = 'Testing Storyline'),
     'requires_complete', 'COMPLETE es-delta');

INSERT INTO mission_unlock_codes (mission_id, unlock_code)
SELECT id, 'EXAMPLE UNLOCK' FROM missions WHERE slug IN ('es-alpha', 'es-beta');

INSERT INTO mission_unlock_codes (mission_id, unlock_code)
SELECT id, 'HIDDEN UNLOCK' FROM missions WHERE slug = 'es-hidden';

INSERT INTO mission_list_requires (mission_id, required_mission_id)
SELECT child.id, parent.id
FROM missions child
JOIN missions parent ON parent.slug = 'es-alpha'
WHERE child.slug = 'es-gamma';

INSERT INTO mission_list_requires (mission_id, required_mission_id)
SELECT child.id, parent.id
FROM missions child
JOIN missions parent ON parent.slug = 'es-beta'
WHERE child.slug = 'es-delta';

INSERT INTO mission_list_requires (mission_id, required_mission_id)
SELECT child.id, parent.id
FROM missions child
JOIN missions parent ON parent.slug = 'es-gamma'
WHERE child.slug = 'es-delta';

-- Diana: orientation only (no storyline unlocks).
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 4, id, 'active' FROM missions WHERE slug = 'basic-training';

-- Alice: EXAMPLE UNLOCK path — alpha complete, beta active, gamma active.
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 1, id, 'completed' FROM missions WHERE slug = 'basic-training';
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 1, id, 'completed' FROM missions WHERE slug = 'es-alpha';
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 1, id, 'active' FROM missions WHERE slug = 'es-beta';
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 1, id, 'active' FROM missions WHERE slug = 'es-gamma';

-- Charlie: beta complete, alpha still active (gamma and delta not listable).
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 3, id, 'completed' FROM missions WHERE slug = 'basic-training';
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 3, id, 'active' FROM missions WHERE slug = 'es-alpha';
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 3, id, 'completed' FROM missions WHERE slug = 'es-beta';

-- Bob: all storyline missions completed (including hidden dead-end).
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 2, id, 'completed' FROM missions WHERE slug = 'basic-training';
INSERT INTO agent_mission_status (user_id, mission_id, status)
SELECT 2, id, 'completed' FROM missions WHERE slug IN (
    'es-alpha', 'es-beta', 'es-hidden', 'es-gamma', 'es-delta'
);

COMMIT;
