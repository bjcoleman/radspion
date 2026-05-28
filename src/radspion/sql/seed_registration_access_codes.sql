-- Registration access codes (signup gate). Replace placeholders before production.
-- Prerequisite: src/radspion/sql/schema.sql
--
-- Three independent codes (rotate one without changing the others):
--   CS majors at large (subtle recruitment)
--   DevOps class (direct distribution)
--   External invite (non-Moravian Google accounts allowed after code + OAuth)

PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO registration_access_codes (code) VALUES
    ('CHANGE-ME-cs-general'),
    ('CHANGE-ME-devops-220'),
    ('CHANGE-ME-invite-external');

COMMIT;
