-- Example class seed: 220.2 DevOps + sample Orientation mission (global-hidden).
-- Requires schema.sql and seed_orientation.sql (basic-training) loaded first.
-- See docs/design/04-example-data-walkthrough.md

PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO groups (id, name) VALUES
    (2, '220.2 DevOps');

INSERT INTO users (id, email, google_subject_id, display_name) VALUES
    (1, 'alice@moravian.edu', 'google-alice', 'Alice'),
    (2, 'bob@moravian.edu', 'google-bob', 'Bob'),
    (3, 'charlie@moravian.edu', 'google-charlie', 'Charlie'),
    (4, 'diana@moravian.edu', 'google-diana', 'Diana');

INSERT INTO group_members (group_id, user_id) VALUES
    (1, 1), (1, 2), (1, 3), (1, 4),
    (2, 1), (2, 2), (2, 3);

INSERT INTO missions (id, slug, title, brief_path, debrief_path, group_id, access_rule, completion_code) VALUES
    (2, 'global-hidden', 'Training: Confidential Briefing',
     'content/missions/global-hidden/brief.md', 'content/missions/global-hidden/debrief.md',
     1, 'unlock_code', 'CONFIDENTIAL-BRIEF-OK'),
    (3, 'read-the-manual', 'Training: Read the Manual',
     'content/missions/read-the-manual/brief.md', 'content/missions/read-the-manual/debrief.md',
     2, 'open', 'READ-MANUAL-OK'),
    (4, 'learn-the-system', 'Training: Learn the System',
     'content/missions/learn-the-system/brief.md', 'content/missions/learn-the-system/debrief.md',
     2, 'open', 'LEARN-SYSTEM-OK'),
    (5, 'remote-access', 'Training: Remote Access',
     'content/missions/remote-access/brief.md', 'content/missions/remote-access/debrief.md',
     2, 'requires_complete', '-----BEGIN OPENSSH PRIVATE KEY-----\nEXAMPLE\n-----END OPENSSH PRIVATE KEY-----'),
    (6, 'identify-the-traitor', 'Training: Identify the Traitor',
     'content/missions/identify-the-traitor/brief.md', 'content/missions/identify-the-traitor/debrief.md',
     2, 'requires_complete', 'TRAITOR-IDENTIFIED-OK');

INSERT INTO mission_unlock_codes (mission_id, unlock_code) VALUES
    (2, 'UNLOCK-BLINDFOLD');

-- remote-access listed after learn-the-system; identify-the-traitor after read-the-manual AND remote-access
INSERT INTO mission_list_requires (mission_id, required_mission_id) VALUES
    (5, 4),
    (6, 3),
    (6, 5);

-- remote-access: complete only after read-the-manual (Charlie stealth path).
-- identify-the-traitor: list prereqs only (agents cannot see it until both targets are completed).
INSERT INTO mission_complete_requires (mission_id, required_mission_id) VALUES
    (5, 3);

INSERT INTO agent_mission_status (user_id, mission_id, status) VALUES
    (1, 1, 'completed'),
    (2, 1, 'completed'),
    (3, 1, 'active'),
    (4, 1, 'active'),
    (2, 2, 'completed'),
    (1, 3, 'completed'),
    (1, 4, 'completed'),
    (1, 5, 'active'),
    (2, 3, 'completed'),
    (2, 4, 'completed'),
    (2, 5, 'completed'),
    (2, 6, 'completed'),
    (3, 3, 'active'),
    (3, 4, 'completed'),
    (3, 5, 'active');

COMMIT;
